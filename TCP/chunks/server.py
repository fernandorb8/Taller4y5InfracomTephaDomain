import socket
import argparse
import threading
import hashlib
import time


#Arguments for the server
parser = argparse.ArgumentParser(description='TCP server')

parser.add_argument('--host', type=str, default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096,
                    help='size of buffer for the server')

parser.add_argument('--nclients', type=int, default=1,
                    help='number of clients the server will manage')

parser.add_argument('--out', default='test_server_1.log',
                    help='output file for the log')

parser.add_argument('--size', type= float, default=8*1024,
                    help='chunk size used for sending the complete message')

parser.add_argument('--file', default='./../files/test',
                    help='file to transfer to the clients')

args = parser.parse_args()

# Initialize the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((args.host,args.port))
server.listen(5) 

# Encoding and hashing of the videos that are going to be sent
# TODO: Falta poner los dos videos.
video = '************'.encode()
hashVideo = hashlib.sha256(video).hexdigest().encode()

# Initialize the list of clients connected 
clients = []

# open log file
fl = open(args.out, 'w')

# header of file
fl.write(time.strftime('%c') + '\n')
fl.write('Listening on {}:{} \n'.format(args.host, args.port))
fl.write('Buffsize {} \n'.format(args.buffsize))
fl.write('Number of clients: {} \n'.format(args.nclients))
fl.write('-----------------\n')

# function that writes on the log file
def log_event(time, message):
    fl.write('execution time: {} s \n'.format(time))
    fl.write('{} \n'.format(message))
    fl.write('----------------- \n')


def send_video(client_socket, start):
    lines = []
    # Open file and start reading in bytes
    with open(args.file, 'rb') as f:
        lines = [x.strip() for x in f.readlines()]
    
    #Send number of lines of the file
    print('Sending {} lines ...'.format(len(lines)))
    client_socket.send(str(len(lines)).encode())
    i = 1
    for line in lines:
        client_socket.send(line)
        print('Sending {}'.format(line))
        client_socket.send(hashlib.sha256(line).hexdigest().encode())
        print((i/len(lines))*100)
        i += 1
    print('finish!')
    while(client_socket.recv(args.buffsize) != b'OK'):
        client_socket.send('END'.encode())
    # Stop time
    print('Received the OK')
    log_event(time.time()-start, 'Video send successfully')
    client_socket.send('bye'.encode())

print('Listening on {}:{}'.format(args.host, args.port))

def handle_client_connection(client_socket):
    try:
        request = client_socket.recv(args.buffsize)
        end = False
        while(not end):
            print('Received {}'.format(request))
            if request == b'bye':
                end = True
            elif request == b'SYN':
                client_socket.send('SYNACK'.encode())
            elif request == b'ACK':
                # Start time
                start = time.time()
                log_event(start, 'Start sending video')
                send_video(client_socket, start)
                # if request == b'OK':
                #     # Stop time
                #     log_event(time.time()-start, 'Video send successfully')
                #     client_socket.send('bye'.encode())
            elif request == b'OK':
                # Stop time
                log_event(time.time()-start, 'Video send successfully')
                client_socket.send('bye'.encode())
                end = True
            request = client_socket.recv(args.buffsize)
    except Exception as err:
        client_socket.close()
        print(err)
    client_socket.close()

while True:
    client_sock, address = server.accept()
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    clients.append(client_sock)
    if args.nclients == len(clients):
        print('Starting threads ...')
        for client_sock in clients:
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
            )
            client_handler.start()