import re
import twitch
import json
import requests

message = "racer0940: http://www.twitch.tv/racer0940"
channels = ["SuperMCGamer", "tomvsofficial"]


twitch_regex = re.findall("twitch.tv\/([a-zA-Z0-9\_\+]+)", message, flags=re.IGNORECASE)

# stream_info = json.loads(twitch.get_channel_info(channels[0]))
# print stream_info["viewer_count"]

for channel in channels:
    channel_info = json.loads(twitch.get_channel_info(channel))

    if channel_info:  # if the channel is live, send stream info
        if channel_info["viewer_count"] == 1:
            print("%s is streaming %s | Title: %s | %s viewer" %
                  (channel_info["display_name"],
                   channel_info["game"],
                   channel_info["status"],
                   channel_info["viewer_count"]
                   )
                  )
        else:
            print("%s is streaming %s | Title: %s | %s viewers" %
                  (channel_info["display_name"],
                   channel_info["game"],
                   channel_info["status"],
                   channel_info["viewer_count"]
                   )
                  )
