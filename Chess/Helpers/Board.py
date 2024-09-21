class Board:
    def __init__(self):
        # Define the starting Klipper coordinates for the lower-left corner (a1)
        self.start_x = 25
        self.start_y = 340

        # Define the step size between the centers of each square (in mm)
        self.step_x = 50  # Distance between columns (along x-axis)
        self.step_y = 50  # Distance between rows (along y-axis)

        # Mapping from UCI file (a-h) to column index (0-7)
        self.file_mapping = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    def get_klipper_coords(self, uci_square):
        """Converts UCI chess square like 'e2' to Klipper (x, y) coordinates"""
        # Split UCI square into file (letter) and rank (number)
        file = uci_square[0]  # e.g., 'a'
        rank = int(uci_square[1])  # e.g., 1

        # Calculate the x and y offsets based on the file and rank
        x_offset = self.file_mapping[file] * self.step_x
        y_offset = (rank - 1) * self.step_y

        # Calculate the final Klipper coordinates
        klipper_x = self.start_x + x_offset
        klipper_y = self.start_y - y_offset  # Y decreases as rank increases

        return (klipper_x, klipper_y)
