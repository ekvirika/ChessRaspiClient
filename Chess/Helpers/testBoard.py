import unittest
from Board import Board
class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_get_klipper_coords_a1(self):
        expected = (25, 340)
        result = self.board.get_klipper_coords('a1')
        self.assertEqual(result, expected)

    def test_get_klipper_coords_h8(self):
        expected = (75, 340)
        result = self.board.get_klipper_coords('a2')
        self.assertEqual(result, expected)

    def test_get_klipper_coords_d4(self):
        expected = (225, 190)
        result = self.board.get_klipper_coords('d4')
        self.assertEqual(result, expected)

    def test_get_klipper_coords_e5(self):
        expected = (25, 290)
        result = self.board.get_klipper_coords('b1')
        self.assertEqual(result, expected)

    def test_get_klipper_coords_c3(self):
        expected = (25, 240)
        result = self.board.get_klipper_coords('c3')
        self.assertEqual(result, expected)

    def test_get_klipper_coords_b2(self):
        expected = (75, 290)
        result = self.board.get_klipper_coords('b2')
        self.assertEqual(result, expected)

    def test_get_klipper_coords_g7(self):
        expected = (325, 40)
        result = self.board.get_klipper_coords('g7')
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
