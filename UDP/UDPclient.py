import socket , argparse, threading , hashlib , time

#Arguments for the client
parser = argparse.ArgumentParser(description='UDP client')

parser.add_argument('--host', type=str, default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096,
                    help='size of buffer for the client')

parser.add_argument('--out', default='test_client_1.log',
                    help='output file for the log')

args = parser.parse_args()

# open log file
fl = open(args.out, 'w')
fl.write(time.strftime('%c')+'\n')
fl.write('Connecting to {}:{}'.format(args.host, args.port)+'\n')
fl.write('Buffsize {}'.format(args.buffsize)+'\n')
fl.write('-----------------'+'\n')
fl.flush()


def log_event(time, message):
    fl.write('execution time: {} s'.format(time)+'\n')
    fl.write(message+'\n')
    fl.write('-----------------'+'\n')
    fl.flush()

# create an ipv4 (AF_INET) socket object using the UDP protocol (SOCK_DGRAM)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    client.sendto('connect'.encode(),(args.host,args.port))

    state , address = client.recvfrom(args.buffsize)
    print(state)
    client.connect(address)
    client.send('ready-to-receive'.encode())
    start = time.time()
    video = client.recv(args.buffsize)
    vhash = client.recv(args.buffsize).decode('UTF-8')
    hashVideo = hashlib.sha256(video).hexdigest()
    if vhash == hashVideo:
        client.send('ok'.encode())
        log_event(time.time()-start,'send_state: ok, recieved succesfully')
    else:
        client.send('error'.encode())
        log_event(time.time()-start,'send_state: error, Problems receiving the data')
except Exception as err:
    print(err)
