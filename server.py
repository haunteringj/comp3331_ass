# Jay Patel, z5309776

# Used sample code from TCPserver.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66096,
# and https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/

from socket import *
from threading import Thread
import sys
import select

# Check for arguments when starting server.py
if len(sys.argv) != 2:
    print("> Error: Usage: python3 server.py port_num")
    sys.exit(1)

# Finding given port number. Raise error if invalid port number.
server_port = int(sys.argv[1])
if server_port == 80 or server_port == 8080 or server_port < 1024:
    print("> Error: Use a standard port number")
    sys.exit(1)

server_addr = ('localhost', server_port)

# Creating socket and intially setting up server
server_socket = socket(AF_INET, SOCK_STREAM)
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_addr)

print("> Listening for connections on 127.0.0.1:%d" %(server_port),"...")        

# List of active sockets
sockets_list = []
# List of all clients which have joined. Used to keep record of users names and their sockets
clients= {}

#Multi-thread class for client
#This class would be used to define the instance for each connection from each client
class ClientThread(Thread):
    def __init__(self, client_addr, client_socket):
        Thread.__init__(self)
        self.client_addr = client_addr
        self.client_socket = client_socket
        self.client_alive = False

        self.client_alive = True
        
    def run(self):
        message = ''
        
        if self.client_alive:
            self.process_login()
        
        while self.client_alive:
            # Use recv() to receive message from the client
            data = self.client_socket.recv(1024)
            message = data.decode()
            
            message_words = message.split()            
                    
            # If the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.client_alive = False
                print("> User disconnected - ", client_addr)
                sockets_list.remove(client_socket)
                break
            
            # If client uses the broadcast command, send messages to all online users except the sender and blocked clients
            if message_words[0] == "message":
                print(message)
            elif message_words[0] == "broadcast":
                self.broadcast(message)
            elif message == "whoelse":
                print("message")
            elif message == "whoelsesince":
                print("message")
            elif message_words[0] == "block":
                print("message")
            elif message_words[0] == "unblock":
                print("message")
            # If client uses the logout command, broadcast presence and delete socket from sockets_list
            elif message == 'logout':
                self.logout()
            else:
                print(f"> Recieved message from {client_addr}: \n{message}")

    # Method for broadcasting message
    def broadcast(self, message):                
        
        # If message is a presence message, do not edit message
        if message == (f"> {client_addr} has joined the server!"):
            print(message)
        else:
            message = (f"> Broadcasting message from {clients[client_socket]}: {message}")
        print(message)

        # Iterate through all online sockets and send message to all users
        for socket in sockets_list:
            # Do not broadcast to the sender
            if socket != self.client_socket:
                socket.send(message.encode())
                
    # Method for processing user logouts
    def logout(self):
        print("logging out")
        message = (f"> {clients[client_socket]} has disconnected from the server")
        self.broadcast(message)
        message = ("disconnecting_user_logout")
        self.client_socket.send(message.encode())        
        sockets_list.remove(self.client_socket)
        
    # Method for processing user logins and account creations
    def process_login(self):
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! NEED TO ADD, USER CANNOT LOGIN TO AN ACCOUNT THAT IS BEING USED !!!!!!!!!!!!!!
    # Check if client's details are true. Client gets 3 attempts before being locked out
    # Check for username
        credentials_username = client_socket.recv(1024).decode()
        
        print("> " + credentials_username)

        # Iterate through credentials file to check for username
        credientials_file = open("credentials.txt", "r+")
        create_account = True
        for value in credientials_file:
            crediential = value.split()
            # If username exists, get password from client
            if crediential[0] == credentials_username:
                self.client_socket.send(("username_validated").encode())
                create_account = False

                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! PRNTING USERS PASSWORDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print("> " + crediential[1])

                # Check if password matches username
                attempts = 2
                while True:
                    # Get password from client
                    credentials_password = client_socket.recv(1024).decode()

                    # Check if password matches
                    if crediential[1] == credentials_password:
                        self.client_socket.send(("user_authorised").encode())
                                        
                        # Add client to list of sockets_list
                        sockets_list.append(self.client_socket)
                        clients[client_socket] = credentials_username
                        
                        # Broadcast presence when someone joins the server
                        print(f"> Accepting new connection from {crediential[0]}")
                        presence_broadcast = (f"> {credentials_username} has joined the server!")
                        self.broadcast(presence_broadcast)
                        break 

                    # Check if the client has not attempted to login more that 3 times
                    elif attempts > 0:
                        self.client_socket.send(("Error: Incorrect password. Attempts remaining {attempts}").encode())
                        attempts = attempts - 1
                    # Otherwise break connection with the client
                    else: 
                        self.client_socket.send(("Error: Incorrect password. Breaking connection with this client").encode())
                        break

        if create_account == True:
            # If username does not exist, create a new account
            self.client_socket.send(("username_invalid").encode())
            credentials_password = client_socket.recv(1024).decode()
            new_credntials = credentials_username + ' ' + credentials_password
            # Append new account to credentials file
            credientials_file.write("\n")
            credientials_file.write(new_credntials)

            # Add client to list of sockets_list
            sockets_list.append(self.client_socket)
            clients[client_socket] = credentials_username

            # Broadcast presence when someone joins the server
            print(f"> Accepting new connection from {credentials_username}")
            presence_broadcast = (f"> {credentials_username} has joined the server!")
            self.broadcast(presence_broadcast)
            
            # Let client know, account creation was successful
            self.client_socket.send(("account_created").encode())
            # Close credentials file
        credientials_file.close()

while True:
    server_socket.listen()
    client_socket, client_addr = server_socket.accept()
    clientThread = ClientThread(client_addr, client_socket)
    clientThread.start()