import praw
import re

reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW

message = "this is cool: https://www.reddit.com/r/iRacing/comments/3vmdc2/i_want_to_feel_the_engine_any_way_to_manually/"

regexSearch = re.findall("[r][/][a-z0-9_]+", message, flags=re.IGNORECASE)
if regexSearch:  # if this is true, we found a subreddit name
    # now we want to see if this is a thread, instead of a whole subreddit
    regex_search2 = re.findall("[/]comments[/][a-z0-9]+[/]", message, flags=re.IGNORECASE)
    if regex_search2:  # if this is true, a thread was linked
        for thread in regex_search2:
            thread_id = thread.split("comments/")[1].strip("/")  # get rid of "comments/" and the trailing "/"
            try:
                thread_info = reddit.get_submission(submission_id=thread_id)
                print str(thread_info.title) + " - " + str(thread_info.subreddit)
            except Exception as e:
                print e
    else:  # otherwise, only a subreddit was mentioned
        for sub in regexSearch:  # for each subreddit mentioned, print
            subreddit_name = sub.split("r/")[1]  # this contains the subreddit name
            try:
                subreddit_title = reddit.get_subreddit(subreddit_name).title
                print ("http://www.reddit.com/r/" + subreddit_name + " - " + subreddit_title)
            except Exception as e:
                print ("http://www.reddit.com/r/" + subreddit_name + " - That's not a real subreddit...")
                print e
