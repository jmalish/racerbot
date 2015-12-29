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
from bs4 import BeautifulSoup
import urllib
import xml.etree.ElementTree as Etree
import cleverbot
import twitch

# <editor-fold desc="Variables">
# Some basic variables used to configure the bot
server = "irc.freenode.net"     # irc server
port = 6667                     # irc port
channel = "#hoggit.iracing"  # actual channel, uncomment this line when ready to join
# channel = "#racerbot.testroom"  # test room, uncomment next line to overwrite this channel and use 'real' channel
botnick = "racerbot_py"  # bot name
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# API Key variables
with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    secrets = json.load(jsonfile)

wolfram_api_key = secrets["wolfram"]         # api key for wolfram alpha
youtubeApiKey = secrets["youtubeKey"]         # api key for youtube

# other variables
joined = False      # tells us if bot has successfully joined, keeps from sending messages if not joined to channel
reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW
clever = cleverbot.Cleverbot()  # cleverbot setup
twitch.twitch_initial()  # twitch setup
print "Initial setup done"

# </editor-fold desc="Variables">
# <editor-fold desc="Basic Functions">


def joinchan(chan):  # joins channels
    ircsock.send("JOIN " + chan + "\n")
    print "Joining " + chan


def ping():  # responds to pings from server
    ircsock.send("PONG :Pong\n")
    print "PONG!"


def sendmsg(message):  # function to send message, a little easier than typing ircsocket over and over
    now = time.strftime("%I:%M:%S")
    ircsock.send('PRIVMSG %s :%s\n' % (channel, message))
    print "%s: I sent: %s to %s" % (now, message, channel)


def get_page_title(site):  # takes what we thinks might be a url and tries to get the page title
    try:
        if "http" not in site:
            site = "http://" + site  # requests needs the link to have http in front of it

        r = requests.get(site, headers={'user-agent': 'roboracer'})
        if r.status_code == 200:
            html = BeautifulSoup(r.text, "html.parser")
            return html.title.text.encode('utf-8').strip()
        else:
            print "Unable to reach " + site + ": " + r.status_code
            pass  # we got a 404 page or something
    except ConnectionError:
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


def query_wolfram_alpha(query):
    query = urllib.quote(query)  # convert string to url safe string
    try:
        api_url = "http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext" % \
                  (wolfram_api_key, query)
        wolfram_response = requests.get(api_url).text.encode('utf-8').strip()

        root = Etree.fromstring(wolfram_response)

        if root.attrib["success"]:
            if int(root.attrib["numpods"]) > 0:  # make sure the query actually has something to show
                # get all the stuff we want
                wolfram_input_title = root[0].attrib["title"]
                wolfram_input_text = root[0][0][0].text
                wolfram_output_title = root[1].attrib["title"]
                wolfram_output_text = root[1][0][0].text
                # put all that stuff into a json string
                wolfram_json = json.dumps({"input_title": wolfram_input_title,
                                           "input_text": wolfram_input_text,
                                           "output_title": wolfram_output_title,
                                           "output_text": wolfram_output_text.encode('utf-8'),
                                           "isSuggestion": False,
                                           "message": None})
                return wolfram_json
            else:  # if not, give user wolfram's suggestion
                wolfram_json = json.dumps({"suggestion": str(root[0][0].text),
                                           "isSuggestion": True,
                                           "message": None})
                return wolfram_json
        else:
            wolfram_json = json.dumps({"isSuggestion": False,
                                       "message": "I don't even know how you got this message, I'm impressed"})
        return wolfram_json
    except Exception, e:
        print e
        wolfram_json = json.dumps({"isSuggestion": False,
                                   "message": "You broke Wolfram, way to go... jerk"})
        return wolfram_json
# </editor-fold desc="Basic Functions">
# </editor-fold desc="Commands">


