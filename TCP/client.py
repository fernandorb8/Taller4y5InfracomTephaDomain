import socket
import argparse
import hashlib
import time
import asyncio

#Arguments for the client
parser = argparse.ArgumentParser(description='TCP client')

parser.add_argument('--host', type=str, default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096*4,
                    help='size of buffer for the client')

parser.add_argument('--out', default='test_client_1.log',
                    help='output file for the log')

args = parser.parse_args()

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# open log file
fl = open(args.out, 'w')

# header of file
fl.write(time.strftime('%c'))
fl.write('Listening on {}:{}'.format(args.host, args.port))
fl.write('buffsize {}'.format(args.buffsize))
fl.write('-----------------')

# function that writes on the log file
def log_event(time, message):
    fl.write('execution time: {} s \n'.format(time))
    fl.write('message: {} \n'.format(message))
    fl.write('----------------- \n')

def receive(act, client, start, chunks, lenMess, i):
    hashact = client.recv(args.buffsize)
    myhash = hashlib.sha256(act).hexdigest().encode()
    print(act)
    if hashact == myhash:
        print('++++++')
        chunks[i] = act
    else:
        log_event(time.time()-start, 'Message lost')
    print((i/lenMess)*100)

# async def main():
# connect the client
try:
    #Initialization of handshake
    client.connect((args.host, args.port))
    client.send('SYN'.encode())
    # receive the response data
    response = client.recv(args.buffsize)
    print(response)
    if response == b'SYNACK':
        client.send('ACK'.encode())
        #Start time
        start = time.time()
        end = False
        while(not end):
            # video = client.recv(args.buffsize)
            lenMess = int(client.recv(args.buffsize).decode())
            print('Received {}'.format(lenMess))
            chunks = ['']*lenMess
            full = False
            i = 0
            while(not full):
                act = client.recv(args.buffsize)
                if(act == b'END'):
                    print('Entreeeeeee')
                    full = True
                    break
                else: 
                    # receive(act, client, start, chunks, lenMess, i)
                    hashact = client.recv(args.buffsize)
                    myhash = hashlib.sha256(act).hexdigest().encode()
                    if hashact == myhash:
                        print('++++++')
                        chunks[i] = act
                    else:
                        log_event(time.time(), 'Message lost')
                    print((i/lenMess)*100)
                    i += 1
                    print('Received {}'.format(act))
                    print('Received {}'.format(hashact))
            # vhash = client.recv(args.buffsize)
            # print('Received {}'.format(vhash))
            # hashVideo = hashlib.sha256(video).hexdigest().encode()
            if lenMess == lenMess:
                client.send('OK'.encode())
                end = True
                # Stop and print
                log_event(time.time()-start, 'Video received successfully')
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

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()