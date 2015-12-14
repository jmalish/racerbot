import re
from bs4 import BeautifulSoup as Bs
import requests

message = "twitch.tv/racer0940 name@nasa.gov google.com words that are not links."


def get_page_title(site):  # TODO: Make this use GETs instead of POST
    try:
        r = requests.get(site, headers={'user-agent': 'roboracer'})
        html = Bs(r.text, "html.parser")
        return html.title.text
    except:
        pass  # do nothing, it's probably a fake website

url_regex = re.findall("(www.)?[a-zA-Z0-9\-]+\.[a-z]{2,3}", message, flags=re.IGNORECASE)
# here, we're just seeing if the message even contains a url, not concerned with whole url yet
if url_regex:  # if this is true, the message has a url in it
    for word in message.split():
        word = word.strip(',').strip('.')  # get rid of trailing commas or periods (ie end of sentence)
        if "reddit" in word:
            pass  # reddit stuff is already being taken care of, no need to get it here
        # find 'words' with a common TLD
        elif "." in word:
            if "@" not in word:  # ignore emails
                print word
                # TODO: check for status with   requests.status_code
