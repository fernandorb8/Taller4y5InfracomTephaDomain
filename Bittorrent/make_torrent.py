# torrent.py
# Torrent file related utilities
#    Written by Joe Salisbury <salisbury.joseph@gmail.com>
#    Extended by Fernando Reyes Bejarano
#
#    You are free to use this code in anyway you see fit, on the basis
#    that if it is used, modified, or distributed, proper accreditation
#    of the original author remains.

from hashlib import md5, sha1
from util import collapse, slice
import argparse
from time import time

from bencode import Encoder

#Arguments for the tracker
parser = argparse.ArgumentParser(description='Bittorrent client')

parser.add_argument('--torrent', type=str, default="test.torrent",
                    help='torrent file name with .torrent extension')

parser.add_argument('--tracker', type=str, default="http://127.0.0.1:9010",
                    help='url of the tracker')

parser.add_argument('--comment', type=str,
                    help='comment for the .torrent file')

parser.add_argument('--file', type=str, default="test.txt",
                    help='file name for the torrent')

parser.add_argument('--piece_length', type=int, default=2**20,
                    help='number of bytes per piece of torrent')

args = parser.parse_args()

CLIENT_NAME = b"pytorrent"

def write_torrent_file(torrent = None, file = None, tracker = None, \
    comment = None):
    """ Largely the same as make_torrent_file(), except write the file
    to the file named in torrent. """

    if not torrent:
        raise TypeError("write_torrent_file() requires a torrent filename to write to.")

    data = make_torrent_file(file = file, tracker = tracker, \
        comment = comment)
    with open(torrent, "wb") as torrent_file:
        torrent_file.write(data)

def make_torrent_file(file = None, tracker = None, comment = None):
    """ Returns the bencoded contents of a torrent file. """

    if not file:
        raise TypeError("make_torrent_file requires at least one file, non given.")
    if not tracker:
        raise TypeError("make_torrent_file requires at least one tracker, non given.")

    torrent = {}

    # We only have one tracker, so that's the announce
    if type(tracker) != list:
        torrent["announce"] = tracker
    # Multiple trackers, first is announce, and all go in announce-list
    elif type(tracker) == list:
        torrent["announce"] = tracker[0]
        # And for some reason, each needs its own list
        torrent["announce-list"] = [[t] for t in tracker]

    torrent["creation date"] = int(time())
    torrent["created by"] = CLIENT_NAME
    if comment:
        torrent["comment"] = comment

    torrent["info"] = make_info_dict(file)

    return Encoder(torrent).encode()

def make_info_dict(file):
    """ Returns the info dictionary for a torrent file. """

    with open(file,"rb") as f:
        contents = f.read()

    piece_length = args.piece_length    # TODO: This should change dependent on file size

    info = {}

    info["piece length"] = piece_length
    info["length"] = len(contents)
    info["name"] = file
    info["md5sum"] = md5(contents).hexdigest()

    # Generate the pieces
    pieces = slice(contents, piece_length)
    pieces = [ sha1(p).digest() for p in pieces ]
    info["pieces"] = collapse(pieces)
    return info



write_torrent_file(args.torrent, args.file, args.tracker, args.comment)