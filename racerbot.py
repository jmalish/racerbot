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
import irc_quotes
import traceback
import fish_facts

# <editor-fold desc="Variables">
# Some basic variables used to configure the bot
server = "irc.freenode.net"     # irc server
port = 6667                     # irc port
channel = "#hoggit.iracing"     # channel for bot to join
botnick = "racerbot_py"         # bots name in channel
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user_list = []  # contains list of all users in channel (includes ops)
ops_list = []  # contains list of all ops in channel

# testing
testing = False
if testing:
    channel = "#racerbottestroom"
    botnick = "racerbot_py2"

log_file_name = channel + ".log"  # file name for logging (placed here so it creates one for testing room too)

# API Key variables
with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    secrets = json.load(jsonfile)

wolfram_api_key = secrets["wolfram"]    # api key for wolfram alpha
youtubeApiKey = secrets["youtubeKey"]   # api key for youtube

# other variables
joined = False      # tells us if bot has successfully joined, keeps from sending messages if not joined to channel
reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW
clever = cleverbot.Cleverbot()  # cleverbot setup
fish_chance = 30
twitch.twitch_initial()  # twitch setup
print "Initial setup done"

# </editor-fold desc="Variables">
# <editor-fold desc="Basic Functions">


def join_chan(chan):  # joins channels
    ircsock.send("JOIN " + chan + "\n")
    print "Joining " + chan


def ping():  # responds to pings from server
    ircsock.send("PONG :Pong\n")
    print "PONG!"


def send_message(message):  # function to send message, a little easier than typing ircsocket over and over
    message = message.encode('utf-8')
    now = time.strftime("%I:%M:%S")
    ircsock.send('PRIVMSG %s :%s\n' % (channel, message))
    print "%s: I sent: %s to %s" % (now, message, channel)
    irc_quotes.add_last_message(botnick, message)  # add bots message to last messages table


def private_message(message, user):  # function to send message, a little easier than typing ircsocket over and over
    message = message.encode('utf-8')
    now = time.strftime("%I:%M:%S")
    ircsock.send('PRIVMSG %s :%s\n' % (user, message))
    print "%s: I sent: %s to %s" % (now, message, user)


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
    except Exception, error:
        print error
        return False


def twitch_check():  # check for twitch updates
    if joined:
        try:
            now_streaming = twitch.timer_check()  # check for twitch updates
            if len(now_streaming):  # if this has anything in it, someone's started streaming
                print "people started streaming~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                for tw_channel in now_streaming:
                    print tw_channel
                    stream_info = json.loads(twitch.get_channel_info(tw_channel))
                    send_message("www.twitch.tv/%s has started streaming %s | Title: %s" %
                                 (stream_info["display_name"], stream_info["game"], stream_info["status"]))
        except Exception, error:
            print "Error in twitch_check() in racerbot.py"
            print error


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
    except Exception, error:
        print "Error in get_yt_video_info(video_id) in racerbot.py"
        print error


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
    except Exception, error:
        print error
        wolfram_json = json.dumps({"isSuggestion": False,
                                   "message": "You broke Wolfram, way to go... jerk"})
        return wolfram_json
# </editor-fold desc="Basic Functions">


