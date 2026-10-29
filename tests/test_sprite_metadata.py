import unittest
from tools.sprite_metadata import (decode_frame_header, decode_resource_header, inventory_observed,
                                   inventory_candidates, resource_pointer_candidates)


class SpriteMetadataTests(unittest.TestCase):
    def test_separate_dimensions_keep_full_bytes_and_payload_offset(self):
        frame = decode_frame_header(bytes([0x82, 17, 3]), header_format='separate-bytes')
        self.assertEqual((frame['oam_base_index'], frame['large_sprites']), (2, True))
        self.assertEqual((frame['columns'], frame['rows'], frame['tile_pairs']), (17, 3, 51))
        self.assertEqual(frame['tile_read_offsets'], list(range(3, 105)))
        self.assertFalse(frame['index_wraps'])
        with self.assertRaises(ValueError):
            decode_frame_header(bytes([0, 1]), header_format='separate-bytes')
        with self.assertRaises(ValueError):
            decode_frame_header(bytes([0, 1, 1]), header_format='guessed')

    def test_separate_header_changes_the_last_nonwrapping_payload(self):
        last = decode_frame_header(bytes([0, 126, 1]), header_format='separate-bytes')
        wrapped = decode_frame_header(bytes([0, 127, 1]), header_format='separate-bytes')
        self.assertFalse(last['index_wraps'])
        self.assertTrue(wrapped['index_wraps'])
        self.assertEqual(last['tile_read_offsets'], list(range(3, 255)))
        self.assertIn(0, wrapped['tile_read_offsets'])
        zero = decode_frame_header(bytes([0, 1, 0]), header_format='separate-bytes')
        self.assertEqual(zero['effective_rows'], 256)
        self.assertTrue(zero['index_wraps'])

    def test_direct_frame_and_offset_order(self):
        result = decode_resource_header(bytes([0x82, 0x23]))
        self.assertEqual(result['kind'], 'direct')
        frame = result['frame']
        self.assertTrue(frame['large_sprites'])
        self.assertEqual((frame['columns'], frame['rows'], frame['tile_pairs']), (2, 3, 6))
        self.assertEqual(frame['tile_read_offsets'], list(range(2, 14)))
        self.assertFalse(frame['index_wraps'])

    def test_animation_header_and_empty_marker(self):
        self.assertEqual(decode_resource_header(bytes([0x4F])), {'kind': 'empty'})
        self.assertEqual(decode_resource_header(bytes([0x53, 3, 4, 0x34, 0x12])),
                         {'kind': 'animated', 'frame_count': 3, 'delay': 4,
                          'first_frame_pointer': 0x1234})

    def test_index_wraps_and_zero_dimensions_follow_eight_bit_loops(self):
        wrapped = decode_frame_header(bytes([0, 0xF9]))
        self.assertEqual(wrapped['tile_pairs'], 135)
        self.assertTrue(wrapped['index_wraps'])
        self.assertEqual(wrapped['tile_read_offsets'], list(range(256)))
        zero = decode_frame_header(bytes([0, 0x10]))
        self.assertEqual((zero['effective_columns'], zero['effective_rows']), (1, 256))
        self.assertEqual(zero['tile_pairs'], 256)
        self.assertTrue(zero['index_wraps'])

    def test_truncated_headers_are_rejected(self):
        for data in (b'', bytes([1]), bytes([0x53, 1, 2, 3])):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_resource_header(data)
        with self.assertRaises(ValueError):
            decode_frame_header(b'\x00')


class SpriteInventoryTests(unittest.TestCase):
    def setUp(self):
        self.bank0 = bytearray(0x8000)
        self.bank0[8:13] = bytes([0x53, 2, 4, 0x34, 0x12])
        self.bank0[20:22] = bytes([0x82, 0x25])
        self.bank1 = bytes(0x8000)

    def test_validated_samples_and_counts(self):
        trace = {'results': {'test': {'reads': {'header': {'0008:5302': 2},
                                                  'frame': {'0014:8225': 3}},
                                      'totals': {'header': [2, 0], 'frame': [3, 0]}}}}
        result = inventory_observed(trace, bytes(self.bank0), self.bank1)
        self.assertEqual(result['header'][0]['decoded']['kind'], 'animated')
        self.assertEqual(result['header'][0]['decoded']['first_frame_pointer'], 0x1234)
        self.assertEqual(result['frame'][0]['decoded']['tile_pairs'], 10)
        self.assertEqual(result['frame'][0]['scenarios'], {'test': 3})
        self.assertTrue(result['frame'][0]['tile_reads_within_bank'])

    def test_wrong_samples_and_totals_fail_closed(self):
        for reads, totals in (({'0008:5303': 1}, [1, 0]),
                              ({'0008:5302': 1}, [2, 0]),
                              ({'7FFF:0000': 1}, [1, 0])):
            trace = {'results': {'test': {'reads': {'header': reads, 'frame': {}},
                                          'totals': {'header': totals, 'frame': [0, 0]}}}}
            with self.subTest(reads=reads), self.assertRaises(ValueError):
                inventory_observed(trace, bytes(self.bank0), self.bank1)


