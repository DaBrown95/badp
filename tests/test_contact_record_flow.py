"""Synthetic checks for candidate native contact-event record discovery."""
import unittest

from tools.contact_record_flow import contact_candidates


def fixture():
    bank0 = bytearray(0x8000)
    bank1 = bytearray(0x8000)
    lengths = bytearray([1] * 0xc5)
    lengths[0x30] = 2
    lengths[0x1e] = 2
    # Candidate initial script clears bit 0, then releases the slot.
    bank1[0x100:0x104] = bytes([0x30, 1, 0x1e, 0])
    # A possible contact record has a skipped resource and script at $0300.
    bank1[0x209:0x212] = bytes([0xff, 0xff, 0x00, 0x03, 0, 0, 0, 0, 0])
    records = [{'status': 'inspected', 'script_status': 'candidate',
                'encoded_script_pointer': '0x0100', 'descriptor_indices': [4],
                'location': {'bank': 1, 'bank_offset': 0x200}}]
    return bank0, bank1, lengths, records


class ContactRecordFlowTests(unittest.TestCase):
    def test_literal_flag_clear_finds_contact_record_and_script(self):
        b0, b1, lengths, records = fixture()
        result = contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(result['seeds'], [(0x200, 0x300)])
        ref = result['references'][0]
        self.assertEqual((ref['base'], ref['encoded_pointer'], ref['offset'], ref['mode']),
                         ('0x0200', '0x0209', 9, 0))
        self.assertEqual(ref['candidate_clear_sites'], ['0x0100'])
        self.assertEqual(ref['descriptor_indices'], [4])

    def test_clear_must_include_bit_zero_and_script_sentinel_stops_seed(self):
        b0, b1, lengths, records = fixture()
        b1[0x101] = 2
        self.assertEqual(contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)['references'], [])
        b1[0x101] = 1
        b1[0x20c] = 0xff
        result = contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(len(result['references']), 1)
        self.assertEqual(result['seeds'], [])

    def test_contact_fetch_crossing_bank_is_reported_not_followed(self):
        b0, b1, lengths, records = fixture()
        records[0]['location']['bank_offset'] = 0x7ff0
        result = contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(result['references'][0]['status'], 'fetch_crosses_bank_boundary')
        self.assertEqual(result['seeds'], [])

    def test_shared_script_keeps_each_descriptor_base(self):
        b0, b1, lengths, records = fixture()
        bank_record = dict(records[0], descriptor_indices=[5],
                           location={'bank': 1, 'bank_offset': 0x220})
        records.append(bank_record)
        b1[0x229:0x232] = bytes([0xff, 0xff, 0x20, 0x03, 0, 0, 0, 0, 0])
        result = contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(result['seeds'], [(0x200, 0x300), (0x220, 0x320)])
        self.assertEqual([ref['base'] for ref in result['references']], ['0x0200', '0x0220'])

    def test_uninspected_records_cannot_create_a_candidate(self):
        b0, b1, lengths, records = fixture()
        records[0]['status'] = 'fetch_crosses_bank_boundary'
        result = contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(result, {'references': [], 'seeds': []})

    def test_unreachable_clear_does_not_create_a_candidate(self):
        b0, b1, lengths, records = fixture()
        lengths[0x04] = 3
        b1[0x100:0x105] = bytes([0x04, 0x10, 0x01, 0x30, 1])
        b1[0x110:0x112] = bytes([0x1e, 0])
        result = contact_candidates(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(result, {'references': [], 'seeds': []})


if __name__ == '__main__':
    unittest.main()
