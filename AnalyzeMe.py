#!/usr/bin/python

import argparse
import json
import sys
from datetime import datetime
from datetime import date
from dateutil import tz

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# print messages to file in a human-readable format
def humanReadable(args):
    data = json.load(args.data)
    for message in reversed(data):
        name = message.get('name', '')
        liked = "[<3]" if len(message["favorited_by"]) > 0 else ""
        time = datetime.fromtimestamp(message['created_at'], tz=tz.tzlocal())
        #attachment = "[" + message["attachments"][0] + "]" if len(message["attachments"]) > 0 else ""
        text = message["text"] if message["text"] != None else ""
        args.output.write("[{}/{:02d}/{:02d} {:02d}:{:02d}] {} {}: {}\n".format(time.year, time.month, time.day,time.hour, time.minute, name, liked, text))

# return a dictionary of username->number of messages
def count(data):
    counts = {}
    for message in data:
        counts[message['name']] = counts.get(message['name'], 0) + 1
    return counts

# display a the number of messages sent by each user
def cmdCount(args):
    data = json.load(args.data)
    users = count(data)
    users = dict(sorted(users.items(), key=lambda item: item[1]))
    if args.plot == 'pie':
        fig1, ax1 = plt.subplots()
        fig1.suptitle('Total Message Count')
        def pfmt(pct, values):
            return '{:.1f}% ({})'.format(pct, int(round(pct * sum(values) / 100.0)))
        wedges, texts, autotexts = ax1.pie(users.values(), labels=users.keys(),
                                           autopct=lambda pct:pfmt(pct, users.values()))
        ax1.axis('equal')
        plt.show()
    elif args.plot == 'bar':
        p = plt.bar(users.keys(), users.values())
        plt.title('Message Count')
        plt.xticks(rotation=90)
        plt.show()
    else:
        list(map(lambda u: args.output.write('{}, {}\n'.format(u, users[u])), users.keys()))
    return users

# return a dictionary of username->average message length
def messageLength(args):
    data = json.load(args.data)
    thresh = args.threshold
    lens = {}
    msgs = {}
    for message in data:
        length = len(message["text"]) \
            if 'text' in message and message['text'] != None \
            else 0
        lens[message['name']] = lens.get(message['name'], 0) + length
        msgs[message['name']] = msgs.get(message['name'], 0) + 1
    lens = dict(filter(lambda item: msgs[item[0]] > thresh, lens.items()))
    msgs = dict(filter(lambda item: item[1] > thresh, msgs.items()))
    for user in lens:
        lens[user] = lens[user] / msgs[user]
    lens = dict(sorted(lens.items(), key=lambda item: item[1]))
    if args.plot:
        p = plt.bar(lens.keys(), lens.values())
        plt.ylabel('Length in Characters')
        plt.title('Average Message Length')
        plt.xticks(rotation=90)
        plt.show()
    else:
        list(map(lambda u: args.output.write('{}, {}\n'.format(u, lens[u])), lens.keys()))
    return lens

# generate a map of username->number of attachments sent
def attachmentCount(args):
    data = json.load(args.data)
    attachments = {}
    for message in data:
        a = attachments.get(message['name'], 0)
        attachments[message['name']] = a + len(message['attachments'])
    if args.plot:
        print('no plot yet')
    else:
        list(map(lambda u: args.output.write('{}, {}\n'.format(u, attachments[u])),
                 attachments.keys()))
    return attachments

def likeCount(args):
    data = json.load(args.data)
    likes = {}
    for message in data:
        l = likes.get(message['name'], 0)
        likes[message['name']] = l + len(message['favorited_by'])
    counts = count(data)
    thresh = args.threshold
    likes = dict(filter(lambda item: counts[item[0]] > thresh, likes.items()))
    counts = dict(filter(lambda item: item[1] > thresh, counts.items()))
    if args.average:
        counts = count(data)
        for user in likes:
            likes[user] = likes[user] / counts[user]
    likes = dict(sorted(likes.items(), key=lambda item: item[1]))
    if args.plot:
        p = plt.bar(likes.keys(), likes.values())
        plt.title('Average Number of Likes' if args.average else 'Number of Likes')
        plt.xticks(rotation=90)
        plt.show()
    else:
        list(map(lambda u: args.output.write('{}, {}\n'.format(u, likes[u])),
                 likes.keys()))

