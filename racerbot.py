# Imports
import socket
import time
import random
import json

# Some basic variables used to configure the bot
server = "irc.freenode.net"
port = 6667
channel = "#racerbottestroom"  # test room, uncomment next line to overwrite this channel and use 'real' channel
# channel = "#hoggit.iracing"  # actual channel, uncomment this line when ready to join
botnick = "racerbot_py"
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

with open('secrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    data = json.load(jsonfile)

dictionaryApiKey = data["dictionary"]  # api key for dictionary
wolframApiKey = data["wolfram"]  # api key for wolfram alpha
youtubeApiKey = data["youtube"]  # api key for youtube

# <editor-fold desc="Basic Functions">


def joinchan(chan):  # joins channels
    ircsock.send("JOIN " + chan +"\n")
    print "Joining " + chan


def ping():  # responds to pings from server
    ircsock.send("PONG :Pong\n")
    print "PONG!"


def sendmsg(message):  # function to send message, a little easier than typing ircsocket over and over
    now = time.strftime("%I:%M:%S")
    ircsock.send('PRIVMSG %s :%s\n' % (channel, message))
    print "%s: I sent: %s" % (now, message)
# </editor-fold desc="Basic Functions">

# </editor-fold desc="Commands">


def commands(nick, channel, message):
    random.seed(time.time())
    randomInt = random.randint(0, 30)
    if randomInt == 30:
        pass
    if message.find(".here") != -1:  # checks if bot is listening to us
        sendmsg("Yup!")


def dickify(word):
    return "test"

# </editor-fold desc="Commands">


# <editor-fold desc="Bot">
# setting up socket
ircsock.connect((server, port))  # Connect to the server using provided port
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " Created by racer0940\n")  # user authentication
print "Authenticating"
ircsock.send("NICK " + botnick + "\n")  # assign the nick to the bot
print "Assigning name"

joinchan(channel)  # initial channel join

while True:  # this is the actual bot itself, everything in this block is what the bot uses
    ircmsg = ircsock.recv(2048)  # receive data from server
    ircmsg = ircmsg.strip('\n\r')  # strip any unnecessary line breaks
    now = time.strftime("%I:%M:%S")
    print(now + " - " + ircmsg)  # print message to console

    if ircmsg.find("PING :") != -1:  # don't want to be rude, respond to servers pings
        ping()

    if ircmsg.find(' PRIVMSG '):
        nick = ircmsg.split('!')[0][1:]
        channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
        message = ircmsg.split(' :')[-1]

        commands(nick, channel, message)

# </editor-fold desc="Bot">
