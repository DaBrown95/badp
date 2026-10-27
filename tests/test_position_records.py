"""Position-record decoding is tested solely with synthetic byte fixtures."""
import unittest

from tools.position_records import TERMINATOR, decode_stream, decode_tables, encode_stream


def record(key, flag=False, kind=0, parameters=None):
    return {"key": key, "range_flag": flag, "type": kind,
            "parameters": parameters if parameters is not None else [1, 2, 3, 4, 5]}


class PositionRecordsTests(unittest.TestCase):
    def test_round_trip_preserves_flag_and_parameters(self):
        records = [record(0), record(0x1234, True, 0xF0, [0, 255, 3, 4, 5])]
        data = encode_stream(records)
        self.assertEqual(len(data), 20)
        self.assertEqual(data[-4:], TERMINATOR)
        self.assertEqual(decode_stream(data), records)

    def test_rejects_malformed_length_and_terminator(self):
        for data in (b"", b"\xff\xff", b"\xff\xff\x00\x01",
                     b"\x00" + TERMINATOR, b"\xff\xff" + bytes(6) + TERMINATOR):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_stream(data)

    def test_rejects_unordered_keys_and_invalid_fields(self):
        for records in ([record(2), record(1)], [record(0x7FFF, True)],
                        [record(0, flag=1)], [record(0, kind=256)],
                        [record(0, parameters=[1, 2])]):
            with self.subTest(records=records), self.assertRaises(ValueError):
                encode_stream(records)
        malformed = encode_stream([record(1), record(2)])
        malformed = malformed[8:16] + malformed[:8] + TERMINATOR
        with self.assertRaisesRegex(ValueError, "sorted"):
            decode_stream(malformed)

    def test_tables_deduplicate_aliases_and_bound_last_stream(self):
        a = encode_stream([record(0), record(2, True, 3)])
        b = encode_stream([record(1, kind=9)])
        bank = bytearray(160)
        start = 32
        bank[start:start + len(a)] = a
        second = start + len(a)
        bank[second:second + len(b)] = b
        for off, value in ((0, start), (2, second), (4, second), (6, start)):
            bank[off:off + 2] = value.to_bytes(2, "little")
        decoded = decode_tables(bytes(bank), 0, 4, 2, start, 120)
        self.assertEqual(decoded["tables"], [[start, second], [second, start]])
        self.assertEqual([s["start"] for s in decoded["streams"]], [start, second])
        self.assertEqual([s["end"] for s in decoded["streams"]], [second, second + len(b)])
        self.assertEqual(decoded["streams"][0]["records"], [record(0), record(2, True, 3)])

    def test_rejects_unbounded_or_mispointed_streams(self):
        bank = bytearray(96)
        bank[:2] = (32).to_bytes(2, "little")
        bank[2:4] = (40).to_bytes(2, "little")
        bank[32:40] = bytes(8)
        bank[40:48] = bytes(8)
        with self.assertRaisesRegex(ValueError, "terminator"):
            decode_tables(bytes(bank), 0, 2, 1, 32, 80)
        bank[2:4] = (95).to_bytes(2, "little")
        with self.assertRaisesRegex(ValueError, "outside"):
            decode_tables(bytes(bank), 0, 2, 1, 32, 80)

    def test_pointer_address_base(self):
        bank = bytearray(80)
        bank[:2] = (0x8020).to_bytes(2, "little")
        bank[2:4] = (0x8020).to_bytes(2, "little")
        bank[32:36] = TERMINATOR
        result = decode_tables(bytes(bank), 0, 2, 1, 32, 64, 0x8000)
        self.assertEqual(result["tables"], [[32], [32]])
        self.assertEqual(result["streams"][0]["records"], [])


if __name__ == "__main__":
    unittest.main()
