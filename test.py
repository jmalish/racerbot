import json
import re
import requests


message = "video 1: https://www.youtube.com/watch?v=ybwCQmbCh2I video 2: https://youtu.be/Ro6HkE0On-k"

with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    data = json.load(jsonfile)

youtubeApiKey = data["youtubeKey"]  # api key for youtube


def get_yt_video_info(video_id):
    try:
        # URL to get info for video
        api_url = "https://www.googleapis.com/youtube/v3/videos?id=" + video_id + \
                  "&key=" + youtubeApiKey + "%20&part=snippet,statistics"
        data = requests.get(api_url)  # retrieve the JSON from Google's API
        vid_title = data.json()["items"][0]["snippet"]["title"]  # get title of video
        vid_channel = data.json()["items"][0]["snippet"]["channelTitle"]  # get channel of video
        vid_view_count = data.json()["items"][0]["statistics"]["viewCount"]  # get view count of video
        return "Title: %s | Views: %s | Channel: %s" % (vid_title, vid_view_count, vid_channel)
    except Exception, e:
        print e

# regex to get youtube ID, this might need to be cleaned up
# will not see links that have an argument before the video id argument (ie ?t=)
regex_youtube = re.findall("youtu\.?be(.com)?/?(watch\?v=)?([a-zA-Z0-9\-]+)", message, flags=re.IGNORECASE)
if regex_youtube:  # if we find a youtube link
    for id in regex_youtube:  # foreach youtube link in message
        print get_yt_video_info(id[2])  # pass the video ID to function
