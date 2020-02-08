import csv
import datetime
import os
import random
import time
import traceback

import praw
from praw.exceptions import APIException
from praw.models import Message

authors = {}
blacklist = {}
cooldown = 300


def main():
    if os.environ.get('reddit_username') != 'jamiepullthatquote':
        devprod = "(DEVELOPMENT MODE)"
    else:
        devprod = "(PRODUCTION MODE)"

    get_posts()
    get_phrases()
    get_triggers()

    print("Currently listening in:", os.environ['active_subreddit'])
    print("Logging in as", os.environ.get('reddit_username'), devprod)
    r = praw.Reddit(username=os.environ['reddit_username'],
                    password=os.environ['reddit_password'],
                    client_id=os.environ['client_id'],
                    client_secret=os.environ['client_secret'],
                    user_agent="Joe Rogan quote responder:v1.0.1 (by /u/picmip)")
    print("Logged in as", os.environ.get('reddit_username'), devprod)
    run_bot(r)


def run_bot(r):
    for comment in r.subreddit(os.environ['active_subreddit']).stream.comments():
        check_pm(r)
        user = comment.author
        cbody = comment.body.lower()
        comment_newer_than_30sec = comment.created_utc > time.time() - 30
        comment_older_than_30sec = comment.created_utc < time.time() - 30
        user_not_self = user != os.environ.get('reddit_username')
        comment_url = "https://reddit.com" + comment.submission.permalink + comment.id
        comment_has_keyword_without_reply = comment.id not in posts.keys() and keyword_found_in_comment(cbody)

        if comment_has_keyword_without_reply and comment_newer_than_30sec:
            if user_blacklisted(user):
                print(user, "has asked to be blacklisted")
            elif user_in_cooldown(user):
                print(user, "posted", comment.id, "but is in cooldown for", remaining_cooldown(user), "seconds")
            else:
                if user_not_self:
                    print("Keyword found posted by", user, "at", comment_url)
                    try:
                        if "!joe" in cbody:
                            random_phrase = random.choice(phrases)
                            comment_reply_random(comment, random_phrase)
                            print("Replied to comment", comment.id, "with:", random_phrase.strip())
                        else:
                            phrases_arr = []
                            find_keyword_in_comment(cbody, phrases_arr)
                            random_array_phrase = random.choice(phrases_arr)
                            comment_reply(comment, random_array_phrase)
                            print("Replied to comment", comment.id, "with:", random_array_phrase)

                    except APIException as e:
                        traceback.print_exc(e)

                save_cooldown(comment)
                save_posts(comment)


def check_pm(r):
    for pm in r.inbox.unread():
        if isinstance(pm, Message):
            frm = pm.author
            sub = pm.subject
            msg = pm.body

            print("PM from:", frm, "Subject:", sub, "Message:", msg)
            repsub = 'Re: ' + sub

            if "fuck off" in msg or "fuck off" in sub:
                blacklist_user(frm)
                reply = "you have been unsubscribed from joe rogan facts and will not be replied to again"
                frm.message(repsub, reply)
                pm.mark_read()
                print("Replied to PM with:", "\"", reply, "\"")


def save_posts(comment):
    posts[comment.id] = time.time()
    wr = csv.writer(open("resources/posts.csv", "w"))
    for k, v in posts.items():
        wr.writerow([k, v])


def save_cooldown(comment):
    authors[comment.author] = time.time()
    wr = csv.writer(open("resources/cooldowns.csv", "w"))
    for k, v in authors.items():
        wr.writerow([k, v])


def clear_authors(comment):
    authors.clear()
    save_cooldown(comment)


def clear_blacklist():
    blacklist.clear()


def user_in_cooldown(author):
    if author in authors:
        last_replied_post_timestamp = authors[author]
        seconds_elapsed = (last_replied_post_timestamp + cooldown) - time.time()
        return seconds_elapsed > 0


def user_blacklisted(author):
    return author in blacklist


def remaining_cooldown(author):
    if author in authors:
        timestamp = authors[author]
        return int(cooldown - (time.time() - timestamp))


def blacklist_user(frm):
    blacklist[frm] = time.time()
    w = csv.writer(open("resources/blacklist.csv", "w"))
    for k, v in blacklist.items():
        w.writerow([k, v])


def keyword_found_in_comment(cbody):
    return any(word.lower() in cbody for word in triggers or "!joe" in cbody)


def find_keyword_in_comment(cbody, phrases_arr):
    for trigger in triggers:
        if trigger.lower() in cbody:
            for phrase in phrases:
                if trigger.lower() in phrase.lower():
                    phrases_arr.append(phrase)


def comment_reply_random(comment, random_phrase):
    comment.reply(
        ">\"*" + random_phrase.strip()
        + "*\" \n\n ^Joe ^Rogan \n\n --- \n\n [^^^Click "
          "^^^here ^^^to ^^^tell ^^^me ^^^to ^^^fuck "
          "^^^off ^^^and ^^^unsubscribe ^^^from ^^^Joe "
          "^^^Rogan's ^^^words ^^^of ^^^wisdom "
          "^^^forever]("
          "https://www.reddit.com/message/compose/?to=jamiepullthatquote&subject=fuck%20off&message=fuck%20off)")


def comment_reply(comment, random_array_phrase):
    comment.reply(
        ">\"*" + random_array_phrase
        + "*\" \n\n ^Joe ^Rogan  \n\n --- \n\n [^^^Click "
          "^^^here ^^^to ^^^tell ^^^me ^^^to ^^^fuck "
          "^^^off ^^^and ^^^unsubscribe ^^^from ^^^Joe "
          "^^^Rogan's ^^^words ^^^of ^^^wisdom "
          "^^^forever]("
          "https://www.reddit.com/message/compose/?to=jamiepullthatquote&subject=fuck%20off&message=fuck%20off)")


def get_posts():
    global posts, line
    posts = {}
    with open("resources/posts.csv") as f:
        for line in f:
            if ',' not in line:
                continue
            (key, val) = line.strip().split(',')
            posts[key] = val


def get_phrases():
    global phrases, file, line
    phrases = []
    with open("resources/list.txt") as file:
        for line in file:
            phrases.append(line.strip())


def get_triggers():
    global triggers, file, line
    triggers = []
    with open("resources/triggers.txt") as file:
        for line in file:
            triggers.append(line.strip())


if __name__ == "__main__":
    main()
