import json
import requests
import os.path
import calendar
import time

# variables
# all_channels = []  # this holds all channels, on and offline
online_channels = []  # this holds all channels that are currently live
offline_channels = []  # this holds all channels that are currently offline
timer = 60  # used to tell bot when to check for channel updates (60 = 1 minute)
tw_clock = 0  # used to keep track of how long it's been since last check
joined = False  # bot tells us when it has successfully joined the room


# used to check if it's been long enough to update streams
def timer_check():
    if joined:
        time_now = calendar.timegm(time.gmtime())
        if (time_now - tw_clock) > timer:
            now_streaming = update_stream_statuses()
            return now_streaming
        else:
            return []


def update_stream_statuses():
    now_streaming = []  # used for channels that have started streaming
    try:
        for channel in online_channels:
            api_url = "https://api.twitch.tv/kraken/streams/%s" % channel
            channel_details = requests.get(api_url).text
            channel_details_json = json.loads(channel_details)
            # read API to see if streamer is live and put them in correct list
            if channel_details_json["stream"] is None:  # channel is not live
                online_channels.remove(channel)  # remove the channel from list of offline
                offline_channels.append(channel)  # and move it to the online list
                # the channel has gone from offline to online, so we need to let the irc room know
            else:
                pass  # don't do anything, as the channel is still online

        for channel in offline_channels:
            api_url = "https://api.twitch.tv/kraken/streams/%s" % channel
            channel_details = requests.get(api_url).text
            channel_details_json = json.loads(channel_details)
            # read API to see if streamer is live and put them in correct list
            if channel_details_json["stream"] is None:  # channel is not live
                pass  # don't do anything, as the channel is still offline
            else:
                offline_channels.remove(channel)  # remove the channel from list of offline
                online_channels.append(channel)  # and move it to the online list
                now_streaming.append(channel)
        global tw_clock
        tw_clock = calendar.timegm(time.gmtime())

        return now_streaming
    except Exception, e:
        print "Error in update_streams_status()"
        print e


# initial setup, should only be run when bot first joins (and again every time it has to rejoin)
def twitch_initial():
    print "Initializing twitch"
    try:
        # first, make sure the streamers file actually exists
        if os.path.isfile("streamers.json"):
            # read the json file of streamers and add them to our list
            with open('streamers.json') as streamers_json:
                for channel in json.load(streamers_json):
                    # all_channels.append(channel)  # add the current streamer to the list of all channels
                    offline_channels.append(channel)  # add all channels to offline for right now
        # we don't want to update lists just yet, that'll be done in the first check
        else:
            print "streamers.json file does not exist, creating it now"
            open('streamers.json', 'w').close()  # create file
            global tw_clock
            tw_clock = calendar.timegm(time.gmtime())
    except Exception, e:
        print "Error in twitch Initial:"
        print e
    print "Twitch Initialization done"


def get_channel_info(channel):
    try:
        api_url = "https://api.twitch.tv/kraken/channels/%s" % channel
        stream_details = requests.get(api_url)
        stream_status = stream_details.json()["status"]  # this is the title of the stream
        stream_game = stream_details.json()["game"]  # game the streamer is playing
        stream_display_name = stream_details.json()["display_name"]  # name of streamer with correct capitalization
        stream_json = json.dumps({"status": stream_status,
                                  "game": stream_game,
                                  "display_name": stream_display_name})
        return stream_json
    except Exception, e:
        print "Error in get_channel_title(channel)"
        print e


def add_new_channel(new_channel):
    if new_channel in get_all_channels():  # if the list already contains the channel, no need to add it
        return "%s is already in the list of streamers. To see the full list, type '.allstreamers'" % new_channel
    else:
        api_url = "https://api.twitch.tv/kraken/streams/%s" % new_channel
        channel_details = requests.get(api_url)
        if "error" not in channel_details.json():  # this is a crappy way to do this, I don't know a better way
            # all_channels.append(new_channel)  # add channel to list
            offline_channels.append(new_channel)
            with open('streamers.json', 'w') as outfile:  # update file
                json.dump(get_all_channels(), outfile)  # write all channels to file, including new channel

            return "%s added to list of streamers" % new_channel
        else:
            return "%s does not exist on twitch" % new_channel  # inform user that channel doesn't exist


def remove_channel(channel_to_remove):
    try:
        if channel_to_remove in get_all_channels():  # check to see if channel even exists
            get_all_channels().remove(channel_to_remove)  # if it does, remove it from all_channels
            if channel_to_remove in online_channels:  # we also need to remove it from whatever list it's in
                online_channels.remove(channel_to_remove)
            elif channel_to_remove in offline_channels:
                offline_channels.remove(channel_to_remove)
        else:
            return "%s is not in the list of streamers" % channel_to_remove
        with open('streamers.json', 'w') as outfile:  # update file
            json.dump(get_all_channels(), outfile)  # write all channels to file, including new channel
        return "%s has been removed from the list of streamers" % channel_to_remove
    except Exception, e:
        print "Error in twitch.remove_channel, possibly because channel doesn't exist"
        print e
        return "%s is not in the list of streamers" % channel_to_remove


# gets time since last fishify
def time_since_update():
    time_now = calendar.timegm(time.gmtime())
    time_since_tw_update = (time_now - tw_clock)  # get seconds since fish

    m, s = divmod(time_since_tw_update, 60)  # < this converts seconds
    h, m = divmod(m, 60)                  # < to HH:MM:SS form
    return "Time since twitch update: %d:%02d:%02d" % (h, m, s)


def get_all_channels():
    all_channels = []
    for channel in online_channels:
        all_channels.append(channel)
    for channel in offline_channels:
        all_channels.append(channel)

    all_channels.sort()
    return all_channels
