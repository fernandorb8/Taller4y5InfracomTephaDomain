import socket
import argparse
import hashlib
import time
import os
import os.path as osp

#Arguments for the client
parser = argparse.ArgumentParser(description='TCP client')

parser.add_argument('--host', default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096,
                    help='size of buffer for the client')

parser.add_argument('--out', default='test_client_1.log',
                    help='output file for the log')

parser.add_argument('--file', default='./../files/myfile_250',
                    help='file to transfer to the clients')

args = parser.parse_args()

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Info of file
fileContents = []
with open(args.file, 'rb') as f:
    fileContents = f.read()

video = fileContents

# open log file
fl = open(args.out, 'w')

# header of file
fl.write(time.strftime('%c') + '\n')
fl.write('Listening on {}:{} \n'.format(args.host, args.port))
fl.write('buffsize {}\n'.format(args.buffsize))
fl.write('-----------------\n')
fl.flush()

# function that writes on the log file
def log_event(time, message):
    fl.write('execution time: {} s\n'.format(time))
    fl.write('message: {} \n'.format(message))
    fl.write('-----------------\n')
    fl.flush()

def receiveVideo(client, start):
    chunks = []
    b_recv = 0
    while b_recv < len(fileContents):
        chunk = client.recv(min(len(fileContents) - b_recv, args.buffsize))
        if chunk == b'':
            log_event(time.time()-start, 'Connection broken')
        chunks.append(chunk)
        b_recv = len(chunk) + b_recv
        print('{}%'.format((b_recv/len(fileContents)*100)))
    log_event(time.time()-start, 'Video received successfully, {} packages received'.format(b_recv))
    return [b''.join(chunks), hashlib.sha256(b''.join(chunks)).hexdigest().encode]

# connect the client
try:
    #Initialization of handshake
    client.connect((args.host, args.port))
    print('Connected to Server!')
    client.send('SYN'.encode())
    # receive the response data
    response = client.recv(args.buffsize)
    print(response)
    if response == b'SYNACK':
        client.send('ACK'.encode())
        #Start time
        start = time.time()
        video, vhash = receiveVideo(client, start)
        hashVideo = hashlib.sha256(video).hexdigest().encode()
        if vhash == hashVideo:
            client.send('OK'.encode())
            log_event(time.time()-start, 'Video is correct')
        else:
            client.send('ACK'.encode())
            # Restart time and log problem
            prev = start
            start = time.time()
            log_event(start-prev, 'Problem receiving the video, sending again...')
        response = client.recv(args.buffsize)
        print(response)
        client.send('bye'.encode())
    else:
        client.send('bye'.encode())
except Exception as err:
    print(err)
    log_event(time.time(), 'An error ocurred in the connection with the server')