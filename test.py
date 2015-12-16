import json
import re

import gdata.youtube
import gdata.youtube.service

message = "video 1: https://www.youtube.com/watch?v=ybwCQmbCh2I video 2: https://youtu.be/Ro6HkE0On-k"


def get_yt_video_info(id):
    pass

with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    data = json.load(jsonfile)

youtubeApiKey = data["youtubeKey"]  # api key for youtube
youtubeApiId = data["youtubeId"]  # api key for youtube

# YouTube setup
yt_service = gdata.youtube.service.YouTubeService()  # create youtube service
yt_service.ssl = True  # Turn on HTTPS/SSL access for youtube
yt_service.developer_key = youtubeApiKey
yt_service.client_id = youtubeApiId

# regex to get youtube ID, this might need to be cleaned up
# will not see links that have an argument before the video id argument (ie ?t=)
regex_youtube = re.findall("youtu\.?be(.com)?/?(watch\?v=)?([a-zA-Z0-9\-]+)", message, flags=re.IGNORECASE)

if regex_youtube:
    for id in regex_youtube:  # foreach youtube link
        print id[2]  # pass the video ID to function
