import socket

class SendMove:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_gcode(self, gcode):
        """Send a G-code command to Klipper"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(gcode.encode())

    def move_to(self, x, y):
        """Moves the magnet to the (x, y) coordinates on the board"""
        gcode = f"G1 X{x} Y{y} F3000"  # G1 moves with feedrate F
        self.send_gcode(gcode)
