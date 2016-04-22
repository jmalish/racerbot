import praw
import re

reddit = praw.Reddit(user_agent="racer0940")  # used to access reddit's API with PRAW

message = "this comment here https://www.reddit.com/r/SmarterEveryDay/comments/4fstkg/thoughts_on_a_podcast/d2bzsa5"

reddit_regex = \
    re.findall("([A-z_0-9]*)?(\/comments\/)([A-z_0-9]{6})(\/[A-z_0-9-]*)?(\/([A-z_0-9]{7}))?",
               message, flags=re.IGNORECASE)

for result in reddit_regex:
    if result[5]:  # if result[5] has something in it, that means we have a comment
        try:
            reddit_link = "https://www.reddit.com/comments/%s/_/%s" % (result[2], result[5])
            submission = reddit.get_submission(reddit_link)
            print "%s commented on %s" % (submission.comments[0].author, submission.title)
        except Exception as error:
            print error
