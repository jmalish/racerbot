import requests
import json
import time
import calendar

channel = "racer0940"
api_url = "https://api.twitch.tv/kraken/streams/%s" % channel

all_channels = ["bobross", "racer0940"]  # this holds all channels, on and offline
online_channels = []  # this holds all channels that are currently live
offline_channels = ["bobross", "racer0940"]  # this holds all channels that are currently offline
timer = 120  # used to tell bot when to check for channel updates (120 = 2 minutes)
tw_clock = 0


def update_stream_statuses():
    now_streaming = []  # used for channels that have started streaming
    try:
        # first, see if the live streams are still live
        for channel in online_channels:
            api_url = "https://api.twitch.tv/kraken/streams/%s" % channel
            channel_details = requests.get(api_url)
            # read API to see if streamer is live and put them in correct list
            if channel_details.json()["stream"] is None:  # channel is no longer live
                online_channels.remove(channel)  # remove the channel from list of online
                offline_channels.append(channel)  # and move it to the offline list
            else:
                pass  # don't do anything, as the channel is still live
        for channel in offline_channels:
            api_url = "https://api.twitch.tv/kraken/streams/%s" % channel
            channel_details = requests.get(api_url)
            # read API to see if streamer is live and put them in correct list
            if channel_details.json()["stream"] is not None:  # channel is now live
                offline_channels.remove(channel)  # remove the channel from list of offline
                online_channels.append(channel)  # and move it to the online list
                # the channel has gone from offline to online, so we need to let the irc room know
                now_streaming.append(channel)
                print "%s has started streaming" % channel  # debugging
            else:
                pass  # don't do anything, as the channel is still offline
        global tw_clock
        tw_clock = calendar.timegm(time.gmtime())
        return now_streaming
    except Exception, e:
        print "Error in update_streams_status()"
        print e


# used to check if it's been long enough to update streams
def timer_check():
    time_now = calendar.timegm(time.gmtime())
    if (time_now - tw_clock) > timer:
        print "updating"
        return update_stream_statuses()
    else:
        print "not updating"
        return []


print timer_check()
