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
from requests.exceptions import ConnectionError
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
    secrets = json.load(jsonfile)

wolframApiKey = secrets["wolfram"]         # api key for wolfram alpha
youtubeApiKey = secrets["youtube"]         # api key for youtube

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


def get_page_title(site):  # takes what we thinks might be a url and tries to get the page title
    try:
        if "http" not in site:
            site = "http://" + site  # requests needs the link to have http in front of it

        r = requests.get(site, headers={'user-agent': 'roboracer'})
        if r.status_code == 200:
            html = Bs(r.text, "html.parser")
            return html.title.text.encode('utf-8').strip()
        else:
            print "Unable to reach " + site + ": " + r.status_code
            pass  # we got a 404 page or something
    except ConnectionError as c:
        print "Connection Error: " + site
        return False
    except Exception, e:
        print e
        return False


def get_yt_video_info(video_id):  # get video info of youtube video
    try:
        # URL to get info for video
        api_url = "https://www.googleapis.com/youtube/v3/videos?id=" + video_id + \
                  "&key=" + youtubeApiKey + "%20&part=snippet,statistics"
        video_details = requests.get(api_url)  # retrieve the JSON from Google's API
        vid_title = video_details.json()["items"][0]["snippet"]["title"]  # get title of video
        vid_channel = video_details.json()["items"][0]["snippet"]["channelTitle"]  # get channel of video
        vid_view_count = video_details.json()["items"][0]["statistics"]["viewCount"]  # get view count of video
        return "Title: %s | Views: %s | Channel: %s" % (vid_title, vid_view_count, vid_channel)
    except Exception, e:
        print e
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
                except Exception, e:
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

    # ~~~~~~~~ REDDIT
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

    # ~~~~~~~~ WEBSITE TITLES
    # search for websites
    url_regex = re.findall("(www.)?[a-zA-Z0-9\-]+\.[a-z]{2,3}", message, flags=re.IGNORECASE)
    # here, we're just seeing if the message even contains a url, not concerned with whole url yet
    if url_regex:  # if this is true, the message has a url in it
        for word in message.split():
            word = word.strip(',').strip('.')  # get rid of trailing commas or periods (ie end of sentence)
            if ("reddit" in word) or ("twitch" in word):
                # reddit and twitch stuff is already being taken care of
                # no need to get it here
                pass
            elif "." in word:  # look for 'words' with a '.' in the middle
                if "@" not in word:  # ignore emails
                    title = get_page_title(word)
                    if title:
                        sendmsg(title)

    # ~~~~~~~~ YOUTUBE
    # regex to get youtube ID, this might need to be cleaned up
    # will not see links that have an argument before the video id argument (ie ?t=)
    regex_youtube = re.findall("youtu\.?be(.com)?/?(watch\?v=)?([a-zA-Z0-9\-]+)", message, flags=re.IGNORECASE)
    if regex_youtube:  # if we find a youtube link
        for id in regex_youtube:  # foreach youtube link in message
            sendmsg(get_yt_video_info(id[2]))  # pass the video ID to function

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