def commands(ircmessage):
    try:
        if not joined:  # there are a few things we don't want to do until joined
            print ircmessage
        else:
            now = time.strftime("%I:%M:%S")
            nick = ircmessage.split("!")[0].strip(":")
            message = ircmessage.split(channel + " :")[1]

            print "%s - %s: %s" % (now, nick, message)

            try:
                # this block is all the "dot" commands, where something is requested from the bot by a user
                if message.lower().startswith(".here"):  # checks if bot is listening to us
                    sendmsg("Yup!")
                elif message.lower().startswith(".source"):
                    sendmsg("https://github.com/jmalish/racerbot")
                elif message.lower().startswith(".help"):
                    sendmsg("https://github.com/jmalish/racerbot/blob/master/commands_list.txt")
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
                    sendmsg("You got it, I'll put %s all over everything now" % fishify.fishWord)
                elif message.lower().startswith(".calc"):  # ~~~~~~~~~~ WOLFRAM
                    to_send = message.split(".calc")
                    wolfram_results = json.loads(query_wolfram_alpha(to_send[1]))
                    if wolfram_results["isSuggestion"]:  # whatever was sent didn't work
                        sendmsg("WA says that's not a thing, it suggests: %s" % wolfram_results["suggestion"])
                    elif wolfram_results["message"] is None:
                        sendmsg("%s: %s" % (wolfram_results["input_title"], wolfram_results["input_text"]))
                        sendmsg("%s: %s" % (wolfram_results["output_title"], wolfram_results["output_text"]))
                    else:
                        sendmsg(wolfram_results["message"])
                elif message.startswith(".chat"):
                    to_send = message.split(".chat")
                    sendmsg((clever.ask(to_send[1].strip())))
                elif message.lower().startswith(".livestreams"):
                    twitch.update_stream_statuses()
                    if len(twitch.online_channels) > 0:
                        for tw_channel in twitch.online_channels:
                            stream_info = json.loads(twitch.get_channel_info(tw_channel))
                            sendmsg("www.twitch.tv/%s is streaming %s | Title: %s" %
                                    (stream_info["display_name"], stream_info["game"], stream_info["status"]))
                    else:
                        sendmsg("No one's streaming!")
                elif message.lower().startswith(".offlinestreams"):
                    if len(twitch.offline_channels) > 0:
                        channels = ""
                        for tw_channel in twitch.offline_channels:
                            channels += tw_channel + ", "
                        sendmsg(channels.rstrip().rstrip(','))
                    else:
                        sendmsg("There are no offline channels.")
                elif message.lower().startswith(".allstreams"):
                    if twitch.get_all_channels() == 0:
                        sendmsg("I don't have any streamers in my list! Add some with '.addstream <channel name>")
                    else:
                        channels = ""
                        for tw_channel in twitch.get_all_channels():
                            channels += tw_channel + ", "
                        sendmsg(channels.rstrip().rstrip(','))
                elif message.lower().startswith(".addstream"):
                    channel_to_add = message.split(".addstream ")
                    sendmsg(twitch.add_new_channel(channel_to_add[1]))
                elif message.lower().startswith(".removestream"):
                    channel_to_remove = message.split(".removestream ")
                    sendmsg(twitch.remove_channel(channel_to_remove[1]))
                elif message.lower().startswith(".timesincetwitch"):
                    sendmsg(twitch.time_since_update())
                else:  # if no commands are called, then we'll do some fun stuff
                    # fishify stuff
                    random.seed(time.time())
                    randomInt = random.randint(0, 30)
                    # fishify stuff
                    if randomInt == 30:  # I want this to be separate so the bot doesn't stop looking for commands here
                        if fishify.timerCheck():
                            try:
                                sendmsg(fishify.fish(message, True))  # send the chosen word to fishify()
                            except Exception, e:
                                print "Error in random fishify:"
                                print e

                    # twitch stuff
                    now_streaming = twitch.timer_check()  # check for twitch updates
                    if len(now_streaming) > 0:  # if this has anything in it, someone's started streaming
                        print "people started streaming~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                        for tw_channel in now_streaming:
                            print tw_channel
                            stream_info = json.loads(twitch.get_channel_info(tw_channel))
                            sendmsg("www.twitch.tv/%s has started streaming %s | Title: %s" %
                                    (stream_info["display_name"], stream_info["game"], stream_info["status"]))
            except Exception, e:
                print "Something went wrong in dot commands:"
                print e

            # ~~~~~~~~ REDDIT
            try:
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
                                sendmsg("http://www.reddit.com/r/%s - %s" % (subreddit_name, subreddit_title))
                            except Exception as e:
                                sendmsg("http://www.reddit.com/r/" + subreddit_name + " - That's not a real subreddit...")
                                print e
            except Exception, e:
                print "Something went wrong in reddit block:"
                print e

            # ~~~~~~~~ WEBSITE TITLES
            try:
                # search for websites
                url_regex = re.findall("(www.)?[a-zA-Z0-9\-]+\.[a-z]{2,3}", message, flags=re.IGNORECASE)
                # here, we're just seeing if the message even contains a url, not concerned with whole url yet
                if url_regex:  # if this is true, the message has a url in it
                    for word in message.split():
                        word = word.strip(',').strip('.')  # get rid of trailing commas or periods (ie end of sentence)
                        if ("reddit" in word) or ("twitch" in word) or ("youtube" in word)\
                                or ("youtu.be" in word) or ("freenode" in word):
                            # reddit, twitch, and youtube stuff is already being taken care of
                            # no need to get it here
                            # freenode server pings bot every so often, he really wants to get the title of those too
                            pass
                        elif "." in word:  # look for 'words' with a '.' in the middle
                            if "@" not in word:  # ignore emails
                                title = get_page_title(word)
                                if title:
                                    sendmsg(title)
            except Exception, e:
                print "Something went wrong in website title:"
                print e

            # ~~~~~~~~ YOUTUBE
            try:
                # regex to get youtube ID, this might need to be cleaned up
                # will not see links that have an argument before the video id argument (ie ?t=)
                regex_youtube = re.findall("youtu\.?be(.com)?/?(watch\?v=)?([_a-zA-Z0-9\-]{11})", message, flags=re.IGNORECASE)
                if regex_youtube:  # if we find a youtube link
                    for id in regex_youtube:  # foreach youtube link in message
                        sendmsg(get_yt_video_info(id[2]))  # pass the video ID to function
            except Exception, e:
                print "Something went wrong in youtube:"
                print e

            # ~~~~~~~~~~~ TWITCH
            try:
                # regex to find twitch channel info
                twitch_regex = re.findall("twitch.tv\/([a-zA-Z0-9\_\+]+)", message, flags=re.IGNORECASE)

                if twitch_regex:
                    for username in twitch_regex:  # for each username in the message
                        channel_info = json.loads(twitch.get_channel_info(username))

                        if channel_info:  # if the channel is live, send stream info
                            if channel_info["viewer_count"] == 1:
                                sendmsg("%s is streaming %s | Title: %s | %s viewer" %
                                        (channel_info["display_name"],
                                         channel_info["game"],
                                         channel_info["status"],
                                         channel_info["viewer_count"]
                                         ))
                            else:
                                sendmsg("%s is streaming %s | Title: %s | %s viewers" %
                                        (channel_info["display_name"],
                                         channel_info["game"],
                                         channel_info["status"],
                                         channel_info["viewer_count"]
                                         ))
            except Exception, e:
                print "Something went wrong in twitch in racerbot"
                print e

            # end of "if joined:"
    except Exception, e:
        print "Error in commands():"
        print e

