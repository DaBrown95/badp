import unittest

from tools.sprite_layout import compare_layout, decode_layout


class SpriteLayoutTests(unittest.TestCase):
    def bank(self):
        bank = bytearray(0x8000)
        # Two frames, with the first repeated in the animation table.
        bank[:9] = bytes([0x53, 3, 4, 9, 0x80, 13, 0x80, 9, 0x80])
        bank[9:17] = bytes([0, 0x11, 3, 0, 0x80, 0x11, 4, 0])
        return bank

    def test_exact_tiling_and_frame_pointer_closure(self):
        result = decode_layout(bytes(self.bank()), 0, 9, 17)
        self.assertEqual(len(result['animations']), 1)
        self.assertEqual(len(result['frames']), 2)
        self.assertEqual(result['frames_without_animation_pointer'], [])
        self.assertEqual(result['animation_bytes'] + result['frame_bytes'], 17)

    def test_rejects_interior_pointer_truncated_tables_and_zero_dimension_wrap(self):
        for change in ('interior', 'truncated', 'wrapped_frame', 'wrong_marker'):
            bank = self.bank()
            if change == 'interior': bank[3] += 1
            elif change == 'truncated': bank[1] = 4
            elif change == 'wrapped_frame': bank[10] = 0
            else: bank[0] = 0x4f
            with self.subTest(change=change), self.assertRaises(ValueError):
                decode_layout(bytes(bank), 0, 9, 17)

    def test_directory_and_frame_relocations_can_differ(self):
        original = bytes(self.bank())
        layout = decode_layout(original, 0, 9, 17)
        other = bytearray(0x8000)
        other[30:38] = original[9:17]
        other[2:11] = bytes([0x53, 3, 4, 30, 0x80, 34, 0x80, 30, 0x80])
        compared = compare_layout(original, layout, bytes(other))
        self.assertEqual(compared['frame_delta'], 21)
        self.assertEqual(compared['animation_directory_delta'], 2)
        self.assertTrue(compared['normalized_animation_directory_unique'])
        other[40:48] = other[30:38]
        self.assertEqual(compare_layout(original, layout, bytes(other)),
                         {'frame_region_exact_occurrences': 'multiple'})


if __name__ == '__main__':
    unittest.main()
