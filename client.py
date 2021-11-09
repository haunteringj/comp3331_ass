# Used sample code from TCPclient.py from webcms, https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66101,
# and https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
 
import socket 
import sys
import datetime

# Finding given port number. Raise error if invalid port number.
server_port = int(sys.argv[1])
if server_port == 80 or server_port == 8080 or server_port < 1024:
    print("> Error: Use a standard port number")
    sys.exit(1)

# Creating socket and intially setting up the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', server_port))
client_socket.setblocking(1)

# User authorisation
username = input("Enter username: ")
#auth = authorisation(client_socket)
# Authorise client's username
client_socket.send(username.encode())

# Check for server response after sending username
while True:
    username_validation = client_socket.recv(1024).decode()
    break

attempts = 2
if username_validation == "username_validated":
    # Check for server response after sending password
    while True:
        password = input("Enter password: ")
        # Send client's password for authorisation
        client_socket.send(password.encode())

        password_validation = client_socket.recv(1024).decode()

        # If password is validated, return true. else return false
        if password_validation == "user_authorised":
            print(f"> {username} successfully connected to 127.0.0.1:{server_port}")
            break
        # User gets only 3 attempts to enter the correct password
        elif attempts > 0: 
            print(f"> Error: Incorrect password. Attempts remaining {attempts}!")
            attempts = attempts - 1
        else:
            print("Error: password was entered incorrectly")
            sys.exit(1)
# If username does not exist, create a new account
elif username_validation == "username_invalid":
    print(f"> {username} does not have an associated account, please enter a password to create an account")
    password = input("Enter password: ")
    # Send password to server
    client_socket.send(password.encode())

    account_creation = client_socket.recv(1024).decode()

    if account_creation == "account_created":
        print("> Account successfully created!")
    else:
        print("> Error: Account creation was unsuccessful!")
        sys.exit(1)

 
while True: 
    message_send = input("Enter message: ")
    client_socket.send(message_send.encode())

    # receive response from the server
    # 1024 is a suggested packet size, you can specify it as 2048 or others
    data = client_socket.recv(1024)
    message_recv = data.decode()

    # parse the message received from server and take corresponding actions
    if message_recv == "":
        print("[recv] Message from server is empty!")
    else:
        print(f"{message_recv}")
        
    ans = input('\nDo you want to continue(y/n) :')
    if ans == 'y':
        continue
    else:
        break
