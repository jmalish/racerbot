# Imports
import socket
import time
import calendar
import random
import json
import fishify
import re
import praw
import requests
from bs4 import BeautifulSoup as Bs

# <editor-fold desc="Variables">
# Some basic variables used to configure the bot
server = "irc.freenode.net"     # irc server
port = 6667                     # irc port
channel = "#racerbottestroom"  # test room, uncomment next line to overwrite this channel and use 'real' channel
# channel = "#hoggit.iracing"  # actual channel, uncomment this line when ready to join
botnick = "racerbot_py"
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# API Key variables
with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    data = json.load(jsonfile)

wolframApiKey = data["wolfram"]         # api key for wolfram alpha
youtubeApiKey = data["youtube"]         # api key for youtube

# other variables
joined = False      # tells us if bot has successfully joined, keeps from sending messages if not joined to channel
reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW

# </editor-fold desc="Variables">
# <editor-fold desc="Basic Functions">


def joinchan(chan):  # joins channels
    ircsock.send("JOIN " + chan + "\n")
    print "Joining " + chan
    global joined
    joined = True


def ping():  # responds to pings from server
    ircsock.send("PONG :Pong\n")
    print "PONG!"


def sendmsg(message):  # function to send message, a little easier than typing ircsocket over and over
    now = time.strftime("%I:%M:%S")
    ircsock.send('PRIVMSG %s :%s\n' % (channel, message))
    print "%s: I sent: %s" % (now, message)


def get_page_title(site):  # TODO: Make this use GETs instead of POST
    try:
        r = requests.get(site, headers={'user-agent': 'roboracer'})
        html = Bs(r.text, "html.parser")
        return html.title.text
    except Exception:
        pass  # do nothing, it's probably a fake website
# </editor-fold desc="Basic Functions">
# </editor-fold desc="Commands">


def commands(nick, channel, message):
    random.seed(time.time())
    randomInt = random.randint(0, 30)
    if joined:  # no reason to fishify stuff if we haven't even joined yet
        if randomInt == 30:  # I want this to be separate so the bot doesn't stop looking for commands here
            if fishify.timerCheck():
                try:
                    sendmsg(fishify.fish(message, True))  # send the chosen word to fishify()
                except Exception as e:
                    print "Error in random fishify: " + e

    # this block is all the "dot" commands, where something is requested from the bot by a user
    if message.lower().find(".here") != -1:  # checks if bot is listening to us
        sendmsg("Yup!")
    elif message.lower().startswith(".fishify"):
        sendmsg(fishify.fish(message, False))
    elif message.lower().startswith(".setfishtimer"):
        sendmsg(fishify.setTimer(message.split()[1]))
    elif message.lower().startswith(".getfishtimer"):
        sendmsg(fishify.getTimer())
    elif message.lower().startswith(".timesincefish"):
        sendmsg(fishify.timeSinceFish())
    elif message.lower().startswith(".setfishify"):
        fishify.fishWord = message.split()[1]

    # search for subreddits (r/example)
    subreddit_regex = re.findall("r/([a-z0-9]+)(/comments/([a-z0-9_]+))?", message, flags=re.IGNORECASE)
    if subreddit_regex:  # if this is true, we found a subreddit name
        for result in subreddit_regex:
            if result[1]:  # if result[1] has something in it, that means we have a comments link
                thread_id = result[2]  # get thread ID from regex group 3
                try:
                    thread_info = reddit.get_submission(submission_id=thread_id)
                    sendmsg(str(thread_info.title) + " | " + str(thread_info.subreddit))
                except Exception as e:
                    print e
            else:  # if not, it's just a subreddit
                subreddit_name = result[0]  # get subreddit name from regex group 1
                try:
                    subreddit_title = reddit.get_subreddit(subreddit_name).title
                    print ("http://www.reddit.com/r/" + subreddit_name + " - " + subreddit_title)
                except Exception as e:
                    sendmsg("http://www.reddit.com/r/" + subreddit_name + " - That's not a real subreddit...")
                    print e

    if message.find("www.") | message.find("http://"):
        for word in message.split():
            if "http" in word:
                sendmsg(get_page_title(word))
            elif "www." in word:
                sendmsg(get_page_title("http://" + word))
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

    if "End of /NAMES list." in ircmsg:
        global joined
        joined = True  # we've joined the channel
        print "I'm in!"
        fishify.fishClock = calendar.timegm(time.gmtime()) - 300

    if ircmsg.find(' PRIVMSG '):
        nick = ircmsg.split('!')[0][1:]
        channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
        message = ircmsg.split(' :')[-1]

        commands(nick, channel, message)
# </editor-fold desc="Bot">
