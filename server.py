# Jay Patel, z5309776

# Used sample code from TCPserver.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66096,
# and https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/

import socket
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
    # Accept connections from potential clients
    client_socket, client_addr = server_socket.accept()
    
    # Check if client's details are true. Client gets 3 attempts before being locked out
    # Check for username
    while True:
        credentials_username = client_socket.recv(1024).decode()
        break

    # Iterate through credentials file to check for username
    credientials_file = open("credentials.txt", "r+")
    for value in credientials_file:
        crediential = value.split()
        # If username exists, get password from client
        if crediential[0] == credentials_username:
            client_socket.send(("username_validated").encode())
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! PRNTING USERS PASSWORDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            print(crediential[1])

            # Check if password matches username
            attempts = 2
            while True:
                # Get password from client
                credentials_password = client_socket.recv(1024).decode()

                # Check if password matches
                if crediential[1] == credentials_password:
                    client_socket.send(("user_authorised").encode())
                                    
                    # Add client to list of clients
                    clients.append(client_socket)
                    print(f"Accepting new connection from {crediential[0]}")
                    break 

                # Check if the client has not attempted to login more that 3 times
                elif attempts > 0:
                    client_socket.send(("Error: Incorrect password. Attempts remaining {attempts}").encode())
                    attempts = attempts - 1
                # Otherwise break connection with the client
                else: 
                    client_socket.send(("Error: Incorrect password. Breaking connection with this client").encode())
                    break

        # If username does not exist, create a new account
        else:
            client_socket.send(("username_invalid").encode())
            credentials_password = client_socket.recv(1024).decode()
            new_credntials = credentials_username + ' ' + credentials_password
            # Append new account to credentials file
            credientials_file.write("\n")
            credientials_file.write(new_credntials)

            # Add client to list of clients
            clients.append(client_socket)
            print(f"Accepting new connection from {credentials_username}")
            
            # Let client know, account creation was successful
            client_socket.send(("account_created").encode())
            break
    # Close credentials file
    credientials_file.close()

    # Recieve/listen for messages sent by client
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(f"Recieved message from {client_addr}: \n{message}")

        except Exception as e:
            # Exception where client disconnects
            print(f"Error: {e}")
            clients.remove(client_socket)

        # If message is recieved, broadcast message to all clients
        for client_sock in clients:
            client_socket.send(message.encode())



