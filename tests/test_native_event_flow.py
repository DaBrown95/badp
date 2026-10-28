"""Synthetic checks for bounded native-event context expansion."""
import unittest

from tools.native_event_flow import inventory_events


def fixture():
    bank0, bank1 = bytearray(0x8000), bytearray(0x8000)
    lengths = bytearray([1] * 0xc5)
    lengths[0x00] = lengths[0x30] = lengths[0x1e] = 2
    # An initial script installs the $0212 record's script.
    bank1[0x100:0x102] = bytes([0, 18])
    bank1[0x212:0x21b] = bytes([0xff, 0xff, 0x20, 0x01, 0, 0, 0, 0, 0])
    # That later script can enable a contact event; its record installs $0130.
    bank1[0x120:0x124] = bytes([0x30, 1, 0x1e, 0])
    bank1[0x209:0x212] = bytes([0xff, 0xff, 0x30, 0x01, 0, 0, 0, 0, 0])
    # The contact script can enable a position event, installing $0140.
    bank1[0x130:0x134] = bytes([0x30, 4, 0x1e, 0])
    bank1[0x21b:0x224] = bytes([0xff, 0xff, 0x40, 0x01, 0, 0, 0, 0, 0])
    bank1[0x140:0x142] = bytes([0x1e, 0])
    records = [{'status': 'inspected', 'script_status': 'candidate',
                'encoded_script_pointer': '0x0100', 'descriptor_indices': [1],
                'location': {'bank': 1, 'bank_offset': 0x200}}]
    return bank0, bank1, lengths, records


class NativeEventFlowTests(unittest.TestCase):
    def test_expands_later_script_contact_and_position_to_fixed_point(self):
        b0, b1, lengths, records = fixture()
        result = inventory_events(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(result['rounds'], 3)
        refs = {r['command']: r for r in result['event_records']}
        self.assertEqual(set(refs), {'native_contact', 'native_position'})
        self.assertEqual(refs['native_contact']['encoded_pointer'], '0x0209')
        self.assertEqual(refs['native_position']['encoded_pointer'], '0x021b')
        self.assertEqual(refs['native_contact']['support'][0]['entry'], '0x0120')
        self.assertEqual(refs['native_position']['support'][0]['entry'], '0x0130')
        self.assertEqual({c['entry'] for c in result['flow']['contexts']},
                         {'0x0100', '0x0120', '0x0130', '0x0140'})

    def test_sentinel_stops_installation_but_retains_candidate_record(self):
        b0, b1, lengths, records = fixture()
        b1[0x20c] = 0xff
        result = inventory_events(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual([r['command'] for r in result['event_records']], ['native_contact'])
        self.assertEqual(result['rounds'], 1)

    def test_iteration_limit_fails_instead_of_claiming_completion(self):
        b0, b1, lengths, records = fixture()
        with self.assertRaisesRegex(ValueError, 'fixed point'):
            inventory_events(bytes(b0), bytes(b1), bytes(lengths), records, max_rounds=1)
        with self.assertRaisesRegex(ValueError, 'invalid native event'):
            inventory_events(bytes(b0), bytes(b1), bytes(lengths), records, limit=0)

    def test_cross_bank_event_record_is_reported_without_a_script_seed(self):
        b0, b1, lengths, records = fixture()
        records[0]['encoded_script_pointer'] = '0x0120'
        records[0]['location']['bank_offset'] = 0x7ff0
        result = inventory_events(bytes(b0), bytes(b1), bytes(lengths), records)
        self.assertEqual(len(result['event_records']), 1)
        self.assertEqual(result['event_records'][0]['status'], 'fetch_crosses_bank_boundary')
        self.assertEqual([c['entry'] for c in result['flow']['contexts']], ['0x0120'])


if __name__ == '__main__':
    unittest.main()
