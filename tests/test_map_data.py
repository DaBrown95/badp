"""Map format tests use synthetic data only."""
import unittest
from tools.map_data import (CHUNK_SIZE, CHUNK_TABLE_OFFSET, STATE_TABLE_OFFSET,
                            decode_chunk, decode_layout, encode_chunk, encode_layout,
                            inventory, map_script_overlaps)
from tools.script_entries import BANK_SIZE


class ChunkTests(unittest.TestCase):
    def test_chunk_round_trip_and_row_layout(self):
        raw = bytes(range(CHUNK_SIZE))
        chunk = decode_chunk(raw)
        self.assertEqual(chunk['tile_rows'][1], list(range(8, 16)))
        self.assertEqual(chunk['attribute_rows'], [[64, 65], [66, 67]])
        self.assertEqual(encode_chunk(chunk), raw)

    def test_rejects_truncated_and_invalid_chunks(self):
        with self.assertRaises(ValueError):
            decode_chunk(bytes(67))
        chunk = decode_chunk(bytes(CHUNK_SIZE))
        chunk['tile_rows'][0][0] = 256
        with self.assertRaises(ValueError):
            encode_chunk(chunk)


class LayoutTests(unittest.TestCase):
    def test_round_trip_and_bounds(self):
        bank = bytearray(BANK_SIZE)
        bank[0x100:0x108] = bytes([3, 2, 0, 1, 2, 3, 4, 5])
        layout = decode_layout(bytes(bank), 0x100, 6)
        self.assertEqual(layout['chunk_rows'], [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(encode_layout(layout), bytes(bank[0x100:0x108]))
        self.assertEqual(layout['width_tiles'], 24)
        self.assertEqual(layout['height_tiles_low'], 16)
        self.assertEqual(layout['horizontal_bound_pixels'], 0xffc0)
        self.assertEqual(layout['vertical_bound_pixels'], 0)
        self.assertEqual(layout['initial_draw_columns'], 24)

    def test_zero_width_and_height_overflow_preserve_original_arithmetic(self):
        bank = bytearray(BANK_SIZE)
        bank[0:2] = bytes([0, 33])
        layout = decode_layout(bytes(bank), 0, 1)
        self.assertEqual(layout['initial_draw_columns'], 256)
        self.assertEqual(layout['height_tiles_low'], 8)
        self.assertEqual(layout['horizontal_bound_pixels'], 0xff00)
        self.assertEqual(encode_layout(layout), b'\x00\x21')

    def test_last_lookup_lookahead_and_out_of_range_index_are_explicit(self):
        bank = bytearray(BANK_SIZE)
        bank[-3:] = bytes([1, 1, 255])
        layout = decode_layout(bytes(bank), BANK_SIZE - 3, 2)
        self.assertTrue(layout['last_lookup_crosses_bank'])
        self.assertEqual(layout['out_of_table_indices'], [255])
        with self.assertRaises(ValueError):
            decode_layout(bytes(bank), BANK_SIZE - 2, 2)

    def test_rejects_unbounded_layout_and_bad_shape(self):
        bank = bytearray(BANK_SIZE)
        bank[-2:] = bytes([2, 2])
        with self.assertRaises(ValueError):
            decode_layout(bytes(bank), BANK_SIZE - 2, 2)
        with self.assertRaises(ValueError):
            encode_layout({'width_chunks': 2, 'height_chunks': 1, 'chunk_rows': [[1]]})


class MapInventoryTests(unittest.TestCase):
    def test_aliases_and_component_round_trips(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytearray(BANK_SIZE)
        for i in range(22):
            bank0[STATE_TABLE_OFFSET + 2*i:STATE_TABLE_OFFSET + 2*i + 2] = bytes([0, 0xa5])
        bank0[0x2500:0x2504] = bytes([2, 1, 0, 1])
        result = inventory(bytes(bank0), bytes(bank1))
        self.assertEqual(len(result['states']), 22)
        self.assertEqual(len(result['layouts']), 1)
        self.assertEqual(result['layouts'][0]['state_indices'], list(range(22)))
        self.assertEqual(len(result['chunks']), 1)
        self.assertEqual(result['chunks'][0]['table_indices'], list(range(146)))

    def test_aligned_unreferenced_slot_is_only_a_candidate(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytes(BANK_SIZE)
        for i in range(22):
            bank0[STATE_TABLE_OFFSET + 2*i:STATE_TABLE_OFFSET + 2*i + 2] = bytes([0, 0xa5])
        bank0[0x2500:0x2502] = bytes([0, 0])
        bank0[CHUNK_TABLE_OFFSET + 2:CHUNK_TABLE_OFFSET + 4] = (2 * CHUNK_SIZE).to_bytes(2, 'little')
        result = inventory(bytes(bank0), bank1)
        self.assertTrue(result['chunk_offsets_aligned'])
        self.assertEqual(len(result['chunks']), 2)
        slots = result['unreferenced_aligned_chunk_slots']
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0]['slot_index'], 1)
        self.assertEqual(slots[0]['location']['physical_prg_offset'], BANK_SIZE + CHUNK_SIZE)
        self.assertEqual(slots[0]['size'], CHUNK_SIZE)
        self.assertNotIn('decoded', slots[0])

    def test_distinct_overlapping_chunks_are_reported(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytes(BANK_SIZE)
        for i in range(22):
            bank0[STATE_TABLE_OFFSET + 2*i:STATE_TABLE_OFFSET + 2*i + 2] = bytes([0, 0xa5])
        bank0[0x2500:0x2502] = bytes([0, 0])
        bank0[CHUNK_TABLE_OFFSET + 2:CHUNK_TABLE_OFFSET + 4] = bytes([1, 0])
        result = inventory(bytes(bank0), bank1)
        self.assertEqual(len(result['chunks']), 2)
        self.assertEqual(result['overlapping_chunk_bytes'], 67)
        self.assertEqual(result['overlapping_layout_bytes'], 0)
        self.assertFalse(result['chunk_offsets_aligned'])
        self.assertEqual(result['unreferenced_aligned_chunk_slots'], [])

    def test_script_and_table_overlap_counts_unique_physical_bytes(self):
        maps = {'chunks': [{'location': {'physical_prg_offset': 0x8010}}],
                'layouts': [{'location': {'physical_prg_offset': 0x100},
                             'decoded': {'size': 4}}]}
        graph = {'nodes': [
            {'encoded_pointer': '0x0010', 'location': {'bank': 1, 'bank_offset': 0x10},
             'length': 2, 'lookup_records': [
                 {'location': {'bank': 0, 'bank_offset': 0x102}, 'size': 2}]},
            {'encoded_pointer': '0x0011', 'location': {'bank': 1, 'bank_offset': 0x11},
             'length': 2}]}
        result = map_script_overlaps(maps, graph)
        self.assertEqual(result['physical_bytes'], 5)
        self.assertEqual(len(result['nodes']), 2)

    def test_rejects_chunk_offset_crossing_bank(self):
        bank0, bank1 = bytearray(BANK_SIZE), bytes(BANK_SIZE)
        bank0[CHUNK_TABLE_OFFSET:CHUNK_TABLE_OFFSET + 2] = bytes([0xff, 0x7f])
        with self.assertRaises(ValueError):
            inventory(bytes(bank0), bank1)


if __name__ == '__main__':
    unittest.main()
