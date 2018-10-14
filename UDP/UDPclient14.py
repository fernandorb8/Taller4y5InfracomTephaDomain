import socket , argparse, threading , hashlib , time, select

#Arguments for the client
parser = argparse.ArgumentParser(description='UDP client')

parser.add_argument('--host', type=str, default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=65536,
                    help='size of buffer for the client')

parser.add_argument('--out', default='test_client_14.log',
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
    print('ready-to-receive')
    chunks= int(client.recv(args.buffsize).decode('ISO-8859-1'))
    datahash = client.recv(args.buffsize).decode('ISO-8859-1')
    start = time.time()
    packets=True
    data = ''
    i=0
    client.setblocking(0)

    while packets:
        ready = select.select([client], [], [], 20)
        if ready[0]:
            request=client.recv(args.buffsize)
            if 'END-FILE' not in request.decode('ISO-8859-1'):
                i+=1
                data+= request.decode('ISO-8859-1')
                print('receiving data...'+str(i))
            else:
                packets=False
                for x in range(10):
                    print('END-MESSAGE')


    print(str(i)+' packets recieved')

    new_file= open('new_file14.txt','wb')
    new_file.write(data.encode('ISO-8859-1'))
    new_file.flush()

    sha1 = hashlib.sha1()
    with open('new_file14.txt', 'rb') as f:
        while True:
            data = f.read(args.buffsize)
            if not data:
                break
            sha1.update(data)

    hashData = sha1.hexdigest()

    if datahash == hashData:
        client.send('ok'.encode('ISO-8859-1'))
        log_event(time.time()-start,'send_state: ok, recieved succesfully. packets send= '+ str(chunks) + ' . packets received= '+ str(i))
    else:
        client.send('error'.encode('ISO-8859-1'))
        log_event(time.time()-start,'send_state: error, Problems receiving the data. packets send= '+ str(chunks) + ' . packets received= '+ str(i))
except Exception as err:
    print(err)
