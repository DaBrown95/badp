"""Audio-route checks use synthetic records and never contain game bytes."""
import unittest

from tools.trace_audio_route import EXPECTED_STARTS, probe_script, validate_entries


class AudioRouteTests(unittest.TestCase):
    def test_probe_requires_complete_unique_input_and_audio_hooks(self):
        gameplay = ('before\nemu.addEventCallback(function()\n local move=frames>=180\n'
                    'end,emu.eventType.inputPolled)\nafter')
        audio = ('before\nlocal pending=false\nlocal crossings=0\n'
                 'emu.addEventCallback(function()\n local move=frames>=180\nafter')
        generated = probe_script(gameplay, audio)
        self.assertIn('local SCENARIO=4;local frames=0', generated)
        self.assertIn('end,emu.eventType.inputPolled)', generated)
        self.assertIn('frames==4300', generated)
        for invalid_gameplay, invalid_audio in ((gameplay.replace('inputPolled', 'endFrame'), audio),
                                                (gameplay + gameplay, audio),
                                                (gameplay, audio.replace('local pending=false', ''))):
            with self.subTest(gameplay=invalid_gameplay, audio=invalid_audio), self.assertRaises(ValueError):
                probe_script(invalid_gameplay, invalid_audio)

    def test_requires_each_expected_entry_and_no_conflicting_decode(self):
        good = {'commands': [{'physical_prg_offset': offset} for offset in EXPECTED_STARTS],
                'conflicts': []}
        validate_entries(good)
        with self.assertRaisesRegex(ValueError, 'expected audio commands'):
            validate_entries({'commands': good['commands'][:-1], 'conflicts': []})
        with self.assertRaisesRegex(ValueError, 'conflicting decodes'):
            validate_entries({'commands': good['commands'], 'conflicts': [{'physical_prg_offset': 0}]})


if __name__ == '__main__':
    unittest.main()
