import re
from bs4 import BeautifulSoup as Bs
import requests

message = "google.com, and http://www.twitch.tv/directory/following"


def get_page_title(site):  # TODO: Make this use GETs instead of POST
    try:
        r = requests.get(site, headers={'user-agent': 'roboracer'})
        html = Bs(r.text, "html.parser")
        return html.title.text
    except:
        pass  # do nothing, it's probably a fake website

url_regex = re.findall("[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|de|co|tv)+", message, flags=re.IGNORECASE)
# here, we're just seeing if the message even contains a url, not concerned with whole url yet
if url_regex:  # if this is true, the message has a url in it
    for word in message.split():
        if "reddit" in word:
            pass  # reddit stuff is already being taken care of, no need to get it here
        elif ("com" or "org" or "net" or "mil" or "edu" or "de" or "co" or "tv") in word:  # find 'words' with a common TLD
            url = word.strip(',')  # get rid of any trailing commas
            print url
            # TODO: check for status with   requests.status_code
        else:
            print "!" + word  # for debugging only
