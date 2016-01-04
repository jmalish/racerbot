import re
import twitch
import json

message = "http://www.twitch.tv/grokken/ and http://www.twitch.tv/grokken/v/33340037"

# twitch_regex = re.findall("twitch.tv\/([a-zA-Z0-9\_\+]+)\/v\/([0-9]{8})", message, flags=re.IGNORECASE)
#
# if twitch_regex[0][1]:
#     vod_id = twitch_regex[0][1]
#     vod_details = twitch.get_vod_info(vod_id)
#     if vod_details:
#         vod_info_json = json.loads(twitch.get_vod_info(vod_id))
#         print("Title: %s | Game: %s | Channel: %s" %
#               (vod_info_json["title"], vod_info_json["game"], vod_info_json["display_name"]))
#     else:
#         print "nothing"

twitch_regex = re.findall("twitch.tv\/([a-zA-Z0-9\_\+]+)(\/v\/([0-9]{8}))?", message, flags=re.IGNORECASE)

for link in twitch_regex:
    if link[2]:  # main page of stream linked
        vod_id = link[2]
        vod_details = twitch.get_vod_info(vod_id)
        if vod_details:
            vod_info_json = json.loads(twitch.get_vod_info(vod_id))
            print("Title: %s | Game: %s | Channel: %s" %
                  (vod_info_json["title"], vod_info_json["game"], vod_info_json["display_name"]))
    else:  # vod linked
        channel_info = json.loads(twitch.get_channel_info(link[0]))
        if channel_info:  # if the channel is live, send stream info
            if channel_info["viewer_count"] == 1:
                print("%s is streaming %s | Title: %s | %s viewer" %  # TODO: sendmsg
                        (channel_info["display_name"],
                         channel_info["game"],
                         channel_info["status"],
                         channel_info["viewer_count"]
                         ))
            else:
                print("%s is streaming %s | Title: %s | %s viewers" %  # TODO: sendmsg
                        (channel_info["display_name"],
                         channel_info["game"],
                         channel_info["status"],
                         channel_info["viewer_count"]))

# try:
#     # regex to find twitch info
#     twitch_regex = re.findall("twitch.tv\/([a-zA-Z0-9\_\+]+)(\/v\/([0-9]{8}))?", message, flags=re.IGNORECASE)
#
#     if twitch_regex:
#         if twitch_regex[0][2] is not '':  # if true, we were passed a vod link
#             vod_id = twitch_regex[0][2]
#             vod_details = twitch.get_vod_info(vod_id)
#             if vod_details:
#                 vod_info_json = json.loads(twitch.get_vod_info(vod_id))
#                 print("Title: %s | Game: %s | Channel: %s" %
#                       (vod_info_json["title"], vod_info_json["game"], vod_info_json["display_name"]))
#         else:  # otherwise it was a live stream
#             for username in twitch_regex[0]:  # for each username in the message
#                 channel_info = json.loads(twitch.get_channel_info(username))
#
#                 if channel_info:  # if the channel is live, send stream info
#                     if channel_info["viewer_count"] == 1:
#                         print("%s is streaming %s | Title: %s | %s viewer" %  # TODO: sendmsg
#                                 (channel_info["display_name"],
#                                  channel_info["game"],
#                                  channel_info["status"],
#                                  channel_info["viewer_count"]
#                                  ))
#                     else:
#                         print("%s is streaming %s | Title: %s | %s viewers" %  # TODO: sendmsg
#                                 (channel_info["display_name"],
#                                  channel_info["game"],
#                                  channel_info["status"],
#                                  channel_info["viewer_count"]))
# except Exception, e:
#     print "Something went wrong in twitch in racerbot"
#     print e
