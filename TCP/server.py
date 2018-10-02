import socket
import argparse
import threading

#Arguments for the server
parser = argparse.ArgumentParser(description='TCP server')

parser.add_argument('--host', type=str, default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096,
                    help='size of buffer for the server')

parser.add_argument('--nclients', default=1,
                    help='number of clients the server will manage')

args = parser.parse_args()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((args.host,args.port))
server.listen(5) 

video = '************'.encode()
hashVideo = str(hash(video)).encode()
separator = ';'.encode()
numClients = 1
clients = []

print('Listening on {}:{}'.format(args.host, args.port))

def handle_client_connection(client_socket):
    try:
        request = client_socket.recv(args.buffsize)
        while(request != 'bye'.encode()):
            print('Received {}'.format(request))
            if request == b'SYN':
                client_socket.send('SYNACK')
            if request == b'ACK':
                # registro tiempo
                client_socket.send(video)
                client_socket.send(separator)
                client_socket.send(hashVideo)
            request = client_socket.recv(args.buffsize)
    except Exception as err:
        client_socket.close()
    client_socket.close()

while True:
    client_sock, address = server.accept()
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    clients.append(client_sock)
    if args.nclients == len(clients):
        for client_sock in clients:
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
            )
            client_handler.start()