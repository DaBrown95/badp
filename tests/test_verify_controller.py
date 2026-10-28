"""Synthetic controller observation tests; no game data is required."""
import unittest
from tools.verify_controller import parse_output


class ControllerVerificationTests(unittest.TestCase):
    def valid(self):
        return ('HANDLER 1600 FBD8 80\nHANDLER 1620 FC03 40\nHANDLER 1620 FBD8 40\n'
                'HANDLER 1660 FC03 40\nHANDLER 1680 FC03 80\nHANDLER 1680 FBD8 80\n'
                'BUTTON 0 80\nBUTTON 1 40\nBUTTON 2 20\nBUTTON 3 10\n'
                'BUTTON 4 08\nBUTTON 5 04\nBUTTON 6 02\nBUTTON 7 01\n'
                'CONTROLLER_DONE 2200\n')

    def test_known_button_order_and_release_dispatch(self):
        result = parse_output(self.valid())
        self.assertEqual(result['button_masks'], [128, 64, 32, 16, 8, 4, 2, 1])
        self.assertEqual(len(result['handler_events']), 6)

    def test_changed_or_incomplete_observations_fail(self):
        good = self.valid()
        for bad in (good.replace('BUTTON 7 01\n', ''), good.replace('BUTTON 0 80', 'BUTTON 0 40'),
                    good.replace('HANDLER 1620 FBD8 40\n', ''),
                    good.replace('HANDLER 1680 FC03 80', 'HANDLER 1680 FC03 40'),
                    good + 'BUTTON 0 80\n', good.replace('CONTROLLER_DONE 2200', 'CONTROLLER_DONE 2100')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_output(bad)


if __name__ == '__main__':
    unittest.main()
