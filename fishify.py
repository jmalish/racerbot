# imports
import random
import time
import calendar
import json
from hyphen import Hyphenator

# get dictionary API key
with open('pysecrets.json') as jsonfile:  # get contents of secrets file (contains api keys)
    data = json.load(jsonfile)

dictionaryApiKey = data["dictionary"]   # api key for dictionary

# other variables
fishWord = "fish"  # used in fish() as the word that replaces the selected syllable
fishTimer = 300     # used to keep fishify from running every other message (default is 5 min)
fishClock = 000     # used to see how long it's been since last fishify
hyphenator = Hyphenator('en_US')  # Hyphenator setup


# checks to see if it's been long enough since last fishify
def timerCheck():
    timeNow = calendar.timegm(time.gmtime())
    if (timeNow - fishClock) > fishTimer:
        return True
    else:
        return False


# sets timer
def setTimer(newTime):
    try:
        global fishTimer
        fishTimer = int(newTime) * 60
        return "Fish timer now set to " + str(fishTimer/60) + " minutes"
    except Exception as e:
        print e.message
        return "Whoa there, what kinda number is that?!"


# gets timer value
def getTimer():
    return "Fish timer is set at " + str(fishTimer/60) + " minutes"


# gets time since last fishify
def timeSinceFish():
    timeNow = calendar.timegm(time.gmtime())
    timeSinceFish = (timeNow - fishClock)  # get seconds since fish

    m, s = divmod(timeSinceFish, 60)  # < this converts seconds
    h, m = divmod(m, 60)              # < to HH:MM:SS form
    return "Time since last fishing: %d:%02d:%02d" % (h, m, s)


# actual fishify function
def fish(sentence, isRandomCall):  # takes a word and changes the syllable to a given word
    for i in range(0, 5):  # let the bot try five times to find a word, this is so it doesn't give up on first try
        try:
            words = sentence.split()  # get number of words by splitting on spaces

            random.seed(time.time())  # set seed for random
            randomIntWord = random.randint(0, len(words) - 1)  # generate a random integer to select word
            chosenWord = words[randomIntWord]  # get the word that correlates to the random integer (location in array)
            print ("I chose '" + chosenWord + "' to fishify")

            chosen_word_unicode = chosenWord.decode('unicode-escape')
            syllables = hyphenator.syllables(chosen_word_unicode)

            random_int_syl = random.randint(0, len(syllables) - 1)  # generate a random integer to select syllable
            syllables[random_int_syl] = fishWord  # replace syllable with fishify word

            newWord = ""
            for i in range(len(syllables)):
                newWord += syllables[i]

            words[randomIntWord] = newWord

            newSentence = ""
            for i in range(len(words)):
                if words[i] == ".fishify":
                    pass  # if the first word is the command to fishify, we don't want to add it to the sentence
                else:
                    newSentence += words[i] + " "

            if isRandomCall:
                # get current time, if the fishify was successful, this says when the last time it was run
                global fishClock
                fishClock = calendar.timegm(time.gmtime())
            return newSentence
        except Exception as e:  # catch if the selected word doesn't exist in the dictionary
            i += 1
            time.sleep(.5)  # wait a sec to give random seed a chance to change
            if i == 3:
                # if it tried all three times and failed, tell chat what happened
                print "Error in fishify(): " + e.message
                return "I'm pretty sure none of those are words... I looked in the dictionary and everything!"
