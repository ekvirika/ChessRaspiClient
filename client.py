import socket
import time
import json  # To serialize the array

# Example 8x8 boolean array (replace this with your actual data)
bool_array = [
    [True, False, True, False, True, False, True, False],
    [False, True, False, True, False, True, False, True],
    [True, True, False, False, True, True, False, False],
    [False, False, True, True, False, False, True, True],
    [True, False, True, False, True, False, True, False],
    [False, True, False, True, False, True, False, True],
    [True, True, False, False, True, True, False, False],
    [False, False, True, True, False, False, True, True],
]

# Convert boolean array to a JSON string (or you can use another format)
data_to_send = json.dumps(bool_array)

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the Raspberry Pi
raspberry_pi_ip = '172.20.10.2'  # Raspberry Pi's IP address
sock.connect((raspberry_pi_ip, 12345))  # Port number should match the server

try:
    while True:
        # Send the data
        sock.sendall(data_to_send.encode())  # Encode the string to bytes
        print(f"Sent: {data_to_send}")
        
        # Wait for 5 seconds before sending the next array
        time.sleep(5)
finally:
    # Close the socket when done
    sock.close()
