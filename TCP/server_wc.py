import socket
import argparse
import threading
import hashlib
import time
import os
import os.path as osp


#Arguments for the server
parser = argparse.ArgumentParser(description='TCP server')

parser.add_argument('--host', type=str, default='',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096,
                    help='size of buffer for the server')

parser.add_argument('--nclients', type=int, default=1,
                    help='number of clients the server will manage')

parser.add_argument('--out', default='test_server_1.log',
                    help='output file for the log')

parser.add_argument('--size', default=4*1024,
                    help='output file for the log')

parser.add_argument('--file', default='./../files/myfile_250',
                    help='file to transfer to the clients')

args = parser.parse_args()

# Initialize the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((args.host,args.port))
server.listen(5) 

# Encoding and hashing of the videos that are going to be sent
video = '************'.encode()
hashVideo = hashlib.sha256(video).hexdigest().encode()

# Initialize the list of clients connected 
clients = []

fileContents = []
with open(args.file, 'rb') as f:
    fileContents = f.read()

video = fileContents
hashVideo = hashlib.sha256(video).hexdigest().encode()

# create directory for log
# out_dir = 'Clients_{}_file_{}'.format(args.nclients, args.file.split('/')[-1]) 
# if osp.exists(out_dir):
#     os.system('rm -rf ' + out_dir)

# os.mkdir(out_dir)

# open log file
# fl = open(out_dir+'/'+args.out, 'w')
fl = open(args.out, 'w')

# header of file
fl.write(time.strftime('%c'))
fl.write('Listening on {}:{}\n'.format(args.host, args.port))
fl.write('Buffsize {}\n'.format(args.buffsize))
fl.write('Number of clients: {}\n'.format(args.nclients))
fl.write('-----------------\n')
fl.flush()

# function that writes on the log file
def log_event(time, message):
    fl.write('execution time: {} s \n'.format(time))
    fl.write('{} \n'.format(message))
    fl.write('----------------- \n')
    fl.flush()


print('Listening on {}:{}'.format(args.host, args.port))

def sendVideo(client_socket, start):
    total = 0
    while(total < len(fileContents)):
        sent = client_socket.send(video[total:])
        if sent == 0:
            log_event(time.time()-start, 'Connection broken')
        total = total + sent
        print('{}%'.format((total/len(fileContents))))
        time.sleep(0.3)
    log_event(time.time()-start, 'Video transferred successfully, {} packages sent'.format(total))

def handle_client_connection(client_socket, id):
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
                log_event(start, 'Start sending video to client {}'.format(id))
                print('Sending video ...')
                # client_socket.send(video)
                sendVideo(client_socket, start)
                # print('Sending hash ...')
                # client_socket.send(hashVideo)
                if request == b'OK':
                    # Stop time
                    log_event(time.time()-start, 'Video send successfully to client {}'.format(id))
                    client_socket.send('bye'.encode())
            elif request == b'OK':
                # Stop time
                log_event(time.time()-start, 'Video send successfully to client {}'.format(id))
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
        i = 0
        for client_sock in clients:
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,i,) 
            )
            client_handler.start()
            i = i + 1