# <editor-fold desc="Commands">
def commands(server_message):
    website = False  # these two are used to determine if the bot should bother with reddit stuff
    reddit_url = False
    try:
        if not joined:  # there are a few things we don't want to do until joined
            print server_message
        else:
            now = time.strftime("%I:%M:%S")
            user = server_message.split("!")[0].strip(":")
            try:
                message = server_message.split(channel + " :")[1]
            except:
                message = ""  # if we're in here, the server sent something the bot thinks a user sent

            print "%s - %s: %s" % (now, user, message)

            if testing:
                if message.lower().startswith(".test"):  # checks if bot is listening to us
                    try:
                        for user in user_list:
                            send_message(user)
                        print "test complete"
                    except:
                        print "Error in testing .test"

            # <editor-fold desc="dot commands">
            try:
                # this block is all the "dot" commands, where something is requested from the bot by a user
                if message.lower().startswith(".here"):  # checks if bot is listening to us
                    send_message("Yup!")
                elif message.lower().startswith(".source"):
                    send_message("https://github.com/jmalish/racerbot")
                elif message.lower().startswith(".help"):
                    send_message("https://github.com/jmalish/racerbot/blob/dev/commands_list.txt")
                elif message.lower().startswith(".fishify"):
                    message = message.split(".fishify ")[1]
                    send_message(fishify.fish(message, False))
                elif message.lower().startswith(".setfishchance "):
                    global fish_chance
                    new_num = message.split(".setfishchance")
                    fish_chance = (int(new_num[1]))
                    send_message("Chance of fishify is now 1 in " + str(fish_chance + 1))
                elif message.lower().startswith(".setfishtimer"):
                    send_message(fishify.set_timer(message.split()[1]))
                elif message.lower().startswith(".getfishtimer"):
                    send_message(fishify.get_timer())
                elif message.lower().startswith(".timesincefish"):
                    send_message(fishify.time_since_fish())
                elif message.lower().startswith(".eject"):
                    if botnick in ops_list:
                        send_message("%s punched out!" % user)
                        ircsock.send('KICK %s %s :EJECTING!!\n' % (channel, user))  # successfully kicks user
                        time.sleep(1)
                        send_message("Holy crap, he got some air!")
                    else:
                        send_message("%s punched out!" % user)
                        time.sleep(1)
                        send_message("...uhhh, I'm pushing the button but nothing's happening")
                elif message.lower().startswith(".setfishify"):
                    fishify.fish_word = message.split()[1]
                    send_message("You got it, I'll put a %s all over everything now" % fishify.fish_word)
                elif message.lower().startswith(".calc"):  # ~~~~~~~~~~ WOLFRAM
                    to_send = message.split(".calc")
                    wolfram_results = json.loads(query_wolfram_alpha(to_send[1]))
                    if wolfram_results["isSuggestion"]:  # whatever was sent didn't work
                        send_message("WA says that's not a thing, it suggests: %s" % wolfram_results["suggestion"])
                    elif wolfram_results["message"] is None:
                        send_message("%s: %s" % (wolfram_results["input_title"], wolfram_results["input_text"]))
                        send_message("%s: %s" % (wolfram_results["output_title"], wolfram_results["output_text"]))
                    else:
                        send_message(wolfram_results["message"])
                elif message.startswith(".chat"):
                    to_send = message.split(".chat")
                    send_message((clever.ask(to_send[1].strip())))
                elif message.lower().startswith(".livestreams"):
                    twitch.update_stream_statuses()
                    if len(twitch.online_channels) > 0:
                        for tw_channel in twitch.online_channels:
                            stream_info = json.loads(twitch.get_channel_info(tw_channel))
                            send_message("Check your pm's!")
                            private_message("www.twitch.tv/%s is streaming %s | Title: %s" %
                                            (stream_info["display_name"], stream_info["game"], stream_info["status"]),
                                            user)
                    else:
                        send_message("No one's streaming!")
                elif message.lower().startswith(".offlinestreams"):
                    if len(twitch.offline_channels) > 0:
                        channels = ""
                        for tw_channel in twitch.offline_channels:
                            channels += tw_channel + ", "

                        send_message("See your pm's for list of offline channels")
                        private_message(channels.rstrip().rstrip(','), user)
                    else:
                        send_message("There are no offline channels.")
                elif message.lower().startswith(".allstreams"):
                    if twitch.get_all_channels() == 0:
                        send_message("I don't have any streamers in my list! Add some with '.addstream <channel name>")
                    else:
                        channels = ""
                        for tw_channel in twitch.get_all_channels():
                            channels += tw_channel + ", "

                        send_message("Check your pm's!")
                        private_message(channels.rstrip().rstrip(','), user)
                elif message.lower().startswith(".addstream"):
                    channel_to_add = message.split(".addstream ")
                    send_message(twitch.add_new_channel(channel_to_add[1]))
                elif message.lower().startswith(".removestream"):
                    channel_to_remove = message.split(".removestream ")
                    send_message(twitch.remove_channel(channel_to_remove[1]))
                elif message.lower().startswith(".timesincetwitch"):
                    send_message(twitch.time_since_update())
                elif message.lower().startswith(".quote"):
                    if not testing:
                        quotes = irc_quotes.get_quotes()  # get all quotes from the table
                        if message.split(".quote")[1].strip():
                            quote_number = int(message.split(".quote")[1].strip()) - 1  # numbers are dumb
                            quote_user = quotes[quote_number][1]  # get each part of quote
                            quote_message = quotes[quote_number][2]
                            send_message("#%s - %s: %s" % (quote_number + 1, quote_user, quote_message))
                        else:  # no number requested, get and send random quote
                            random.seed(time.time())
                            random_int = random.randint(0, len(quotes)-1)  # get a random quote
                            quote_number = quotes[random_int][0]  # get each part of quote
                            quote_user = quotes[random_int][1]
                            quote_message = quotes[random_int][2]
                            send_message("#%s - %s: %s" % (quote_number, quote_user, quote_message))
                    else:
                        send_message("Quotes disabled while in testing mode")
                elif message.lower().startswith(".grab "):
                    if not testing:
                        try:
                            user_to_grab = message.split(".grab")[1].strip()  # split off username
                            if irc_quotes.grab(user_to_grab):
                                send_message("Got it!")
                            else:
                                send_message("Something went wrong! WHAT DID YOU DO?!")
                        except Exception, error:
                            send_message("I can't grab that!")
                            print error
                    else:
                        send_message("Quotes disabled while in testing mode")
                elif message.lower().startswith(".lastseen "):
                    if not testing:
                        user = message.split(".lastseen ")[1].strip()
                        if irc_quotes.last_seen(user):
                            send_message(irc_quotes.last_seen(user))
                        else:
                            send_message("%s? Oh, you don't want to know what they said..." % user)
                    else:
                        send_message("Quotes disabled while in testing mode")
                elif message.lower().startswith(".fishfact"):
                    send_message(fish_facts.get_random_fact())
                else:  # if no commands are called, then we'll do some fun stuff
                    # fishify stuff
                    ran_seed = time.time()
                    random.seed(ran_seed)
                    random_int = random.randint(0, fish_chance)
                    # fishify stuff
                    if random_int == 0:  # I want this to be separate so the bot doesn't stop looking for commands here
                        if fishify.timer_check():
                            try:
                                send_message(fishify.fish(message, True))  # send the chosen word
                            except Exception, error:
                                print "Error in random fishify:"
                                print error

            except Exception, error:
                print "Something went wrong in dot commands:"
                print error
            # </editor-fold desc="dot commands">

            # <editor-fold desc="regex stuff">
            if "nospoil" not in message:  # this lets a user post a link without the bot giving info on it
                # ~~~~~~~~ WEBSITE TITLES
                try:
                    # search for websites
                    url_regex = re.findall("(www.)?[a-zA-Z0-9\-]+\.[a-z]{2,4}", message, flags=re.IGNORECASE)
                    # here, we're just seeing if the message even contains a url, not concerned with whole url yet
                    if url_regex:  # if this is true, the message has a url in it
                        website = True
                        for word in message.split():
                            # get rid of trailing commas or periods (ie end of sentence)
                            word = word.strip(',').strip('.')
                            if "reddit" in word:
                                website = False
                                pass
                            elif ("twitch" in word) or ("youtube" in word) \
                                    or ("youtu.be" in word) or ("freenode" in word):
                                # reddit, twitch, and youtube stuff is already being taken care of
                                # no need to get it here
                                # Freenode server pings bot every so often
                                pass
                            elif "." in word:  # look for 'words' with a '.' in the middle
                                if "@" not in word:  # ignore emails
                                    if "meme" not in word:
                                        title = get_page_title(word)
                                        if title:
                                            send_message(str(title))
                except Exception, error:
                    print "Something went wrong in website title:"
                    print error
                # end of website url block

                # ~~~~~~~~ REDDIT
                try:
                    # search for subreddits (r/example)
                    ''' old regex  
                    reddit_regex = re.findall("r\/([a-z0-9_]+)(\/comments\/([a-z0-9_]+))?", message,
                                                 flags=re.IGNORECASE)
                    '''

                    reddit_regex = \
                        re.findall("([A-z_0-9]*)?(\/comments\/)([A-z_0-9]{6})(\/[A-z_0-9]*)?(\/([A-z_0-9]{7}))?",
                                   message, flags=re.IGNORECASE)

                    # if this is true, we found a subreddit name
                    if reddit_regex and not website:
                        for result in reddit_regex:
                            if result[5]:  # if result[5] has something in it, that means we have a comment
                                try:
                                    reddit_link = "https://www.reddit.com/comments/%s/_/%s" % (result[2], result[5])
                                    submission = reddit.get_submission(reddit_link)
                                    send_message("%s commented on %s" %
                                                 (submission.comments[0].author, submission.title))
                                except Exception as error:
                                    print error
                            elif result[1]:  # if result[1] has something in it, that means we have a comments link
                                thread_id = result[2]  # get thread ID from regex group 3
                                try:
                                    thread_info = reddit.get_submission(submission_id=thread_id)
                                    send_message(str(thread_info.title) + " | " + str(thread_info.subreddit))
                                except Exception as error:
                                    print error

                    subreddit_regex = re.findall(r"\br\/([A-z_0-9]*\b)", message)

                    if subreddit_regex:
                        for result in subreddit_regex:
                            subreddit_name = result  # get subreddit name from regex group 1
                            try:
                                subreddit_title = reddit.get_subreddit(subreddit_name)
                                send_message("http://www.reddit.com/r/%s - %s" % (subreddit_name, subreddit_title))
                            except Exception as error:
                                send_message("http://www.reddit.com/r/%s - That's not a real subreddit..." %
                                      subreddit_name)
                                print error
                except Exception, error:
                    print "Something went wrong in reddit block:"
                    print error
                # end of reddit block

                # ~~~~~~~~ YOUTUBE
                try:
                    # regex to get youtube ID, this might need to be cleaned up
                    # will not see links that have an argument before the video id argument (ie ?t=)
                    regex_youtube = re.findall("youtu\.?be(.com)?/?(watch\?v=)?([_a-zA-Z0-9\-]{11})",
                                               message, flags=re.IGNORECASE)
                    if regex_youtube:  # if we find a youtube link
                        for vid_id in regex_youtube:  # foreach youtube link in message
                            send_message(get_yt_video_info(vid_id[2]))  # pass the video ID to function
                except Exception, error:
                    print "Something went wrong in youtube:"
                    print error

                # ~~~~~~~~~~~ TWITCH
                try:
                    # regex to find twitch info
                    twitch_regex = re.findall("twitch.tv/([a-zA-Z0-9\+_]+)(/v/([0-9]{8}))?",
                                              message, flags=re.IGNORECASE)

                    for link in twitch_regex:
                        if link[2]:  # main page of stream linked
                            vod_id = link[2]
                            vod_details = twitch.get_vod_info(vod_id)
                            if vod_details:
                                vod_info_json = json.loads(twitch.get_vod_info(vod_id))
                                send_message("Title: %s | Game: %s | Channel: %s" %
                                             (vod_info_json["title"],
                                              vod_info_json["game"],
                                              vod_info_json["display_name"]))
                        else:  # vod linked
                            channel_info = json.loads(twitch.get_channel_info(link[0]))
                            if channel_info:  # if the channel is live, send stream info
                                if channel_info["viewer_count"] == 1:
                                    send_message("%s is streaming %s | Title: %s | %s viewer" %
                                                 (channel_info["display_name"],
                                                  channel_info["game"],
                                                  channel_info["status"],
                                                  channel_info["viewer_count"]))
                                else:
                                    send_message("%s is streaming %s | Title: %s | %s viewers" %
                                                 (channel_info["display_name"],
                                                  channel_info["game"],
                                                  channel_info["status"],
                                                  channel_info["viewer_count"]))
                except Exception, error:
                    print "Something went wrong in twitch in racerbot"
                    print error
                # end of Twitch block
            # end of nospoil block
            # </editor-fold desc="regex stuff">

            # ~~~~~~~~ QUOTES
            if not testing:
                try:
                    irc_quotes.add_last_message(user, message)  # add message to latest messages
                except Exception, error:
                    print "Something went wrong in quotes"
                    print error

            # end of "if joined:"
    except Exception, error:
        print "Error in commands():"
        print traceback.format_exc(error)
