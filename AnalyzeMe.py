#!/usr/bin/python

import json
import sys

# print messages to file in a human-readable format
def humanReadable(data, argv):
    outfname = argv[2] if len(argv) >=3 else 'out.txt'
    outfile = open(outfname, "w")
    for message in reversed(data):
        name = message["name"] if message["name"] != None else ""
        liked = "[<3]" if len(message["favorited_by"]) > 0 else "[  ]"
        #attachment = "[" + message["attachments"][0] + "]" if len(message["attachments"]) > 0 else ""
        text = message["text"] if message["text"] != None else ""
        outfile.write("{} {}: {}\n".format(name, liked, text))
        print("Written output to {}".format(outfname))

# return a dictionary of username->number of messages
def messageCount(data, argv):
    users = {}
    for message in data:
        users[message['name']] = users.get(message['name'], 0) + 1
    print(users)

#return a dictionary of username->average message length
def messageLength(data, argv):
    lens = {}
    msgs = {}
    for message in data:
        length = len(message["text"]) \
            if 'text' in message and message['text'] != None \
            else 0
        lens[message['name']] = lens.get(message['name'], 0) + length
        msgs[message['name']] = msgs.get(message['name'], 0) + 1
    for user in lens:
        lens[user] = lens[user] / msgs[user]
    print(lens)

def attachmentCount(data, argv):
    attachments = {}
    for message in data:
        a = attachments.get(message['name'], 0)
        attachments[message['name']] = a + len(message['attachments'])
    print(attachments)

def error(data, argv):
    print("Unrecognized command: {}".format(argv[1]))

cmds = {
    "len": (messageLength, ''),
    "attachments": (attachmentCount, ''),
    "count": (messageCount, ''),
    "readable": (humanReadable, '[outfile]'),
}

usage = "Usage: AnalyzeMe.py messagefile command [args]"

if len(sys.argv) >= 1 and (sys.argv[1] == 'help' or sys.argv[2] == 'help'):
    print(usage)
    print("Available commands: ")
    list(map(lambda k: print('  {} {}'.format(k, cmds[k][1])), cmds.keys()))

    exit(0)

if len(sys.argv) < 3:
    print(usage)
    print("Use analyzeme.py help for a list of available commands.")
    exit(1)


infile = open(sys.argv[1], "r")

data = json.load(infile)

cmds.get(sys.argv[2], error)[0](data, sys.argv)
