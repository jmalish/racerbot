# Imports
import socket
import time
import calendar
import random
import json
import urllib
import xml.etree.ElementTree as ET
import sys

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

dictionaryApiKey = data["dictionary"]   # api key for dictionary
wolframApiKey = data["wolfram"]         # api key for wolfram alpha
youtubeApiKey = data["youtube"]         # api key for youtube

# other variables
joined = False      # tells us if bot has successfully joined, keeps from sending messages if not joined to channel
fish = "fish"       # used in fishify()
fishTimer = 300     # used to keep fishify from running every other message (default is 5 min)
fishClock = 000     # used to see how long it's been since last fishify

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
# </editor-fold desc="Basic Functions">
# </editor-fold desc="Commands">


def commands(nick, channel, message):
    global fish
    global fishTimer
    global fishClock

    random.seed(time.time())
    randomInt = random.randint(0, 30)
    if joined:  # no reason to fishify stuff if we haven't even joined yet
        if randomInt == 30:  # I want this to be separate so the bot doesn't stop looking for commands here
            timeNow = calendar.timegm(time.gmtime())
            if (timeNow - fishClock) > fishTimer:
                try:
                    fishify(message)  # send the chosen word to fishify()
                    # get current time, if the fishify was successful, this says when the last time it was run
                    fishClock = calendar.timegm(time.gmtime())
                except Exception as e:
                    print "Error in random fishify: " + e.message

    if message.lower().find(".here") != -1:  # checks if bot is listening to us
        sendmsg("Yup!")
    elif message.lower().startswith(".fishify"):
        fishify(message)
    elif message.lower().startswith(".setfishtimer"):
        try:
            fishTimer = int(message.split()[1]) * 60
            sendmsg("Fish timer now set to " + str(fishTimer/60) + " minutes")
        except Exception as e:
            sendmsg("Whoa there, what kinda number is that?!")
            print e.message
    elif message.lower().startswith(".getfishtimer"):
        sendmsg("Fish timer is set at " + str(fishTimer/60) + " minutes")
    elif message.lower().startswith(".timesincefish"):
        timeNow = calendar.timegm(time.gmtime())
        timeSinceFish = (timeNow - fishClock)  # get seconds since fish

        m, s = divmod(timeSinceFish, 60)  # < this converts seconds
        h, m = divmod(m, 60)              # < to HH:MM:SS form
        sendmsg("Time since last fishing: %d:%02d:%02d" % (h, m, s))
    elif message.lower().startswith(".setfishify"):
        fish = message.split()[1]


def fishify(sentence):  # takes a word and changes the syllable to a given word
    for i in range(0, 5):  # let the bot try five times to find a word, this is so it doesn't give up on first try
        try:
            words = sentence.split()  # get number of words by splitting on spaces

            random.seed(time.time())  # set seed for random
            randomIntWord = random.randint(1, len(words) - 1)  # generate a random integer to select word
            chosenWord = words[randomIntWord]  # get the word that correlates to the random integer (location in array)
            print ("I chose '" + chosenWord + "' to fishify")

            dictLink = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/" + \
                       chosenWord + "?key=" + dictionaryApiKey

            tree = ET.parse(urllib.urlopen(dictLink))
            root = tree.getroot()

            syllables = root[0].find("hw").text.split('*')  # split word into syllables
            randomIntSyl = random.randint(0, len(syllables) - 1)  # generate a random integer to select syllable

            syllables[randomIntSyl] = fish  # replace syllable with fishify word

            newWord = ""
            for i in range(len(syllables)):
                newWord += syllables[i]

            words[randomIntWord] = newWord

            newSentence = ""
            for i in range(len(words)):
                if words[i] == ".fishify":
                    pass  # if the first word is the command to fishify, we don't want to add it to the sentence
                else:
                    newSentence += words[i] + " "

            sendmsg(newSentence)
            break
        except Exception as e:  # catch if the selected word doesn't exist in the dictionary
            i += 1
            if i == 5:
                # if it tried all five times and failed, tell chat what happened
                sendmsg("I'm pretty sure none of those are words... I looked in the dictionary and everything!")
                print "Error in fishify(): " + e.message

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
        global fishClock
        fishClock = calendar.timegm(time.gmtime()) - 300

    if ircmsg.find(' PRIVMSG '):
        nick = ircmsg.split('!')[0][1:]
        channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
        message = ircmsg.split(' :')[-1]

        commands(nick, channel, message)
# </editor-fold desc="Bot">
