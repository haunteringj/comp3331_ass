# Jay Patel, z5309776

# Used sample code from TCPserver.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66096,
# and https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/

import socket
import select
import sys

if len(sys.argv) != 2:
    print("Error: Usage: python3 server.py port_num")
    sys.exit(1)

# Creating socket and intially setting up server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Finding given port number. Raise error if invalid port number.
server_port = int(sys.argv[1])
if server_port == 80 or server_port == 8080 or server_port < 1024:
    print("Error: Use a standard port number")
    sys.exit(1)

# Bind and listen port
server_socket.bind(('localhost', server_port))
server_socket.listen(1)

# Create list of sockets and dict of clients
clients = []


print("Listening for connections on 127.0.0.1:%d" %(server_port),"...")

# Infinite loop to listen to clients
while True:
    # Get any clients and accept their connections
    client_socket, client_addr = server_socket.accept()
    clients.append(client_socket)
    print(f"Accepting new connection from {client_addr}")

    # Recieve/listen for messages sent by client
    while True:
        try:
            message = client_socket.recv(1024).decode()
        except Exception as e:
            # Exception where client disconnects
            print(f"Error: {e}")
            clients.remove(client_socket)

        print(f"Recieved message from {client_addr}: {message}")

        # If message is recieved, broadcast message to all clients
        for client_sock in clients:
            client_socket.send(message.encode())