class SpriteCandidateTests(unittest.TestCase):
    def test_candidate_record_pointers_respect_sentinels_and_cpu_address_space(self):
        def fields(pointer, present=True):
            return {'sprite_pointer': pointer, 'sprite_fields_present': present}
        descriptors = [{'status': 'inspected', 'decoded_fields': fields(0x8100)},
                       {'status': 'inspected', 'decoded_fields': fields(0xffff, False)},
                       {'status': 'crosses_bank_boundary'}]
        references = [{'status': 'candidate', 'fields': fields(0x8100)},
                      {'status': 'candidate', 'fields': fields(0x0042)},
                      {'status': 'candidate', 'fields': fields(0xff01)},
                      {'status': 'fetch_crosses_bank_boundary'}]
        found = resource_pointer_candidates(descriptors, references)
        self.assertEqual(found, {'rom_pointers': [0x8100], 'non_rom_pointers': [0x42],
                                 'sentinel_pointers': [0xff01]})
        with self.assertRaises(ValueError):
            resource_pointer_candidates([], [{'status': 'candidate', 'fields': fields(True)}])

    def test_direct_and_animated_frames_deduplicate_physical_aliases(self):
        bank = bytearray(0x8000)
        bank[0x100:0x107] = bytes([0x53, 2, 4, 0, 0x82, 0x10, 0x82])
        bank[0x200:0x204] = bytes([0, 0x11, 7, 8])
        bank[0x210:0x216] = bytes([0, 0x21, 1, 2, 3, 4])
        result = inventory_candidates(bytes(bank), [0x8100, 0x8200, 0x8100])
        self.assertEqual(len(result['resources']), 2)
        self.assertEqual(len(result['frames']), 2)
        self.assertFalse(result['crossings'])
        self.assertFalse(result['non_rom_frames'])
        covered = {i for start, length in result['spans'] for i in range(start, start + length)}
        self.assertEqual(covered, set(range(0x100, 0x107)) | set(range(0x200, 0x204))
                         | set(range(0x210, 0x216)))

    def test_empty_marker_keeps_the_slot_loader_dimension_read(self):
        bank = bytearray(0x8000)
        bank[0x300:0x302] = bytes([0x4f, 0x21])
        result = inventory_candidates(bytes(bank), [0x8300])
        self.assertEqual(result['resources'][0]['kind'], 'empty')
        self.assertEqual(result['spans'], [(0x300, 2)])
        self.assertEqual(result['frames'], [])

    def test_out_of_bank_frame_header_and_tile_reads_are_reported(self):
        bank = bytearray(0x8000)
        bank[0x100:0x107] = bytes([0x53, 2, 4, 0xff, 0xff, 0xfe, 0xff])
        bank[-2:] = bytes([0, 0x11])
        result = inventory_candidates(bytes(bank), [0x8100])
        self.assertIn({'kind': 'frame_header', 'cpu_address': 0xffff}, result['crossings'])
        self.assertTrue(any(item['kind'] == 'frame_tile' and item['cpu_address'] == 0xfffe
                            for item in result['crossings']))
        self.assertTrue(all(start + length <= 0x8000 for start, length in result['spans']))

    def test_zero_count_wrap_and_boundary_failures_are_visible(self):
        bank = bytearray(0x8000)
        bank[0x100:0x103] = bytes([0x53, 0, 1])
        for i in range(256):
            bank[0x103 + 2*i:0x105 + 2*i] = bytes([0, 0x84])
        bank[0x400:0x404] = bytes([0, 0x11, 1, 2])
        bank[0x7efe:0x7f01] = bytes([0x53, 255, 1])
        result = inventory_candidates(bytes(bank), [0x8100, 0xfefe])
        self.assertEqual(result['resources'][0]['candidate_frames'], 256)
        self.assertIn({'kind': 'frame_pointer_table', 'cpu_address': 0xfefe}, result['crossings'])
        self.assertIn(0, result['non_rom_frames'])
        with self.assertRaises(ValueError):
            inventory_candidates(bytes(bank), [0x7fff])


if __name__ == '__main__':
    unittest.main()
