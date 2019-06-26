#!/usr/bin/python

import argparse
import json
import sys
from datetime import datetime
from datetime import date
from dateutil import tz

import matplotlib
matplotlib.use('gtk3agg')
import matplotlib.pyplot as plt
import numpy as np

# print messages to file in a human-readable format
def humanReadable(data, argv):
    outfname = argv[3] if len(argv) >=4 else 'out.txt'
    outfile = open(outfname, "w")
    for message in reversed(data):
        name = message["name"] if message["name"] != None else ""
        liked = "[<3]" if len(message["favorited_by"]) > 0 else ""
        time = datetime.fromtimestamp(message['created_at'], tz=tz.tzlocal())
        #attachment = "[" + message["attachments"][0] + "]" if len(message["attachments"]) > 0 else ""
        text = message["text"] if message["text"] != None else ""
        outfile.write("[{}/{:02d}/{:02d} {:02d}:{:02d}] {} {}: {}\n".format(time.year, time.month, time.day,
                                                            time.hour, time.minute, name, liked, text))
    return "Written output to {}".format(outfname)

# return a dictionary of username->number of messages
def messageCount(data, argv):
    users = {}
    for message in data:
        users[message['name']] = users.get(message['name'], 0) + 1
    return users

def messageCountPlot(data, argv):
    counts = messageCount(data, argv)
    fig1, ax1 = plt.subplots()
    fig1.suptitle('Total message count')
    def pfmt(pct, values):
        return '{:.1f}% ({})'.format(pct, int(round(pct * sum(values) / 100.0)))
    wedges, texts, autotexts = ax1.pie(counts.values(), labels=counts.keys(),
                                       autopct=lambda pct:pfmt(pct, counts.values()))
    ax1.axis('equal')
    plt.show()


# return a dictionary of username->average message length
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
    return lens

# generate a map of username->number of attachments sent
def attachmentCount(data, argv):
    attachments = {}
    for message in data:
        a = attachments.get(message['name'], 0)
        attachments[message['name']] = a + len(message['attachments'])
    return attachments

# count how many messages were sent per day by each user
# produce a map date->{user->count}
def messagesPerDay(data, argv):
    dates = {}
    for message in data:
        day = datetime.fromtimestamp(message['created_at'], tz=tz.tzlocal())
        daystring = "{}/{}/{}".format(day.month, day.day, day.year)
        if not daystring in dates: dates[daystring] = {}
        dates[daystring][message['name']] = dates[daystring].get(message['name'], 0) + 1
    return dates

# produce a histogram of how many messages were sent by each user in each hour of the day
# returns a map of user to histogram of messages per hour
def hourHistogram(data, argv):
    hours = {}
    for message in data:
        time = datetime.fromtimestamp(message['created_at'], tz=tz.tzlocal())
        if not message['name'] in hours:
            hours[message['name']] = [0] * 24
        hours[message['name']][time.hour] += 1
    return hours

def plotHourHistogram(data, argv):
    hists = hourHistogram(data, argv)
    xl = range(24)
    labels = list(map(lambda h: '{}:00'.format(h), xl))
    x = np.array(xl)
    width = 0.9

    p1 = plt.bar(x, list(hists.values())[0], width)
    p2 = plt.bar(x, list(hists.values())[1], width, bottom=list(hists.values())[0])
    plt.ylabel('Message count')
    plt.title('Message Distribution by Hour')
    plt.xticks(x, labels, rotation=90)
    plt.legend((p1[0], p2[0]), list(hists.keys()))
    plt.show()

def error(data, argv):
    return "Unrecognized command: {}".format(argv[2])

# format: 'name': (func, 'args', 'description'),
cmds = {
    'len': (messageLength, '', 'average message length per user'),
    'attachments': (attachmentCount, '', 'number of attachments per user'),
    'count': (messageCount, '', 'number of messages per user'),
    'countplot': (messageCountPlot, '', 'plot number of messages per user'),
    'readable': (humanReadable, '[outfile]', 'output in a human-readable format'),
    'perday': (messagesPerDay, '', 'number of messages per day'),
    'perhour': (hourHistogram, '', 'histogram of number of messages per hour'),
    'hourplot': (plotHourHistogram, '', 'plot per-hour histogram'),
    'list': (error, '', 'list commands'),
}

def listcmds(data, argv):
    print('Available commands:')
    list(map(lambda s: print('  {} {}: {}'.format(s, cmds[s][1], cmds[s][2])),
             cmds.keys()))

cmds['list'] = (listcmds, '', 'list commands')

usage = "Usage: AnalyzeMe.py path/to/message.json command [args]"

#if len(sys.argv) >= 1 and (sys.argv[1] == 'help' or sys.argv[2] == 'help'):
#    print(usage)
#    print("Available commands: ")
#    list(map(lambda k: print('  {} {}'.format(k, cmds[k][1])), cmds.keys()))
#
#    exit(0)


parser = argparse.ArgumentParser(description='Analyze GroupMe conversations')
parser.add_argument('data', help='/path/to/message.json', type=argparse.FileType('r'))
parser.add_argument('command', help='operation to perform')
parser.add_argument('-o', '--output', help='output file', nargs='?',
                    type=argparse.FileType('w'), default=sys.stdout)

args = parser.parse_args()

infile = args.data
#infile = open(args.data, "r")

data = json.load(infile)

print(cmds.get(args.command, (error, ''))[0](data, sys.argv))
