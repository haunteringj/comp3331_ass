# Jay Patel, z5309776

# Used sample code from TCPserver.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66096,
# and https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/

from socket import *
from threading import Thread
import sys, select

# Check for arguments when starting server.py
if len(sys.argv) != 2:
    print("Error: Usage: python3 server.py port_num")
    sys.exit(1)

# Finding given port number. Raise error if invalid port number.
server_port = int(sys.argv[1])
if server_port == 80 or server_port == 8080 or server_port < 1024:
    print("Error: Use a standard port number")
    sys.exit(1)

server_addr = ('localhost', server_port)

# Creating socket and intially setting up server
server_socket = socket(AF_INET, SOCK_STREAM)
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_addr)

clients = {}

#Multi-thread class for client
#This class would be used to define the instance for each connection from each client
class ClientThread(Thread):
    def __init__(self, client_addr, client_socket):
        Thread.__init__(self)
        self.client_addr = client_addr
        self.client_socket = client_socket
        self.client_alive = False
        
        print("===== New connection created for: ", client_addr)
        self.client_alive = True
        
    def run(self):
        message = ''
        
        while self.client_alive:
            # use recv() to receive message from the client
            data = self.client_socket.recv(1024)
            message = data.decode()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.client_alive = False
                print("===== the user disconnected - ", client_addr)
                break
            
            # handle message from the client
            if message == 'login':
                print("[recv] New login request")
                self.process_login()
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.client_socket.send(message.encode())
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! QUICK WAY FOR ME TO CLOSE SERVER
            elif message == 'q':
                exit()
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.client_socket.send(message.encode())
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self):
    # Check if client's details are true. Client gets 3 attempts before being locked out
    # Check for username
        while True:
            credentials_username = client_socket.recv(1024).decode()
            break

        # Iterate through credentials file to check for username
        credientials_file = open("credentials.txt", "r+")
        create_account = True
        for value in credientials_file:
            crediential = value.split()
            # If username exists, get password from client
            if crediential[0] == credentials_username:
                client_socket.send(("username_validated").encode())
                create_account = False

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

        if create_account == True:
            # If username does not exist, create a new account
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
            # Close credentials file
        credientials_file.close()


print("Listening for connections on 127.0.0.1:%d" %(server_port),"...")
print("Waiting for connection request from clients...")


while True:
    server_socket.listen()
    client_socket, client_addr = server_socket.accept()
    clientThread = ClientThread(client_addr, client_socket)
    clientThread.start()