# </editor-fold desc="Commands">

# <editor-fold desc="Bot">
# setting up socket
print "Attempting to connect to server"
ircsock.connect((server, port))  # Connect to the server using provided port
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " Created by racer0940\n")  # user authentication
print "Authenticating"
ircsock.send("NICK " + botnick + "\n")  # assign the nick to the bot
print "Assigning name"

join_chan(channel)  # initial channel join

while True:
    while True:  # this is the actual bot itself, everything in this block is what the bot uses
        try:
            irc_message = ircsock.recv(2048)  # receive data from server
            irc_message = irc_message.strip('\n\r')  # strip any unnecessary line breaks

            with open(log_file_name, 'a') as log_file:  # open log file in append mode
                log_file.write(irc_message)  # write to log file

            twitch_check()  # check if it's time to update twitch

            try:
                # user list creation
                if not joined:
                    names_list_check = "%s = %s :" % (botnick, channel)  # find NAMES line
                    if names_list_check in irc_message:
                        names_list = irc_message.split(" :")[1].split("\r")[0].split(' ')
                        for name in names_list:
                            user_list.append(name.strip("@"))  # add user to user list
                            if name.startswith("@"):  # if user is an op (denoted by @)
                                ops_list.append(name.strip("@"))  # add them to op list

                # not sure if making this an if/elif block is a good idea, time will tell I suppose
                if irc_message.find("PING :") != -1:  # don't want to be rude, respond to servers pings
                    if testing:
                        print irc_message

                    ping()
                elif "/NAMES" in irc_message:
                    print "~~~~~~~~~~~~~~~~~~~~~~~ I'm in! ~~~~~~~~~~~~~~~~~~~~~~~"
                    joined = True  # we've joined the channel
                    fishify.fish_clock = calendar.timegm(time.gmtime()) - 300
                    twitch.joined = True
                elif "PART" in irc_message:
                    user = irc_message.split('!')[0].strip(':')
                    try:
                        user_list.remove(user)
                        ops_list.remove(user)
                    except:
                        pass  # do nothing, user is not an op
                elif "KICK" in irc_message:
                    user = irc_message.split(' ')[3]
                    try:
                        user_list.remove(user)
                        ops_list.remove(user)
                    except:
                        pass  # do nothing, user is not an op
                elif "JOIN" in irc_message:
                    user = irc_message.split('!')[0].strip(':')
                    user_list.append(user)
                elif "MODE" in irc_message:
                    if "+o" in irc_message:
                        oped_user = irc_message.split(" ")[4]
                        ops_list.append(oped_user)
                    elif "-o" in irc_message:
                        user = irc_message.split(" ")[4]
                        ops_list.remove(user)
                elif irc_message.find(' PRIVMSG '):
                    commands(irc_message)
            except Exception, e:
                print "Uncaught Error in while True loop"
                print e
        except Exception, error:
            print "Error with server connection"
            print error

    print "Attempting reconnect in 15 seconds..."
    time.sleep(15)
# </editor-fold desc="Bot">
