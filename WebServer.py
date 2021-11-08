import socket
import sys
# Used sample TCPServer.py from webcms: https://webcms3.cse.unsw.edu.au/COMP3331/21T3/resources/66096
# Used part of https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842 which was found via edstem

if len(sys.argv) != 2:
    print("Erorr: Usage: python3 WebServer.py port")
    sys.exit(1)

# Creating socket and setting up server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_port = int(sys.argv[1])

if server_port == 80 or server_port == 8080 or server_port < 1024:
    print("Use a standard port number")
    sys.exit(1)

server_socket.bind(('localhost', server_port))
server_socket.listen(1)

# Infinite loop
while True:
    # Get request
    connection_socket, address = server_socket.accept()
    sentence = connection_socket.recv(1024)

    # Check for file being requested. Split message
    msg = sentence.split()
    msg_split = msg[1]
    # Split message again to get file name
    temp = msg_split.split("/")
    file_name = temp[1]

    print("\n")
    print(file)

    # Try Catch
    try:
        file = open(file_name, "r")
        print("\n file found")
        message = file.read()
        file.close()

        data = "HTTP/1.1 200 OK \r\n"
        connection_socket.send(data)

        # Send image or html depending on file_name
        if "png" in file_name:
            data = "Content-Type: image/png \r\n\r\n"
        elif "html" in file_name:
            data = "Content-Type: text/html \r\n\r\n"

        connection_socket.send(data)
        connection_socket.send(message)
        connection_socket.close()

    # Catch
    except IOError:
        response = '404 Not Found'
        print(response)
        connection_socket.send(response)
        connection_socket.close()
