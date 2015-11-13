import json
import random
import time
import urllib
import xml.etree.ElementTree as ET

with open('pysecrets.json') as jsonfile:
    data = json.load(jsonfile)

dictionaryApiKey = data["dictionary"]  # api key for dictionary

s = "dinosaur"
sCount = s.split()  # get number of words by splitting on spaces

random.seed(time.time())
randomInt = random.randint(0, len(sCount) - 1)
chosenWord = sCount[randomInt]

link = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/" + chosenWord + "?key=" + dictionaryApiKey

tree = ET.parse(urllib.urlopen(link))
root = tree.getroot()


# for test in root.iter('hw'):
#    print test.text

print root[0][2].text
