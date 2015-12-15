import re
from bs4 import BeautifulSoup as Bs
import requests
from requests.exceptions import ConnectionError

message = "this sentence.Don't forget to visit afeadfe.com"


def get_page_title(site):
    try:
        if "http" not in site:
            site = "http://" + site  # requests needs the link to have http in front of it

        r = requests.get(site, headers={'user-agent': 'roboracer'})
        if r.status_code == 200:
            html = Bs(r.text, "html.parser")
            return html.title.text.encode('utf-8').strip()
        else:
            print "Unable to reach " + site + ": " + r.status_code
            pass  # we got a 404 page or something
    except ConnectionError as c:
        print "Connection Error: " + site
        return False
    except Exception, e:
        print e
        return False

url_regex = re.findall("(www.)?[a-zA-Z0-9\-]+\.[a-z]{2,3}", message, flags=re.IGNORECASE)
# here, we're just seeing if the message even contains a url, not concerned with whole url yet
if url_regex:  # if this is true, the message has a url in it
    for word in message.split():
        word = word.strip(',').strip('.')  # get rid of trailing commas or periods (ie end of sentence)
        if ("reddit" in word) or ("twitch" in word):
            # reddit and twitch stuff is already being taken care of
            # no need to get it here
            pass
        elif "." in word:  # look for 'words' with a '.' in the middle
            if "@" not in word:  # ignore emails
                title = get_page_title(word)
                if title:
                    print title
