import csv
import datetime
import os
import random
import time
import traceback
from praw.models import Message
from multiprocessing import Process

import praw
from praw.exceptions import APIException

if os.environ.get('reddit_username') != 'jamiepullthatquote':
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

phrases = []
with open("resources/list.txt") as file:
    for line in file:
        phrases.append(line.strip())

triggers = []
with open("resources/triggers.txt") as file:
    for line in file:
        triggers.append(line.strip())

authors = {}
blacklist = {}
cooldown = 300


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


def check_pm(r):
    for pm in r.inbox.unread():
        if isinstance(pm, Message):
            frm = pm.author
            sub = pm.subject
            msg = pm.body

            print("PM from:", frm, "Subject:", sub, "Message:", msg)

            repsub = 'Re: ' + sub

            if "fuck off" in pm.body or "fuck off" in pm.subject:
                blacklist[pm.author] = time.time()
                wr = csv.writer(open("resources/blacklist.csv", "w"))
                for k, v in blacklist.items():
                    wr.writerow([k, v])
                reply = "you have been unsubscribed from joe rogan facts and will not be replied to again"
                pm.author.message(repsub, reply)
                pm.mark_read()
                print("Replied to PM with:", "\"", reply, "\"")


def run_bot(r):
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
                seconds_elapsed = (last_replied_post_timestamp + cooldown) - time.time()
                return seconds_elapsed > 0

        def check_author_blacklist_status(author):
            return author in blacklist

        def remaining_cooldown(author):
            if author in authors:
                timestamp = authors[author]
                return int(cooldown - (time.time() - timestamp))

        if post_not_replied(posts, comment.id) and any(
                word.lower() in comment.body.lower() for word in triggers or "!joe" in comment.body.lower()):
            if comment.created_utc > time.time() - 30:
                if check_author_cooldown_status(comment.author):
                    print(str(comment.author), "posted comment", comment.id, "but is in cooldown for another",
                          remaining_cooldown(comment.author), "seconds, doing nothing")
                elif check_author_blacklist_status(comment.author):
                    print(str(comment.author), "has asked to be blacklisted")
                else:
                    if comment.author != os.environ.get('reddit_username'):
                        print("Comment with trigger keyword posted by", str(comment.author), "to",
                              "https://reddit.com" + comment.submission.permalink + comment.id)
                        try:
                            if "!joe" in comment.body.lower():
                                random_phrase = random.choice(phrases)
                                comment.reply(
                                    ">\"*" + random_phrase.strip() + "*\" \n\n ^Joe ^Rogan \n\n --- \n\n [^^^Click "
                                                                     "^^^here ^^^to ^^^tell ^^^me ^^^to ^^^fuck "
                                                                     "^^^off ^^^and ^^^unsubscribe ^^^from ^^^Joe "
                                                                     "^^^Rogan's ^^^words ^^^of ^^^wisdom "
                                                                     "^^^forever]("
                                                                     "https://www.reddit.com/message/compose/?to=ckypop&subject=fuck%20off&message=fuck%20off)")
                                print("Replied to comment ", comment.id, "with", "\"",
                                      random_phrase.strip(), "\"")

                            else:
                                phrases_arr = []
                                for trigger in triggers:
                                    if trigger.lower() in comment.body.lower():
                                        for phrase in phrases:
                                            if trigger.lower() in phrase.lower():
                                                phrases_arr.append(phrase)
                                random_array_phrase = random.choice(phrases_arr)
                                comment.reply(
                                    ">\"*" + random_array_phrase + "*\" \n\n ^Joe ^Rogan  \n\n --- \n\n [^^^Click "
                                                                   "^^^here ^^^to ^^^tell ^^^me ^^^to ^^^fuck "
                                                                   "^^^off ^^^and ^^^unsubscribe ^^^from ^^^Joe "
                                                                   "^^^Rogan's ^^^words ^^^of ^^^wisdom "
                                                                   "^^^forever]("
                                                                   "https://www.reddit.com/message/compose/?to=ckypop&subject=fuck%20off&message=fuck%20off)")
                                print("Replied to comment", comment.id, "with", "\"",
                                      random_array_phrase, "\"")

                        except APIException as e:
                            traceback.print_exc(e)

                    save_cooldown()
                    save_posts()

            elif comment.created_utc < time.time() - 30:
                now = int(time.time())
                then = int(comment.created_utc)
                delta = now - then
                print(comment.id, "posted",
                      datetime.datetime.fromtimestamp(then).strftime('%H:%M:%S %d/%m/%Y') + ",",
                      delta, "seconds or", round(delta / 60, 1), "minutes ago")
                save_posts()


reddit = bot_login()


def main():
    Process(target=check_pm(reddit)).start()
    Process(target=run_bot(reddit)).start()


if __name__ == "__main__":
    main()