# </editor-fold desc="Commands">
# <editor-fold desc="Bot">
# setting up socket
print "Attempting to connect to server"
ircsock.connect((server, port))  # Connect to the server using provided port
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " Created by racer0940\n")  # user authentication
print "Authenticating"
ircsock.send("NICK " + botnick + "\n")  # assign the nick to the bot
print "Assigning name"

joinchan(channel)  # initial channel join

while True:  # this is the actual bot itself, everything in this block is what the bot uses
    ircmsg = ircsock.recv(2048)  # receive data from server
    ircmsg = ircmsg.strip('\n\r')  # strip any unnecessary line breaks
    # print(now + " - " + ircmsg)  # print message to console

    # not sure if making this an if/elif block is a good idea, time will tell I suppose
    if ircmsg.find("PING :") != -1:  # don't want to be rude, respond to servers pings
        print ircmsg
        ping()
    elif "/NAMES" in ircmsg:
        print "~~~~~~~~~~~~~~~~~~~~~~~ I'm in! ~~~~~~~~~~~~~~~~~~~~~~~"
        joined = True  # we've joined the channel
        fishify.fishClock = calendar.timegm(time.gmtime()) - 300
        twitch.joined = True
    elif ircmsg.find(' PRIVMSG '):
        commands(ircmsg)
# </editor-fold desc="Bot">
