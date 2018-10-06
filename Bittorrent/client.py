# torrent.py
# Torrent file related utilities
#    Written by Joe Salisbury <salisbury.joseph@gmail.com>
#    Extended by Fernando Reyes Bejarano
#
#    You are free to use this code in anyway you see fit, on the basis
#    that if it is used, modified, or distributed, proper accreditation
#    of the original author remains.

from hashlib import md5, sha1
from random import choice
import socket
from threading import Thread, Lock
from time import sleep, time, strftime
from urllib.parse import urlencode
from urllib.request import urlopen
from util import collapse, slice
import argparse
import signal
from enum import Enum
import math
import sys
import os
import errno

from bencode import Decoder, Encoder

#Arguments for the tracker
parser = argparse.ArgumentParser(description='Bittorrent client')

parser.add_argument('--torrent', type=str, default="test.torrent",
                    help='torrent file')

parser.add_argument('--host', type=str, default="localhost",
                    help='hostname or IP of the client for log')

parser.add_argument('--port', default=6881, type=int,
                    help='port of the client')

parser.add_argument('--out', default='test_client_1.log', type=str,
                    help='output file name for the log')

parser.add_argument('--out_folder', default='test', type=str,
                    help='output file name for the log')

parser.add_argument('--seed', help='flag to indicate if client is seed',
                    action="store_true")

parser.add_argument('--cliversion', help='four digit version',
                   default="0001", type=str)

args = parser.parse_args()

#Make iteration folders
if not os.path.exists(args.out_folder + "/"):
    try:
        os.makedirs(args.out_folder + "/")
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

#Open the log file
with open(args.out_folder + "/" + args.out, 'w') as fl:
    # header of file
    fl.write(strftime('%c') + "\n")
    fl.write('Listening on {}:{}'.format(args.host, args.port) + "\n")
    fl.write('-'*17 + "\n")

def log_event(time, message):
    """ Function that writes on the log file """
    lock.acquire()
    with open(args.out_folder + "/" + args.out, 'a') as fl:
        fl.write('execution time: {} s'.format(time) + "\n")
        fl.write(message + "\n")
        fl.write('-'*17 + "\n")
    lock.release()

# Lock for concurrent writing on the log file
lock = Lock()

CLIENT_NAME = b"pytorrent"
CLIENT_ID = b"PY"
CLIENT_VERSION = args.cliversion.encode()

def read_torrent_file(torrent_file):
    """ Given a .torrent file, returns its decoded contents. """

    with open(torrent_file, "rb") as file:
        return Decoder(file.read()).decode()

def generate_peer_id() -> bytes:
    """ Returns a 20-byte peer id. """

    # As Azureus style seems most popular, we'll be using that.
    # Generate a 12 character long string of random numbers.
    random_string = ""
    while len(random_string) != 12:
        #random_string = random_string + choice("1234567890")
        random_string = random_string + choice("1")

    return b"-" + CLIENT_ID + CLIENT_VERSION + b"-" + random_string.encode()

def make_tracker_request(info_hash: bytes, port: int, peer_id: bytes, tracker_url: str, event: str ="empty"):
    """ Given a torrent info, and tracker_url, returns the tracker
    response. """

    # Generate a tracker GET request.
    payload = {"info_hash" : info_hash,
            "peer_id" : peer_id,
            "port" : port,
            "event" : event}
    payload = urlencode(payload)

    # Send the request
    response = urlopen(tracker_url + "?" + payload).read()

    return Decoder(response).decode()

def decode_expanded_peers(peers) -> list:
    """ Return a list of IPs and ports, given an expanded list of peers,
    from a tracker response. """

    return [(p[b"ip"], p[b"port"], p[b"peer id"]) for p in peers]

def generate_handshake(info_hash: bytes, peer_id: bytes) -> bytes:
    """ Returns a handshake's bytes. """

    protocol_id = b"BitTorrent protocol"
    len_id = bytes([len(protocol_id)])
    reserved = b"00000000"

    return len_id + protocol_id + reserved + info_hash + peer_id

