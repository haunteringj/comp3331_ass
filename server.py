# Jay Patel, z5309776

# Used sample code from TCPserver.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66096,
# and https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/

from socket import *
from threading import Thread
import sys
import datetime
import time

# Check for arguments when starting server.py
if len(sys.argv) != 3:
    print("> Error: Usage: python3 server.py <server_port> <block_duration> <timeout>")
    sys.exit(1) 
    
timeout = int(sys.argv[2])

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
# Dict of all clients which have joined. key is the socket, value is a list containing names
clients = {}
# Dict of active clients. key socket, contains name, login time, and last active time
active_clients = {}
# Dict of all clients. key socket, contains name, login time, and last active time
all_clients = {}
# List of all offline messages, username as key, message as value. Stored as key|message
offline_messages = []
# List of all blocked users. username as key blocked clients as list. one user can block multiple clients
blocked = {}


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
            self.offline_messages()
        
        while self.client_alive:
            
            # Use recv() to receive message from the client
            data = self.client_socket.recv(1024)
            message = data.decode()

            message_words = message.split()            
                    
            # Case where user violently disconnects connection via cntrl+c or otherwise
            if message == '':
                print("> User disconnected -", client_addr)
                # Remove client from active sockets     
                sockets_list.remove(self.client_socket)
                active_clients.pop(self.client_socket)
                print("> Attempting to remove already logged-in user's data")
                self.client_alive = False
                break
            elif message == "already_logged_in":
                print("> User disconnected -", client_addr)
                self.client_alive = False
            
            # If client uses the broadcast command, send messages to all online users except the sender and blocked clients
            if message_words[0] == "message":
                
                message_blocked = False
                
                # Check if command is properly used
                if len(message_words) == 1:
                    message = "> Message has not been sent. Command usage: message <user> <message>"
                    self.client_socket.send(message.encode())   
                else: 
                    # Iterate through blocked dict to check if recipient has blocked the sender. If so, intercept message
                    for key in blocked:
                        if key == message_words[1]:
                            if clients[self.client_socket] in blocked[key]:
                                message_blocked = True
                                message = "> Message has not been sent. Recipient has been blocked by user."
                                print(message)
                                self.client_socket.send(message.encode())   
                    
                    # If recipient is not blocked, send message
                    if message_blocked == False:
                        self.message(message_words)
                    
            # Broadcast message to all clients
            elif message_words[0] == "broadcast":
                self.broadcast(message)
            # Reveal which other users are currently online
            elif message == "whoelse":
                self.whoelse()
            # Reveal which other users are online since a particluar time
            elif message == "whoelsesince":
                print("message")
            # Block a particular user
            elif message_words[0] == "block":
                # Check if command is properly used
                if len(message_words) != 2:
                    message = "> Error. Command usage: block <user>"
                    self.client_socket.send(message.encode())    
                else:
                    message = message_words[1]
                    self.block(message)
            # Unblock a particular user
            elif message_words[0] == "unblock":
                # Check if command is properly used
                if len(message_words) != 2:
                    message = "> Error. Command usage: unblock <user>"
                    self.client_socket.send(message.encode())    
                else:
                    message = message_words[1]
                    self.unblock(message)
            # If client uses the logout command, broadcast presence and delete socket from sockets_list
            elif message == 'logout':
                self.logout()
            else:
                print(f"> Recieved message from {client_addr}: \n{message}")

    # Function to directly message another online user
    def message(self, message_words):

        message = ""

        # Parse message so that it can be sent cleanly
        couter = 0
        for element in message_words:
            if couter ==  0:
                message += "> "
                message += clients[self.client_socket]
                message += " has"
                message += " messaged "
                couter += 1
            elif couter == 1:
                message += element
                message += ": "
                couter += 1
            else: 
                message += " "
                message += element

        # Find recipient's socket and send the message
        success = False
        for socket in sockets_list:
            if clients[socket] == message_words[1]:
                print(message)
                socket.send(message.encode())
                success = True
    
        # Let the sender know if their message was not sent
        if success == False:
            # Since user is offline, add to offline_messages
            offline_messages.append(f"{message_words[1]}|{message}")
            
            # Tell the client that their message has not been sent
            message = (f"> Message has not been sent. {message_words[1]} is offline")
            self.client_socket.send(message.encode())        

    def offline_messages(self):
        for messages in offline_messages:
            message = messages.split("|")
            
            if clients[self.client_socket] == message[0]:
                print("\n")
                message = "> Someone messaged you while you were offline" + "\n" + message[1]
                self.client_socket.send(message.encode())        

    # Method for broadcasting message
    def broadcast(self, message):                
        
        # If message is a presence message, do not edit message
        if message == (f"> {client_addr} has joined the server!"):
            print(message)
        else:
            message = (f"> Broadcasting message from {clients[self.client_socket]}: {message}")
        print(message)

        # Iterate through all online sockets and send message to all users
        for socket in sockets_list:
            block_message = False
            
            # Do not broadcast to the sender
            if socket != self.client_socket:
                
                # Iterate through blocked dict to check if recipient has blocked the sender. If so, intercept message
                for key in blocked:
                    if key == clients[self.client_socket]:
                        if clients[socket] in blocked[key]:
                            block_message = True
                
                if block_message == False:
                    socket.send(message.encode())
                        
                
    def whoelse(self):
        
        message = "> Currently, the following users are online:"
        # Iterate through all online sockets and add a list of usernames
        message_list = []
        for socket, user in active_clients.items():
            if socket != self.client_socket:
                message_list.append(user[0])
        
        for user in message_list:
            #if clients[self.client_socket] in blocked[user]:
            #    message_list.remove(user)
            
            block_user = False
            # Iterate through blocked dict to check if recipient has blocked the sender. If so, intercept message
            for key, item in blocked.items():
                if clients[self.client_socket] in item:
                        block_user = True
                # If user is blocked, remove them from the whoelse message
                if block_user == True:
                    message_list.remove(key)

        # Parse list into a suitable string and send it to the user 
        for item in message_list:
            message += " " + item
        self.client_socket.send(message.encode())        
    
    def block(self, user):
        if user == clients[self.client_socket]:
            message = "> Error. Cannot block yourself..."
            self.client_socket.send(message.encode())   
                         
        else:
            if clients[self.client_socket] not in blocked:
                blocked[clients[self.client_socket]] = []
            
            for key in blocked:
                if key == clients[self.client_socket]:
                    if user not in blocked[key]:
                        blocked[key].append(user)

                    else:
                        message = "> Error. User already blocked"
                        self.client_socket.send(message.encode())   
        print(blocked)
        
    def unblock(self, user):
        for key, value in blocked.items():
            if key == clients[self.client_socket]:
                if user in value:
                    value.remove(user)
                else:
                    message = f"> {user} was already unblocked"
                    self.client_socket.send(message.encode()) 
                
        print(blocked)
    
    # Method for processing user logouts
    def logout(self):
        if self.client_socket in sockets_list:        
            message = (f"> {clients[self.client_socket]} has disconnected from the server")
            # Broadcast presence
            self.broadcast(message)
            message = ("disconnecting_user_logout")
            self.client_socket.send(message.encode())   
            
            # Remove client from active sockets     
            sockets_list.remove(self.client_socket)
            active_clients.pop(self.client_socket)
            
            self.client_alive = False
            
        else:
            message = (f"> User {clients[self.client_socket]} has failed to logout")
            self.client_socket.send(message.encode())   
            
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
                
                logged_in = False
                for value in active_clients.values():
                    print(value)
                    if credentials_username in value:
                        print(f"> {crediential[0]} is already logged in...")
                        self.client_socket.send(("already_logged_in").encode())
                        logged_in = True     
                    
                if logged_in == True:
                    create_account = False
                    break       
                
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
                        
                        # Add to list of active clients including their date and time
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        active_clients[client_socket] = [credentials_username, current_time, current_time]
                        all_clients[client_socket] = [credentials_username, current_time, current_time]
                        
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
            
            # Add to list of active clients including their date and time
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            active_clients[client_socket] = [credentials_username, current_time, current_time]
            all_clients[client_socket] = [credentials_username, current_time, current_time]
                            
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
    client_thread = ClientThread(client_addr, client_socket)
    client_thread.start()