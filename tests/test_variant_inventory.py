"""Variant audio starts preserve namespaces and require a physical debug label."""
import unittest

from tools.audio_flow import literal_seeds
from tools.variant_inventory import audio_source_literals


class VariantInventoryTests(unittest.TestCase):
    def test_relocated_audio_literals_and_native_label(self):
        source = '''
    BogusStartVoice4 (($2123 + (-8)))
ScriptOp18:
    ldx #<LegacyOpcode18Audio
    ldy #>LegacyOpcode18Audio
    jsr StartAudioVoice
.assert 1, error, "synthetic"
'''
        debug = '''seg\tid=7,name="PRG0",start=0x8000,size=0x8000,ooffs=16
scope\tid=1,name="Bank0"
sym\tname="LegacyOpcode18Audio",scope=1,val=0x9345,seg=7,type=lab
'''
        self.assertEqual(literal_seeds(audio_source_literals(source, debug)), [0x211b, 0x9345])
        for bad in (debug.replace('PRG0', 'PRG1'), debug.replace('ooffs=16', 'ooffs=32784'),
                    debug.replace('Bank0', 'Bank1'), debug + debug.splitlines()[-1] + '\n'):
            with self.assertRaises(ValueError):audio_source_literals(source, bad)
        with self.assertRaises(ValueError):audio_source_literals(source.replace('(-8)', '(-99999)'), debug)
        with self.assertRaises(ValueError):literal_seeds(audio_source_literals(source.replace('(-8)', '(Other)'), debug))
