import praw
import re

reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW

message = "https://www.reddit.com/r/videos/comments/3w8e6u/star_wars_battlefront_real_life_mod/"

# looks for subreddits, regex looks for something similar to 'r/subreddit' and strips off the 'r/'
subreddit_regex = re.findall("r/([a-z0-9]+)(/comments/([a-z0-9_]+))?", message, flags=re.IGNORECASE)
if subreddit_regex:  # if this is true, we found a subreddit name
    for result in subreddit_regex:
        if result[1]:  # if result[1] has something in it, that means we have a comments link
            thread_id = result[2]  # get thread ID from regex group 3
            try:
                thread_info = reddit.get_submission(submission_id=thread_id)
                print str(thread_info.title) + " | " + str(thread_info.subreddit)
            except Exception as e:
                print e
        else:  # if not, it's just a subreddit
            subreddit_name = result[0]  # get subreddit name from regex group 1
            try:
                subreddit_title = reddit.get_subreddit(subreddit_name).title
                print ("http://www.reddit.com/r/" + subreddit_name + " - " + subreddit_title)
            except Exception as e:
                print ("http://www.reddit.com/r/" + subreddit_name + " - That's not a real subreddit...")
                print e
