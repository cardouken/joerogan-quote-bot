import csv
import datetime
import traceback

import praw
from praw.exceptions import APIException
from praw.models import Message

import time
import random
import os

if os.environ.get('reddit_username') == 'ckypop':
    devprod = "(DEV MODE)"
else:
    devprod = "(PRODUCTION LIVE)"

posts = {}
with open("posts.csv") as f:
    for line in f:
        if ',' not in line:
            continue
        (key, val) = line.strip().split(',')
        posts[key] = val

print(posts)
authors = {}
cooldown = 360


def bot_login():
    print("Currently listening in:", os.environ['active_subreddit'])
    print("Logging in as", os.environ.get('reddit_username'), devprod)
    r = praw.Reddit(username=os.environ['reddit_username'],
                    password=os.environ['reddit_password'],
                    client_id=os.environ['client_id'],
                    client_secret=os.environ['client_secret'],
                    user_agent="Joe Rogan quote responder:v0.0.1 (by /u/picmip)")
    print("Logged in as", os.environ.get('reddit_username'), devprod)
    return r


# if not os.path.isfile("resources/posts_replied_to.txt"):
#     posts_replied_to = []
#
# else:
#     # Read the file into a list and remove any empty values
#     with open("resources/posts_replied_to.txt", "r") as f:
#         posts_replied_to = f.read()
#         posts_replied_to = posts_replied_to.split("\n")
#         posts_replied_to = list(filter(None, posts_replied_to))


def run_bot(r):
    for pm in r.inbox.unread():
        if isinstance(pm, Message):
            frm = pm.author
            sub = pm.subject

            print("PM from: ", frm)
            print("Subject: ", sub)

            repsub = 'Re: ' + sub
            with open("resources/list.txt") as file:
                phrases = file.readlines()

            random_phrase = random.choice(phrases)
            msg = ">\"*", random_phrase.strip(), "*\" \n\n ^Joe ^Rogan"
            pm.author.message(repsub, msg)
            pm.mark_read()
            print("Replied to PM with:", "\"", random_phrase.strip(), "\"")
    else:
        for comment in r.subreddit(os.environ['active_subreddit']).stream.comments():
            def saveposts():
                posts[comment.id] = datetime.datetime.fromtimestamp(comment.created_utc).strftime('%H:%M:%S %d/%m/%Y')
                wr = csv.writer(open("posts.csv", "w"))
                for k, v in posts.items():
                    wr.writerow([k, v])

            def savecooldown():
                authors[comment.author] = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S %d/%m/%Y')
                wr = csv.writer(open("cooldowns.csv", "w"))
                for key, val in authors.items():
                    wr.writerow([key, val])

            def checkkey(posts, key):
                if key in posts.keys():
                    return True
                else:
                    return False

            def timestampkey(authors, key):
                if key in authors.keys():
                    return datetime.datetime.timestamp(key)
                else:
                    pass

            if not checkkey(posts,
                            comment.id) and "!joe" in comment.body.lower() and comment.created_utc < time.time() - 30:
                if comment.author in authors and int(timestampkey(authors, comment.id)) > int(time.time() - cooldown):
                    print(str(comment.author), "in cooldown for", str(
                        authors.get(comment.author) - int(time.time() - cooldown)) + " seconds")
                    pass

                else:

                    print("Comment containing \"!joe\" posted by", str(comment.author), "to",
                          "https://reddit.com" + comment.submission.permalink + comment.id)
                    with open("resources/list.txt") as file:
                        phrases = file.readlines()
                    random_phrase = random.choice(phrases)

                    try:
                        comment.reply(">\"*" + random_phrase.strip() + "*\" \n\n ^Joe ^Rogan")
                        print("Replied to comment ", comment.id, "with", "\"", random_phrase.strip(), "\"")
                    except APIException as e:
                        traceback.print_exc(e)

                    savecooldown()
                    saveposts()

            elif checkkey(posts,
                          comment.id) and "!joe" in comment.body.lower() and comment.created_utc < time.time() - 30:
                now = int(time.time())
                then = int(comment.created_utc)
                delta = now - then
                print(comment.id, "posted", datetime.datetime.fromtimestamp(then).strftime('%H:%M:%S %d/%m/%Y') + ",",
                      delta, "seconds or", round(delta / 60, 1), "minutes ago")
                saveposts()


r = bot_login()
while True:
    run_bot(r)
