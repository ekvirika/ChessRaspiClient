import unittest
from Board import Board  # Assuming your board class is in board.py

class TestBoard(unittest.TestCase):
    def setUp(self):
        # This method will run before each test case
        self.board = Board()

    def test_a1(self):
        # Test that 'a1' returns the correct Klipper coordinates
        self.assertEqual(self.board.get_klipper_coords('a1'), (25, 340))

    def test_e2(self):
        # Test that 'e2' returns the correct Klipper coordinates
        self.assertEqual(self.board.get_klipper_coords('e2'), (25 + 4 * 50, 340 - 50))

    def test_h8(self):
        # Test that 'h8' returns the correct Klipper coordinates
        self.assertEqual(self.board.get_klipper_coords('h8'), (25 + 7 * 50, 340 - 7 * 50))


if __name__ == '__main__':
    unittest.main()
