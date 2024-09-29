import socket

# Function to get UCI move from the user
def get_uci_move():
    uci_move = input("Enter your UCI move (e.g., e2e4): ")
    return uci_move

# Create a socket and connect to the Raspberry Pi
raspberry_pi_ip = '172.20.10.2'  # Replace with your Raspberry Pi's IP
port = 12346

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((raspberry_pi_ip, port))

try:
    while True:
        uci_move = get_uci_move()  # Get UCI move from the user
        if uci_move:
            # Send the UCI move over the socket
            sock.sendall(uci_move.encode())
            print(f"Sent move: {uci_move}")
finally:
    sock.close()
