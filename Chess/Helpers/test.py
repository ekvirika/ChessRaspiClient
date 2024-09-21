from Board import Board
import requests

mainsail_url = "http://<your-raspberry-pi-ip>/printer/gcode/script"  
def send_gcode(self, gcode):
        response = requests.post(self.mainsail_url, json={"gcode": gcode})
        if response.status_code == 200:
            print(f"G-code '{gcode}' sent successfully!")
        else:
            print(f"Error sending G-code: {response.status_code}, {response.text}")

def main():
    board = Board()
    while True:
        uci_square = input("Enter the chess square (e.g., e2) or 'q' to quit: ").strip().lower()
        if uci_square == 'q':
            print("Exiting...")
            break
        if len(uci_square) != 2 or uci_square[0] not in board.file_mapping or not (1 <= int(uci_square[1]) <= 8):
            print("Invalid input. Please enter a valid square (e.g., e2).")
            continue

        klipper_coords = board.get_klipper_coords(uci_square)
        gcode = f"G1 X{klipper_coords[0]} Y{klipper_coords[1]} F6000"
        board.send_gcode(gcode)

if __name__ == "__main__":
    main()