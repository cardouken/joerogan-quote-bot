import csv
import os
import random
import time
import traceback

import praw
from praw.exceptions import APIException
from praw.models import Message

blacklist = {}
posts = {}
cooldowns = {}
keywords = []
phrases = []

if os.environ.get('reddit_username') != 'jamiepullthatquote':
    cooldown_time = int(os.environ['cooldown_dev'])
    dev_env = "(DEVELOPMENT MODE)"
else:
    cooldown_time = int(os.environ['cooldown_time'])
    dev_env = "(PRODUCTION MODE)"


def main():
    print("Currently listening in:", os.environ['active_subreddit'])
    print("Logging in as", os.environ.get('reddit_username'), dev_env)
    r = praw.Reddit(username=os.environ['reddit_username'],
                    password=os.environ['reddit_password'],
                    client_id=os.environ['client_id'],
                    client_secret=os.environ['client_secret'],
                    user_agent="Joe Rogan quote responder:v1.1")
    print("Logged in as", os.environ.get('reddit_username'), dev_env)
    load_resources()
    check_comments(r)


def check_comments(r):
    for comment in r.subreddit(os.environ['active_subreddit']).stream.comments():
        check_pm(r)
        user = comment.author
        user_not_self = user != os.environ.get('reddit_username')
        comment_body = comment.body.lower()
        comment_newer_than_30sec = comment.created_utc > time.time() - 30
        comment_url = "https://reddit.com" + comment.submission.permalink + comment.id
        comment_has_keyword_without_reply = comment.id not in posts.keys() and keyword_found_in_comment(comment_body)

        if comment_has_keyword_without_reply and comment_newer_than_30sec and user_not_self:
            if user_blacklisted(user):
                print(user, "has asked to be blacklisted")
            elif user_in_cooldown(user):
                print(user, "posted", comment_url, "but is in cooldown for", remaining_cooldown(user))
            else:
                print("Keyword found, posted by", user, "at", comment_url)
                try:
                    if "!joe" in comment_body:
                        phrase = random.choice(phrases)
                        comment_reply(comment, phrase.strip())
                        print("Replied to comment", comment.id, "with:", phrase.strip())
                    else:
                        phrases_arr = []
                        find_keyword_in_comment(comment_body, phrases_arr)
                        phrase = random.choice(phrases_arr)
                        comment_reply(comment, phrase)
                        print("Replied to comment", comment.id, "with:", phrase)

                except APIException as e:
                    traceback.print_exc(e)

            save_cooldown(comment)
            save_posts(comment)


def check_pm(r):
    for pm in r.inbox.unread():
        if isinstance(pm, Message):
            user = pm.author
            subject = pm.subject
            message = pm.body

            print("PM from:", user, "Subject:", subject, "Message:", message)
            reply_subject = 'Re: ' + subject

            if "fuck off" in message or "fuck off" in subject:
                save_blacklist(user)
                reply_message = "you have been unsubscribed from joe rogan facts and will not be replied to again"
                user.message(reply_subject, reply_message)
                pm.mark_read()
                print("Replied to PM with:", "\"", reply_message, "\"")


def comment_reply(comment, phrase):
    comment.reply(
        ">\"*" + phrase
        + "*\" \n\n ^Joe ^Rogan  \n\n --- \n\n [^^^Click "
          "^^^here ^^^to ^^^tell ^^^me ^^^to ^^^get "
          "^^^lost ^^^or ^^^if ^^^something ^^^is "
          "^^^fucked]("
          "https://www.reddit.com/message/compose/?to=" + os.environ.get(
            'reddit_username') + "&subject=fuck%20off&message=fuck%20off)")


def keyword_found_in_comment(comment_body):
    return any(word.lower() in comment_body for word in keywords or "!joe" in comment_body)


def find_keyword_in_comment(comment_body, phrases_arr):
    for word in keywords:
        if word.lower() in comment_body:
            for phrase in phrases:
                if word.lower() in phrase.lower():
                    phrases_arr.append(phrase)


def save_posts(comment):
    posts[comment.id] = time.time()
    wr = csv.writer(open("resources/posts.csv", "w"))
    for k, v in posts.items():
        wr.writerow([k, v])


def save_cooldown(comment):
    cooldowns[comment.author] = time.time()
    wr = csv.writer(open("resources/cooldowns.csv", "w"))
    for k, v in cooldowns.items():
        wr.writerow([k, v])


def save_blacklist(user):
    blacklist[user] = time.time()
    w = csv.writer(open("resources/blacklist.csv", "w"))
    for k, v in blacklist.items():
        w.writerow([k, v])


def user_in_cooldown(author):
    if author in cooldowns:
        last_replied_post_timestamp = cooldowns[author]
        seconds_elapsed = (last_replied_post_timestamp + cooldown_time) - time.time()
        return seconds_elapsed > 0


def remaining_cooldown(author):
    if author in cooldowns:
        timestamp = cooldowns[author]
        return str(int(cooldown_time - (time.time() - timestamp))) + " seconds"


def user_blacklisted(author):
    return author in blacklist


def clear_cooldowns(comment):
    cooldowns.clear()
    save_cooldown(comment)


def clear_blacklist():
    blacklist.clear()


def load_resources():
    with open("resources/cooldowns.csv") as file:
        for line in file:
            if ',' not in line:
                continue
            (key, val) = line.strip().split(',')
            cooldowns[key] = val

    with open("resources/keywords.txt") as file:
        for line in file:
            keywords.append(line.strip())

    with open("resources/list.txt") as file:
        for line in file:
            phrases.append(line.strip())

    with open("resources/posts.csv") as f:
        for line in f:
            if ',' not in line:
                continue
            (key, val) = line.strip().split(',')
            posts[key] = val

    with open("resources/blacklist.csv") as file:
        for line in file:
            if ',' not in line:
                continue
            (key, val) = line.strip().split(',')
            blacklist[key] = val
            print("Blacklist:", blacklist)


if __name__ == "__main__":
    main()
