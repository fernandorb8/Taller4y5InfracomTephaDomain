import socket , argparse, threading , hashlib , time

#arguments
parser = argparse.ArgumentParser(description='UDP server')

parser.add_argument('--host', type=str, default='localhost', help='hostname of the server to connect')

parser.add_argument('--port', default=9000 , help='port of the server to connect')

parser.add_argument('--buffsize', default=4096, help='size of buffer for the server')

parser.add_argument('--nclients', default=1, help='number of clients the server will manage')

parser.add_argument('--out', default='test_udpserver_1.log', help='output file for the log')

args = parser.parse_args()

#initialize the server
UDPServerSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
UDPServerSocket.bind((args.host , args.port ))

# Encoding and hashing of the videos that are going to be sent
# TODO: Falta poner los dos videos.
video = '************'.encode()
hashVideo = hashlib.sha256(video).hexdigest()

# Initialize the list of clients connected
clients = []

# open log file
fl = open(args.out, 'w')

# header of file
fl.write(time.strftime('%c')+'\n')
fl.write('Listening on {}:{}'.format(args.host, args.port)+'\n')
fl.write('Buffsize {}'.format(args.buffsize)+'\n')
fl.write('Number of clients: {}'.format(args.nclients)+'\n')
fl.write('-----------------'+'\n')
fl.flush()


# function that writes on the log file
def log_event(time, message):
    fl.write('execution time: {} s'.format(time)+'\n')
    fl.write(message +'\n')
    fl.write('-----------------'+'\n')
    fl.flush()

print('Listening on {}:{}'.format(args.host, args.port))


def handle_client_connection(client_address,i):
    try:
        port_handle= args.port + i
        handle_socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
        handle_socket.bind((args.host , port_handle ))
        handle_socket.connect(client_address)
        handle_socket.send('connected'.encode())
        response = handle_socket.recv(args.buffsize)
        if response == 'ready-to-receive'.encode():
            start = time.time()
            handle_socket.send(video)
            handle_socket.send(hashVideo.encode())
            request = handle_socket.recv(args.buffsize)
            print(request)
            log_event(time.time()-start,'send-state: '+ request.decode('UTF-8'))

    except Exception as err:
        print(err)

while True:
    bytesAddressPair,address = UDPServerSocket.recvfrom(args.buffsize)
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    clients.append(address)
    if args.nclients == len(clients):
        i=1
        for client_address in clients:
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_address,i,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
            )
            client_handler.start()
            i+=1
