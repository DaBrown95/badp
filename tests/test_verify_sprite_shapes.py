"""Verify sprite dimension trace handling with synthetic pixels and addresses."""
import unittest
from tools.verify_sprite_shapes import parse_output, render_script


class SpriteShapeVerificationTests(unittest.TestCase):
    def test_complete_trace_and_template(self):
        bank = bytearray(0x8000); bank[0x101] = 0x34; bank[0x201] = 0x72
        addresses = [0x8100, 0x8200]
        output = ('SHAPE 0 8100 00101 34 03 04 2 0 0\n'
                  'SHAPE 1 8200 00201 72 07 02 2 0 0\nDONE 2')
        self.assertEqual(parse_output(output, bytes(bank), addresses)['frames'], 2)
        self.assertEqual(render_script('local cases={{FRAME_CASES}}', addresses),
                         'local cases={0x8100,0x8200}')
        for bad in (output.replace('00101', '08101'), output.replace('03 04 2', '03 04 1'),
                    output.replace('2 0 0', '2 0 1', 1), output.replace('DONE 2', 'DONE 1'),
                    output + '\nDONE 2', output + '\nTIMEOUT'):
            with self.subTest(end=bad[-20:]), self.assertRaises(ValueError):
                parse_output(bad, bytes(bank), addresses)

    def test_rejects_invalid_template_or_frame_addresses(self):
        for addresses in ([], [0xffff], [0x8100, 0x8100], [0x8200, 0x8100], [True]):
            with self.subTest(addresses=addresses), self.assertRaises(ValueError):
                render_script('{{FRAME_CASES}}', addresses)
        with self.assertRaises(ValueError): render_script('no placeholder', [0x8100])
        with self.assertRaises(ValueError): parse_output('', bytes(10), [0x8100])


if __name__ == '__main__':
    unittest.main()