class Torrent():
    def __init__(self, torrent_file):
        #args.seed = True # TO-DO delete this

        self.running = False

        self.data = read_torrent_file(torrent_file)

        self.info_hash = sha1(Encoder(self.data[b"info"]).encode()).digest()
        self.peer_id = generate_peer_id()
        self.handshake = generate_handshake(self.info_hash, self.peer_id)

        self.piece_length = int(self.data[b"info"][b"piece length"])
        self.num_torrent_pieces = math.ceil(int(self.data[b"info"][b"length"])/self.piece_length)
        self.torrent_pieces = [PieceInfo() for i in range(self.num_torrent_pieces)]
        
        self.torrent_donwloaded = False

        # Has file and is going to share
        if args.seed:
            with open(self.data[b"info"][b"name"].decode(),"rb") as f:
                contents = f.read()

            # Generate the pieces
            pieces = slice(contents, int(self.data[b"info"][b"piece length"]))
            for i in range(self.num_torrent_pieces):
                self.torrent_pieces[i].bytes = pieces[i]
                pieces[i] = b''
                self.torrent_pieces[i].state = PieceState.HAVE
            del pieces
            
            # All pieces have been downloaded.
            self.torrent_donwloaded = True
            
            # Log served file. Size is in file name.
            log_event(time(), ";".join(["se sirve el .torrent",torrent_file]))
        else:
            log_event(time(), ";".join(["se descarga el .torrent",torrent_file]))

    def perform_tracker_request(self, url, info_hash, peer_id, port):
        """ Make a tracker request to url, every interval seconds, using
        the info_hash and peer_id, and decode the peers on a good response. """

        while self.running:
            self.tracker_response = make_tracker_request(info_hash, port, peer_id, url)

            if b"failure reason" not in self.tracker_response:
                self.peers = decode_expanded_peers(self.tracker_response[b"peers"])
            sleep(self.tracker_response[b"interval"])

    def receive_peer_request(self):
        """ Create a socket to listen to peer request. """
        prsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        prsocket.bind((args.host,args.port))
        prsocket.listen(25)
        while self.running:
            client_sock, address = prsocket.accept()
            log_event(time(),'Accepted connection from {}:{}'.format(address[0], address[1]))
            client_handler = Thread(
                target=self.handle_peer_connection,
                args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
            )
            client_handler.start()

    def handle_peer_connection(self, client_socket: socket.socket):
        """ Comunication with peer following peer protocol"""
        try:
            request = client_socket.recv(4096)
            # TO-DO Check handshake
            client_socket.send(generate_handshake(self.info_hash, self.peer_id))
            request = client_socket.recv(4096)
            active = True
            while(active):
                if request[:1] == b'0': #choke
                    active = False
                elif request[:1] == b'1': #unchoke
                    pass                    
                elif request[:1] == b'2': #interested
                    pass
                elif request[:1] == b'3': #not interested
                    pass
                elif request[:1] == b'4': #have
                    pass
                elif request[:1] == b'5': #bitfield
                    pass
                elif request[:1] == b'6': #request
                    index = int.from_bytes(request[1:5], byteorder="big")
                    if self.torrent_pieces[index].state == PieceState.HAVE:
                        client_socket.send(b"7"+self.torrent_pieces[index].bytes) # TO-DO add begin and index
                    else:
                        client_socket.send(b"3")
                    request = client_socket.recv(4096)
                elif request[:1] == b'7': #piece
                    pass
                elif request[:1] == b'8': #cancel
                    pass
                else:
                    active = False
        except Exception as err:
            print(err)
        finally:
            client_socket.close()

    def get_torrent_file(self):
        """ Get the file in the torrent using the torrent info. """
        start_time = time()
        while not self.torrent_donwloaded:            
        
            tracker_response = make_tracker_request(self.info_hash, args.port, \
                                                    self.peer_id, self.data[b"announce"].decode(),"started")
            peers = tracker_response[b"peers"]
            peers = decode_expanded_peers(peers)
            self.active_peers = {}
            
            for peer in peers:
                if peer[2] != self.peer_id:
                    if peer[2] not in self.active_peers:
                    
                        # Handshake
                        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        peer_sock.connect((peer[0], peer[1]))
                        peer_sock.send(generate_handshake(self.info_hash, self.peer_id))
                        response = peer_sock.recv(4086) # TO-DO check hash
                        
                        self.active_peers[peer[2]] = Thread(target = self.get_pieces_from_peer, \
                                                            args = (peer_sock,))
                        self.active_peers[peer[2]].start()
            
            for key in self.active_peers:
                self.active_peers[key].join()
        log_event(time(), ";".join(["el tiempo de descarga fue",str(time()-start_time)]))
        make_tracker_request(self.info_hash, args.port, self.peer_id, self.data[b"announce"].decode(), "completed")
                
        with open(args.out_folder + "/" + self.data[b"info"][b"name"].decode(), "wb") as f:
            for piece in self.torrent_pieces:
                f.write(piece.bytes)
                
    def get_pieces_from_peer(self, peer_sock: socket.socket):
        """ Get all possible pieces from peer. """
        try:
            while not self.torrent_donwloaded:                
                for val, piece in enumerate(self.torrent_pieces):
                    if piece.state == PieceState.DONT_HAVE:
                        piece.state = PieceState.PENDING
                        peer_sock.send(b'6' + val.to_bytes(4, byteorder="big"))
                        
                        response = peer_sock.recv(self.piece_length + 4086)
                        if response[:1] == b'0': #choke
                            pass
                        elif response[:1] == b'1': #unchoke
                            pass                    
                        elif response[:1] == b'2': #interested
                            pass
                        elif response[:1] == b'3': #not interested
                            piece.state = PieceState.DONT_HAVE
                        elif response[:1] == b'4': #have
                            pass
                        elif response[:1] == b'5': #bitfield
                            pass
                        elif response[:1] == b'6': #request
                            pass
                        elif response[:1] == b'7': #piece
                            piece.bytes = response[1:]
                            piece.state = PieceState.HAVE
                        elif response[:1] == b'8': #cancel
                            pass
                        
                        self.torrent_donwloaded = self.is_torrent_downloaded()
        except Exception as err:
            print(err)
        finally:
            peer_sock.close()
            
    def is_torrent_downloaded(self) -> bool:
        """ Returns a bool indicating if download has been completed. """
        is_downloaded = True
        for piece in self.torrent_pieces:
            is_downloaded = is_downloaded and piece.state == PieceState.HAVE
        return is_downloaded
        
                            
    def run(self):
        """ Start the torrent running. """

        if not self.running:
            self.running = True

            self.tracker_loop = Thread(target = self.perform_tracker_request, \
                args = (self.data[b"announce"].decode(), self.info_hash, self.peer_id, args.port))
            self.tracker_loop.start()
            self.peer_request_loop = Thread(target=self.receive_peer_request)
            self.peer_request_loop.start()
            if not args.seed: # Client did not start as seed
                self.get_torrent_file_loop = Thread(target=self.get_torrent_file)
                self.get_torrent_file_loop.start()


    def stop(self):
        """ Stop the torrent from running. """

        if self.running:
            self.running = False

            self.tracker_loop.join()
            self.peer_request_loop.join()
            if not args.seed: # Client did not start as seed
                self.get_torrent_file_loop.join()

class PieceInfo():
    """ Information of a piece of the torrent """

    def __init__(self):

        self.bytes = b''
        self.state = PieceState.DONT_HAVE


class PieceState(Enum):
    """ Enum for state of the piece """
    DONT_HAVE = 1
    PENDING = 2
    HAVE = 3

client = Torrent(args.torrent)

def stop_exec(signum, frame):
    client.stop()
    del client
    sys.exit()

signal.signal(signal.SIGINT, stop_exec)

client.run()