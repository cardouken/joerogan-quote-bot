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
with open("resources/posts.csv") as f:
    for line in f:
        if ',' not in line:
            continue
        (key, val) = line.strip().split(',')
        posts[key] = val
print(posts)

with open("resources/list.txt") as file:
    phrases = file.readlines()

authors = {}
cooldown = 30


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


def run_bot(r):
    def check_pm():
        for pm in r.inbox.unread():
            if isinstance(pm, Message):
                frm = pm.author
                sub = pm.subject

                print("PM from: ", frm)
                print("Subject: ", sub)

                repsub = 'Re: ' + sub
                random_phrase_pm = random.choice(phrases)
                msg = ">\"*" + random_phrase_pm.strip() + "*\" \n\n ^Joe ^Rogan"
                pm.author.message(repsub, msg)
                pm.mark_read()
                print("Replied to PM with:", "\"", random_phrase_pm.strip(), "\"")

    for comment in r.subreddit(os.environ['active_subreddit']).stream.comments():
        def save_posts():
            posts[comment.id] = time.time()
            wr = csv.writer(open("resources/posts.csv", "w"))
            for k, v in posts.items():
                wr.writerow([k, v])

        def save_cooldown():
            authors[comment.author] = time.time()
            wr = csv.writer(open("resources/cooldowns.csv", "w"))
            for k, v in authors.items():
                wr.writerow([k, v])

        def post_not_replied(posts, post_id):
            return post_id not in posts.keys()

        def check_author_cooldown_status(author):
            if author in authors:
                last_replied_post_timestamp = authors[author]
                secondselapsed = (last_replied_post_timestamp + cooldown) - time.time()
                return secondselapsed > 0

        def get_cooldown_time_remaining(author):
            if author in authors:
                timestamp = authors[author]
                return int(cooldown - (time.time() - timestamp))

        def should_reply():
            return post_not_replied(posts, comment.id) \
                   and "!joe" in comment.body.lower() \
                   and comment_is_new()

        def comment_is_new():
            return comment.created_utc > time.time() - 30

        if should_reply():
            if check_author_cooldown_status(comment.author):
                print(str(comment.author), "posted comment", comment.id, "but is in cooldown for another",
                      get_cooldown_time_remaining(comment.author), "seconds, doing nothing")
                pass
            else:
                print("Comment containing \"!joe\" posted by", str(comment.author), "to",
                      "https://reddit.com" + comment.submission.permalink + comment.id)
                try:
                    random_phrase = random.choice(phrases)
                    comment.reply(">\"*" + random_phrase.strip() + "*\" \n\n ^Joe ^Rogan")
                    print("Replied to comment ", comment.id, "with", "\"", random_phrase.strip(), "\"")
                except APIException as e:
                    traceback.print_exc(e)

                save_cooldown()
                save_posts()

        elif should_reply():
            now = int(time.time())
            then = int(comment.created_utc)
            delta = now - then
            print(comment.id, "posted", datetime.datetime.fromtimestamp(then).strftime('%H:%M:%S %d/%m/%Y') + ",",
                  delta, "seconds or", round(delta / 60, 1), "minutes ago")
            save_posts()

        check_pm()


reddit = bot_login()

while True:
    run_bot(reddit)
