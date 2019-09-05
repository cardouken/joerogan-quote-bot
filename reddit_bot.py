import traceback

import praw
from praw.exceptions import APIException
from praw.models import Message

import time
import random
import os

print("Currently listening in: " + os.environ['active_subreddit'])


def bot_login():
    print("Logging in as " + os.environ['reddit_username'])
    r = praw.Reddit(username=os.environ['reddit_username'],
                    password=os.environ['reddit_password'],
                    client_id=os.environ['client_id'],
                    client_secret=os.environ['client_secret'],
                    user_agent="Joe Rogan quote responder:v0.0.1 (by /u/picmip)")
    print("Logged in as " + os.environ['reddit_username'])

    return r


if not os.path.isfile("resources/posts_replied_to.txt"):
    posts_replied_to = []

else:
    # Read the file into a list and remove any empty values
    with open("resources/posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))


def run_bot(r):
    for pm in r.inbox.unread():
        if isinstance(pm, Message):
            frm = pm.author
            sub = pm.subject

            print("PM from: " + str(frm))
            print("Subject: " + sub)

            repsub = 'Re: ' + sub
            with open("resources/list.txt") as file:
                phrases = file.readlines()
            random_phrase = random.choice(phrases)
            msg = ">\"*" + random_phrase.strip() + "*\" \n\n ^Joe ^Rogan"
            pm.author.message(repsub, msg)
            pm.mark_read()
            print("Replied to PM with: " + "\"" + random_phrase.strip() + "\"")
    else:

        for comment in r.subreddit(os.environ['active_subreddit']).stream.comments():
            if comment.id not in posts_replied_to and "!joe" in comment.body.lower():
                print("Comment containing \"!joe\" posted by "
                      + str(comment.author)
                      + " to "
                      + "https://reddit.com"
                      + comment.submission.permalink
                      + comment.id)
                with open("resources/list.txt") as file:
                    phrases = file.readlines()
                random_phrase = random.choice(phrases)
                try:
                    comment.reply(">\"*" + random_phrase.strip() + "*\" \n\n ^Joe ^Rogan")
                    print("Replied to comment " + comment.id + " with " + "\"" + random_phrase.strip() + "\"")
                except APIException as e:
                    traceback.print_exc()
                posts_replied_to.append(comment.id)
        time.sleep(10)

        with open("resources/posts_replied_to.txt", "w") as f:
            for post_id in posts_replied_to:
                f.write(post_id + "\n")


r = bot_login()
while True:
    run_bot(r)
