import unittest
from tools.sprite_metadata import decode_frame_header, decode_resource_header, inventory_observed


class SpriteMetadataTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
