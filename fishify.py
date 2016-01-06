# imports
import random
import time
import calendar
from hyphen import Hyphenator

# other variables
fish_word = "fish"  # used in fish() as the word that replaces the selected syllable
fish_timer = 300     # used to keep fishify from running every other message (default is 5 min)
fish_clock = 000     # used to see how long it's been since last fishify
hyphenator = Hyphenator('en_US')  # Hyphenator setup


# checks to see if it's been long enough since last fishify
def timer_check():
    time_now = calendar.timegm(time.gmtime())
    if (time_now - fish_clock) > fish_timer:
        return True
    else:
        return False


# sets timer
def set_timer(new_time):
    try:
        global fish_timer
        fish_timer = int(new_time) * 60
        return "Fish timer now set to " + str(fish_timer/60) + " minutes"
    except Exception as e:
        print e
        return "Whoa there, what kinda number is that?!"


# gets timer value
def get_timer():
    return "Fish timer is set at " + str(fish_timer/60) + " minutes"


# gets time since last fishify
def time_since_fish():
    time_now = calendar.timegm(time.gmtime())
    time_since_fishify = (time_now - fish_clock)  # get seconds since fish

    m, s = divmod(time_since_fishify, 60)  # < this converts seconds
    h, m = divmod(m, 60)              # < to HH:MM:SS form
    return "Time since last fishing: %d:%02d:%02d" % (h, m, s)


# actual fishify function
def fish(sentence, is_random_call):  # takes a word and changes the syllable to a given word
    for j in range(0, 5):  # let the bot try five times to find a word, this is so it doesn't give up on first try
        try:
            words = sentence.split()  # get number of words by splitting on spaces

            random.seed(time.time())  # set seed for random
            random_int_word = random.randint(0, len(words) - 1)  # generate a random integer to select word
            chosen_word = words[random_int_word]  # get the word that correlates to the random integer
            print ("I chose '" + chosen_word + "' to fishify")

            chosen_word_unicode = chosen_word.decode('unicode-escape')
            syllables = hyphenator.syllables(chosen_word_unicode)

            random_int_syl = random.randint(0, len(syllables) - 1)  # generate a random integer to select syllable
            syllables[random_int_syl] = fish_word  # replace syllable with fishify word

            new_word = ""
            for i in range(len(syllables)):
                new_word += syllables[i]

            words[random_int_word] = new_word

            new_sentence = ""
            for i in range(len(words)):
                if words[i] == ".fishify":
                    pass  # if the first word is the command to fishify, we don't want to add it to the sentence
                else:
                    new_sentence += words[i] + " "

            if is_random_call:
                # get current time, if the fishify was successful, this says when the last time it was run
                global fish_clock
                fish_clock = calendar.timegm(time.gmtime())
            return new_sentence.strip()
        except Exception as e:  # catch if the selected word doesn't exist in the dictionary
            j += 1
            time.sleep(.5)  # wait a sec to give random seed a chance to change
            if j == 3:
                # if it tried all three times and failed, tell chat what happened
                print "Error in fishify(): " + e
                return "I'm pretty sure none of those are words... I looked in the dictionary and everything!"
