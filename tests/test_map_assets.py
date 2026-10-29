"""Local map-asset round trips and rejection tests using synthetic bytes."""
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import map_assets, packed_text


def synthetic_prg():
    prg = bytearray(2 * map_assets.BANK_SIZE)
    indices = [index for index in range(map_assets.SLOT_COUNT) if index != 22] + [0]
    for i, index in enumerate(indices):
        offset = index * map_assets.CHUNK_SIZE
        start = map_assets.CHUNK_TABLE_OFFSET + i * 2
        prg[start:start + 2] = offset.to_bytes(2, 'little')
    for index in range(map_assets.REGION_SIZE):
        prg[map_assets.BANK_SIZE + index] = (index * 13 + 5) & 255
    a = map_assets.BANK_SIZE + map_assets.DUPLICATE_SLOT * map_assets.CHUNK_SIZE
    b = map_assets.BANK_SIZE + map_assets.DUPLICATE_OF * map_assets.CHUNK_SIZE
    prg[a:a + map_assets.CHUNK_SIZE] = prg[b:b + map_assets.CHUNK_SIZE]
    # Fourteen synthetic 3x3 layouts in bank 1; the 22-state table repeats
    # eight of them. They do not overlap the candidate chunk region.
    for index in range(14):
        offset = 0x2800 + index * 11
        base = map_assets.BANK_SIZE + offset
        prg[base:base + 11] = bytes([3, 3] + [(index + cell) % 145 for cell in range(9)])
    for state in range(22):
        offset = 0x2800 + (state % 14) * 11
        base = 0x21b2 + state * 2
        prg[base:base + 2] = offset.to_bytes(2, 'little')
    # Synthetic text tables and 52 fixed-size records; no game text is used.
    bank = map_assets.BANK_SIZE
    prg[bank + packed_text.PRIMARY_OFFSET:bank + packed_text.PRIMARY_OFFSET + 32] = bytes(range(0x41, 0x61))
    prg[bank + packed_text.SECONDARY_OFFSET:bank + packed_text.SECONDARY_OFFSET + 32] = bytes(range(0x21, 0x41))
    position = 0x403e
    for index in range(52):
        payload_size = 74 if index < 51 else 99
        symbols = next(n for n in range(1, 400) if (n * 5 + 7) // 8 == payload_size)
        record = {'header': [0, 0], 'tokens': [{'kind': 'primary', 'index': 1}] * (symbols - 1),
                  'padding_bits': (-5 * symbols) % 8, 'padding_value': 0}
        encoded = packed_text.encode_record(record)
        pointer = packed_text.TABLE_OFFSET + index * 2
        prg[bank + pointer:bank + pointer + 2] = (0x8000 + position).to_bytes(2, 'little')
        prg[bank + position:bank + position + len(encoded)] = encoded
        position += len(encoded)
    assert position == packed_text.DATA_END
    return bytes(prg)


class MapAssetTests(unittest.TestCase):
    def test_release_geometry_changes_slot_count_and_duplicate_relation(self):
        geometry = {'chunk_index_count': 144, 'slot_count': 144, 'duplicate_of': 135}
        prg = bytearray(2 * map_assets.BANK_SIZE)
        indices = [index for index in range(144) if index != 22] + [0]
        for i, slot in enumerate(indices):
            prg[0x200 + i * 2:0x202 + i * 2] = (slot * 68).to_bytes(2, 'little')
        for slot in range(144):
            start = map_assets.BANK_SIZE + slot * 68
            prg[start:start + 68] = bytes((slot * 17 + n) & 255 for n in range(68))
        start, other = map_assets.BANK_SIZE + 22 * 68, map_assets.BANK_SIZE + 135 * 68
        prg[start:start + 68] = prg[other:other + 68]
        prg = bytes(prg)
        options = {'chunk_table_offset': 0x200, 'geometry': geometry}
        asset = map_assets.capture(prg, self.reference, **options)
        self.assertEqual(len(asset['slots']), 144)
        self.assertEqual(asset['slots'][22]['reference_duplicate_of'], 135)
        baseline = map_assets.encode(asset, prg, self.reference, **options)
        self.assertEqual(baseline, prg[map_assets.BANK_SIZE:map_assets.BANK_SIZE + 144 * 68])
        changed = map_assets.changed_asset(asset, geometry=geometry)
        payload = map_assets.encode(changed, prg, self.reference, **options)
        reference = b'R' * 16 + prg
        candidate = bytearray(reference)
        candidate[16 + map_assets.BANK_SIZE:16 + map_assets.BANK_SIZE + len(payload)] = payload
        offsets = map_assets.verify_control(reference, bytes(candidate), 16, geometry=geometry)
        self.assertEqual(offsets, [16 + map_assets.BANK_SIZE + i for i in (0, 22 * 68 + 1, 135 * 68 + 2)])
        with self.assertRaises(ValueError):
            map_assets.capture(prg, self.reference, chunk_table_offset=0x200)
        with self.assertRaisesRegex(ValueError, 'no longer duplicates'):
            map_assets.capture(prg, self.reference, chunk_table_offset=0x200,
                               geometry=dict(geometry, duplicate_of=134))
        for invalid in (dict(geometry, slot_count=22), dict(geometry, chunk_index_count=True),
                        dict(geometry, duplicate_of=22)):
            with self.subTest(geometry=invalid), self.assertRaises(ValueError):
                map_assets.capture(prg, self.reference, chunk_table_offset=0x200, geometry=invalid)

    def setUp(self):
        self.prg = synthetic_prg()
        self.reference = 'a' * 64
        self.asset = map_assets.capture(self.prg, self.reference)

    def test_all_slots_round_trip_and_duplicate_has_explicit_metadata(self):
        encoded = map_assets.encode(self.asset, self.prg, self.reference)
        self.assertEqual(encoded, self.prg[map_assets.BANK_SIZE:map_assets.BANK_SIZE + map_assets.REGION_SIZE])
        self.assertEqual(sum(x['kind'] == 'chunk' for x in self.asset['slots']), 145)
        self.assertEqual(self.asset['slots'][22]['kind'], 'unreferenced_duplicate_chunk')
        self.assertEqual(self.asset['slots'][22]['reference_duplicate_of'], 134)
        self.assertEqual(len(self.asset['slots'][0]['tile_rows']), 8)
        self.assertEqual(len(self.asset['slots'][0]['attribute_rows']), 2)

    def test_changed_tile_is_explicit_and_does_not_mutate_original(self):
        changed = map_assets.changed_asset(self.asset)
        baseline = map_assets.encode(self.asset, self.prg, self.reference)
        encoded = map_assets.encode(changed, self.prg, self.reference)
        self.assertEqual([i for i, (a, b) in enumerate(zip(baseline, encoded)) if a != b], [0, 22 * 68 + 1, 134 * 68 + 2])
        self.assertNotEqual(changed['slots'][0]['tile_rows'][0][0], self.asset['slots'][0]['tile_rows'][0][0])

    def test_wrong_identity_geometry_and_duplicate_metadata_fail(self):
        for change in ('identity', 'order', 'shape', 'metadata', 'old_schema', 'boolean', 'kind'):
            asset = copy.deepcopy(self.asset)
            if change == 'identity':
                asset['reference_sha256'] = 'b' * 64
            elif change == 'order':
                asset['slots'][0], asset['slots'][1] = asset['slots'][1], asset['slots'][0]
            elif change == 'shape':
                asset['slots'][0]['tile_rows'][0].pop()
            elif change == 'metadata':
                asset['slots'][22]['reference_duplicate_of'] = 0
            elif change == 'old_schema':
                asset['schema_version'] = 1
            elif change == 'boolean':
                asset['slots'][22]['reference_duplicate_of'] = True
            else:
                asset['slots'][22]['kind'] = 'chunk'
            with self.subTest(change=change), self.assertRaises(ValueError):
                map_assets.encode(asset, self.prg, self.reference)

    def test_duplicate_and_original_are_independently_editable(self):
        baseline = map_assets.encode(self.asset, self.prg, self.reference)
        for index in (22, 134):
            changed = copy.deepcopy(self.asset)
            changed['slots'][index]['tile_rows'][3][4] ^= 1
            candidate = map_assets.encode(changed, self.prg, self.reference)
            self.assertEqual([i for i, (a, b) in enumerate(zip(baseline, candidate)) if a != b],
                             [index * 68 + 3 * 8 + 4])

    def test_duplicate_reference_relation_must_be_verified(self):
        bad = bytearray(self.prg)
        bad[map_assets.BANK_SIZE + 22 * 68] ^= 1
        for operation in (lambda: map_assets.capture(bytes(bad), self.reference),
                          lambda: map_assets.encode(self.asset, bytes(bad), self.reference)):
            with self.assertRaisesRegex(ValueError, 'no longer duplicates'):
                operation()

    def test_invalid_table_and_extra_slot_use_are_rejected(self):
        bad = bytearray(self.prg)
        bad[map_assets.CHUNK_TABLE_OFFSET:map_assets.CHUNK_TABLE_OFFSET + 2] = (1).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'unaligned'):
            map_assets.capture(bytes(bad), self.reference)
        bad = bytearray(self.prg)
        bad[map_assets.CHUNK_TABLE_OFFSET:map_assets.CHUNK_TABLE_OFFSET + 2] = (22 * map_assets.CHUNK_SIZE).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'reviewed slot'):
            map_assets.capture(bytes(bad), self.reference)

    def test_local_selection_and_changed_input_are_visible(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asset, payload, source, _ = map_assets.select(root, self.prg, self.reference)
            self.assertEqual(source, 'reference')
            path = root / map_assets.ASSET_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes(map_assets.serialize(map_assets.changed_asset(asset)))
            _, changed, source, _ = map_assets.select(root, self.prg, self.reference)
            self.assertEqual(source, 'local')
            self.assertNotEqual(changed, payload)

    def test_export_is_idempotent_and_preserves_existing_edits(self):
        target = {'reference': {'file': {'sha256': self.reference}}}
        banks = (target, self.prg[:map_assets.BANK_SIZE], self.prg[map_assets.BANK_SIZE:], b'')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / map_assets.ASSET_PATH
            with (patch.object(map_assets, 'ROOT', root),
                  patch.object(map_assets, 'load_audited_banks', return_value=banks),
                  contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO())):
                self.assertEqual(map_assets.main(), 0)
                first = path.read_bytes()
                self.assertEqual(map_assets.main(), 0)
                self.assertEqual(path.read_bytes(), first)
                user_edit = b'{"user_edit":true}\n'
                path.write_bytes(user_edit)
                self.assertEqual(map_assets.main(), 1)
                self.assertEqual(path.read_bytes(), user_edit)

    def test_control_requires_all_three_independent_selected_changes(self):
        reference = bytes(16) + self.prg + bytes(65536)
        candidate = bytearray(reference)
        positions = [16 + map_assets.BANK_SIZE + i * 68 + r * 8 + c
                     for i, r, c in map_assets.CONTROL_TILES]
        for position in positions:
            candidate[position] ^= 1
        self.assertEqual(map_assets.verify_control(reference, bytes(candidate), 16), positions)
        # Omitting either duplicate/original edit, or coupling the edits at
        # identical tile positions, cannot pass the retained build control.
        for position in positions:
            bad = candidate.copy()
            bad[position] ^= 1
            with self.assertRaisesRegex(ValueError, 'exactly'):
                map_assets.verify_control(reference, bytes(bad), 16)
        candidate[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'exactly'):
            map_assets.verify_control(reference, bytes(candidate), 16)


if __name__ == '__main__':
    unittest.main()
