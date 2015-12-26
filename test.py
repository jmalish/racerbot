import twitch
import requests
import json

# twitch.twitch_initial()

channel = "xmasia"

api_url = "https://api.twitch.tv/kraken/streams/%s" % channel
channel_details = requests.get(api_url).text
channel_details_json = json.loads(channel_details)
# read API to see if streamer is live and put them in correct list
if channel_details_json["stream"] is None:  # channel is not live
    print True
else:
    print False
