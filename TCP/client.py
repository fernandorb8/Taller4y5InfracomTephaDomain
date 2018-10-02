
# HOST = 'localhost'
# PORT = 9876
# ADDR = (HOST,PORT)
# BUFSIZE = 4096
# videofile = "videos/royalty-free_footage_wien_18_640x360.mp4"

# bytes = open(videofile, 'rb').read()

# print len(bytes)

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDR)

# client.send(bytes)

# client.close()
import socket
import argparse

#Arguments for the client
parser = argparse.ArgumentParser(description='TCP client')

parser.add_argument('--host', type=str, default='localhost',
                    help='hostname of the server to connect')

parser.add_argument('--port', default=9000,
                    help='port of the server to connect')

parser.add_argument('--buffsize', default=4096,
                    help='size of buffer for the client')

args = parser.parse_args()

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# connect the client
# client.connect((target, port))
try:
    #Initialization of handshake
    client.connect((args.host, args.port))
    client.send('SYN'.encode())
    # receive the response data
    response = client.recv(args.buffsize)
    print(response)
    if response == b'SYNACK':
        client.send('ACK'.encode())
        #Registro tiempo
        video = client.recv(args.buffsize)
        separator = client.recv(args.buffsize)
        vhash = client.recv(args.buffsize)
        print(video)
        client.send('bye'.encode())
    else:
        client.send('bye'.encode())
except Exception as err:
    print(err)