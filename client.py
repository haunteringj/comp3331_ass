# Used sample code from TCPclient.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66101,
# and https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
 
import socket
import sys
import datetime

# Finding given port number. Raise error if invalid port number.
server_port = int(sys.argv[1])
if server_port == 80 or server_port == 8080 or server_port < 1024:
    print("Error: Use a standard port number")
    sys.exit(1)

# Get user's username
username = input("Enter username: ")

# Creating socket and intially setting up the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', server_port))
client_socket.setblocking(False)

print(f"User {username} connected to 127.0.0.1:{server_port}")

while True: 
    #message_recv = client_socket.recv(1024).decode()
    #print("Received message from" + "127.0.0.1:%d" %(server_port) + message_recv)

    message_send = input("Enter message: ")
    date = datetime.datetime.now()
    message = f"{date} | {username} > {message_send}"
    client_socket.send(message.encode())


