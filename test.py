import urllib
import json
import requests
import xml.etree.ElementTree as Etree

# API Key variables
with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    secrets = json.load(jsonfile)

wolfram_api_key = secrets["wolfram"]         # api key for wolfram alpha


def sendmsg(message):
    print message


def query_wolfram_alpha(query):
    query = urllib.quote(query)  # convert string to url safe string
    try:
        api_url = "http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext" % \
                  (wolfram_api_key, query)
        wolfram_response = requests.get(api_url).text.encode('utf-8').strip()

        root = Etree.fromstring(wolfram_response)

        if root.attrib["success"]:
            if int(root.attrib["numpods"]) > 0:  # make sure the query actually has something to show
                # get all the stuff we want
                wolfram_input_title = root[0].attrib["title"]
                wolfram_input_text = root[0][0][0].text
                wolfram_output_title = root[1].attrib["title"]
                wolfram_output_text = root[1][0][0].text
                # put all that stuff into a json string
                wolfram_json = json.dumps({"input_title": str(wolfram_input_title),
                                           "input_text": str(wolfram_input_text),
                                           "output_title": str(wolfram_output_title),
                                           "output_text": str(wolfram_output_text),
                                           "isSuggestion": False})
                # send that json string back
                return wolfram_json
            else:  # if not, give user wolfram's suggestion
                # print "we're here"
                wolfram_json = json.dumps({"suggestion": str(root[0][0].text),
                                           "isSuggestion": True})
                return wolfram_json
        else:
            sendmsg("Now you're just trying to make stuff up")
    except Exception, e:
        print e.message
        sendmsg("You broke Wolfram, way to go... jerk")



message = ".calc test"

if message.lower().startswith(".calc"):  # ~~~~~~~~~~ WOLFRAM
    to_send = message.split(".calc")
    wolfram_results = json.loads(query_wolfram_alpha(to_send[1]))
    if wolfram_results["isSuggestion"]:  # whatever was sent didn't work
        sendmsg("WA says that's not a thing, it suggests: %s" % wolfram_results["suggestion"])
    else:
        sendmsg("%s: %s" % (wolfram_results["input_title"], wolfram_results["input_text"]))
        sendmsg("%s: %s" % (wolfram_results["output_title"], wolfram_results["output_text"]))