# count how many messages were sent per day by each user
# produce a map date->{user->count}
def messagesPerDay(args):
    data = json.load(args.data)
    dates = {}
    for message in data:
        day = datetime.fromtimestamp(message['created_at'], tz=tz.tzlocal())
        daystring = "{}/{}/{}".format(day.month, day.day, day.year)
        if not daystring in dates: dates[daystring] = {}
        dates[daystring][message['name']] = dates[daystring].get(message['name'], 0) + 1
    if args.plot:
        print('no plot yet')
    else:
        list(map(lambda d: args.output.write('{}, {}\n'.format(d, dates[d])), dates.keys()))
    return dates

# produce a histogram of how many messages were sent by each user in each hour of the day
# returns a map of user to histogram of messages per hour
def hourHistogram(args):
    data = json.load(args.data)
    hours = {}
    for message in data:
        time = datetime.fromtimestamp(message['created_at'], tz=tz.tzlocal())
        if not message['name'] in hours:
            hours[message['name']] = [0] * 24
        hours[message['name']][time.hour] += 1
    if args.plot:
        hists = hours
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
    else:
        list(map(lambda u: args.output.write('{}, {}\n'.format(u, str(hours[u])[1:-1])), hours))
    return hours

parser = argparse.ArgumentParser(description='Analyze GroupMe conversations')

subparsers = parser.add_subparsers()

base_parser = argparse.ArgumentParser(add_help=False)
base_parser.add_argument('data', type=argparse.FileType('r'), help='/path/to/message.json')
base_parser.add_argument('--output', '-o', help='write output to a file',
                         type=argparse.FileType('w'), default=sys.stdout)

graph_parser = argparse.ArgumentParser(parents=[base_parser], add_help=False)
graph_parser.add_argument('--plot', '-p', help='plot on a graph', action='store_const', const=True)

len_parser = subparsers.add_parser('len', description='Average message length per user',
                                   parents=[graph_parser])
len_parser.add_argument('--threshold', '-t',
                        help='Only count users who sent at least n messages',
                        type=int, default=0)
len_parser.set_defaults(func=messageLength)

attachments_parser = subparsers.add_parser('attachments',
                                           description='Number of attachments per user',
                                           parents=[graph_parser])
attachments_parser.set_defaults(func=attachmentCount)

likes_parser = subparsers.add_parser('likes',
                                     description='Number of likes per user',
                                     parents=[graph_parser])
likes_parser.add_argument('--average', '-a',
                          help="display the users's average number of likes per message",
                          action='store_const', const=True)
likes_parser.add_argument('--threshold', '-t',
                          help='Only count users who sent at least n messages',
                          type=int, default=0)
likes_parser.set_defaults(func=likeCount)

count_parser = subparsers.add_parser('count',
                                     description='Number of messages per user',
                                     parents=[base_parser])
count_parser.add_argument('--plot', '-p',
                          help='plot on a bar or pie graph',
                          choices=['bar', 'pie'])
count_parser.set_defaults(func=cmdCount)

perday_parser = subparsers.add_parser('perday',
                                      description='Number of messages per day',
                                      parents=[graph_parser])
perday_parser.set_defaults(func=messagesPerDay)

perhour_parser = subparsers.add_parser('perhour',
                                       description='Aggregate number of messages per hour',
                                       parents=[graph_parser])
perhour_parser.set_defaults(func=hourHistogram)

readable_parser = subparsers.add_parser('readable',
                                        description=
                                        'Convert the data to a human-readable format',
                                        parents=[base_parser])
readable_parser.set_defaults(func=humanReadable)

args = parser.parse_args()
if len(sys.argv) < 2:
    parser.parse_args(['-h'])
args.func(args)
