import praw
import re

reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW

message = "r/iracing comment here r/nascar"

subreddit_regex = re.findall(r"\br\/([A-z_0-9]*\b)", message)

if subreddit_regex:
    for result in subreddit_regex:
        subreddit_name = result  # get subreddit name from regex group 1
        try:
            subreddit_title = reddit.get_subreddit(subreddit_name)
            print("http://www.reddit.com/r/%s - %s" % (subreddit_name, subreddit_title))
        except Exception as error:
            print("http://www.reddit.com/r/%s - That's not a real subreddit..." %
                         subreddit_name)
            print error
else:
    print "nothing found"
