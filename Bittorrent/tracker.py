# pytorrent-tracker.py
# A bittorrent tracker
#    Written by Joe Salisbury <salisbury.joseph@gmail.com>
#    Extended by Fernando Reyes Bejarano
#
#    You are free to use this code in anyway you see fit, on the basis
#    that if it is used, modified, or distributed, proper accreditation
#    of the original author remains.

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from logging import basicConfig, info, INFO
from socket import inet_aton
from struct import pack
from urllib.request import urlopen
from urllib.parse import parse_qs
import time
import argparse
import signal
import sys
import os
import errno

from bencode import Encoder

#Arguments for the tracker
parser = argparse.ArgumentParser(description='Bittorrent Tracker')

parser.add_argument('--host', type=str,
                    help='hostname of the tracker')

parser.add_argument('--port',
                    help='port of the tracker')

parser.add_argument('--out', default='test_tracker.log',
                    help='output file for the log')

parser.add_argument('--out_folder', default='test', type=str,
                    help='output file name for the log')

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
    fl.write(time.strftime('%c') + "\n")
    fl.write('Listening on {}:{}'.format(args.host, args.port) + "\n")
    fl.write('-'*17 + "\n")

def log_event(time, message):
    """ Function that writes on the log file """
    with open(args.out_folder + "/" + args.out, 'a') as fl:
        fl.write('execution time: {} s'.format(time) + "\n")
        fl.write(message + "\n")
        fl.write('-'*17 + "\n")

def decode_request(path):
    """ Return the decoded request string. """

    # Strip off the start characters
    if path[:1] == "?":
        path = path[1:]
    elif path[:2] == "/?":
        path = path[2:]

    return parse_qs(path, keep_blank_values=True)

def add_peer(torrents, info_hash, peer_id, ip, port, event):
    """ Add the peer to the torrent database. """
    
    # If we've heard of this, just add the peer
    if info_hash in torrents:
         # Only add the peer if they're not already in the database
        if (peer_id, ip, port) not in torrents[info_hash]:
            torrents[info_hash].append((peer_id, ip, port))
    # Otherwise, add the info_hash and the peer
    else:
        torrents[info_hash] = [(peer_id, ip, port)]
    # If download has finished or started log the time.
    if event:
        if event == "started":
            torrents[peer_id] = time.time()
            log_event(time.time(),";".join([peer_id,"la descarga inicia"]))
        elif event == "completed":
            log_event(time.time(),";".join([peer_id,"el tiempo de descarga fue",str(time.time()-torrents[peer_id])]))
        else:
            log_event(time.time(),";".join([peer_id,"contacto de"]))


def make_peer_list(peer_list):
    """ Return an expanded peer list suitable for the client, given
    the peer list. """

    peers = []
    for peer in peer_list:
        p = {}
        p["peer id"] = peer[0]
        p["ip"] = peer[1]
        p["port"] = int(peer[2])

        peers.append(p)

    return peers

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """ Take a request, do some some database work, return a peer
        list response. """

        # Decode the request
        package = decode_request(self.path)

        if not package:
            self.send_error(403)
            return

        # Get the necessary info out of the request
        info_hash = package["info_hash"][0]
        ip = self.client_address[0]
        port = package["port"][0]
        peer_id = package["peer_id"][0]
        event = package["event"][0]

        add_peer(self.server.torrents, info_hash, peer_id, ip, port, event)

        # Generate a response
        response = {}
        response["interval"] = self.server.interval
        response["peers"] = make_peer_list( \
        self.server.torrents[info_hash])

        # Send off the response
        self.send_response(200)
        self.end_headers()
        #self.wfile.write(str(response).encode())
        self.wfile.write(Encoder(response).encode())


    def log_message(self, format, *args):
        """ Just supress logging. """

        return

class Tracker():
    def __init__(self, host = "", port = 9010, interval = 5, \
        torrent_db = "tracker.db", \
        inmemory = True):
        """ Read in the initial values, load the database. """
        if args.host:
            self.host = args.host
        else:
            self.host = host
        
        if args.port:
            self.port = args.port
        else:
            self.port = port

        self.server_class = HTTPServer
        self.httpd = self.server_class((self.host, self.port), \
            RequestHandler)

        self.running = False    # We're not running to begin with

        self.server_class.interval = interval

        # The database will stay in memory
        self.server_class.torrents = {}

    def runner(self):
        """ Keep handling requests, until told to stop. """

        while self.running:
            self.httpd.handle_request()

    def run(self):
        """ Start the runner, in a seperate thread. """

        if not self.running:
            self.running = True

            self.thread = Thread(target = self.runner)
            self.thread.start()

    def send_dummy_request(self):
        """ Send a dummy request to the server. """

        # To finish off httpd.handle_request()
        address = "http://127.0.0.1:" + str(self.port)
        try:
           urlopen(address)
        #except HTTPError:
        #    pass
        except Exception as inst:
            print(type(inst))
    def stop(self):
        """ Stop the thread, and join to it. """

        if self.running:
            self.running = False
            self.send_dummy_request()
            self.thread.join()

    def __del__(self):
        """ Stop the tracker thread, write the database. """

        self.stop()
        self.httpd.server_close()

tracker = Tracker()

def stop_exec(signum, frame):
    del tracker
    sys.exit()

signal.signal(signal.SIGINT, stop_exec)

tracker.run()