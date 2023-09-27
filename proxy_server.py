import socket
from threading import Thread

BYTES_TO_READ = 4096
PROXY_SERVER_HOST = "127.0.0.1"
PROXY_SERVER_PORT = 8080


# send some data (request) to host : port
def send_request(host, port, request):

    # create a new socket in with block to ensure it is closed once we're done
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))  # connect the socket to host:port
        client_socket.send(request)  # send the request through the connected socket
        client_socket.shutdown(socket.SHUT_WR)  # shut the socket to further writes. tells server we are done sending

        # assemble response
        data = client_socket.recv(BYTES_TO_READ)
        result = b'' + data
        while len(data) > 0:
            data = client_socket.recv(BYTES_TO_READ)
            result += data

        return result


# Handle an incoming connection that has been accepted by the server
def handle_connection(conn, addr):

    with conn:
        print(f"Connected by {addr}")

        request = b''
        while True:  # While the client is keeping the socket open
            data = conn.recv(BYTES_TO_READ) # read some data from socket
            if not data: # if the socket has been closed to further writes, break
                break
            print(data)
            request += data

        response = send_request("www.google.com", 80, request)  # send it as a request to www.google.com
        conn.sendall(response)


# start single threaded proxy server
def start_server():
    """
    Create the socket in 'with' block to ensure it gets auto closed once we are done
    """

    with  socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the server to a specific host and port on this machine
        server_socket.bind((PROXY_SERVER_HOST, PROXY_SERVER_PORT))

        """
        Allow us to reuse this socket address during linger, as well as other implications
        """

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.listen(2)

        """
        Wait for incoming connection, and when one arrives, accept it and create a new socket called conn to interact with it
        """

        conn, addr = server_socket.accept()

        # pass 'conn' off to handle_connection to do some logic
        handle_connection(conn, addr)


# start multi threaded proxy server
def start_threaded_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((PROXY_SERVER_HOST, PROXY_SERVER_PORT))
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.listen(2)  # allow queuing of up to two connections

        while True:
            conn, addr = server_socket.accept()
            thread = Thread(target = handle_connection, args=(conn, addr))
            thread.run()


start_server()
# start_threaded_server()