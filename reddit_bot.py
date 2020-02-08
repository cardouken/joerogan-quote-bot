import os
import random
import time
import traceback

import praw
import psycopg2
from praw.exceptions import APIException
from praw.models import Message

blacklist = {}
posts = {}
cooldowns = {}
keywords_phrases = {}

if os.environ.get('reddit_username') != 'jamiepullthatquote':
    cooldown_time = int(os.environ['cooldown_dev'])
    comment_expiry_in_seconds = 120
    dev_env = "(DEVELOPMENT MODE)"
else:
    cooldown_time = int(os.environ['cooldown_time'])
    comment_expiry_in_seconds = 30
    dev_env = "(PRODUCTION MODE)"


def connect_to_db():
    return psycopg2.connect(
        database=os.environ['db_name'],
        user=os.environ['db_user'],
        password=os.environ['db_pw'],
        host=os.environ['db_host'],
        port=os.environ['db_port'])


def execute_db_query(sql):
    con = connect_to_db()
    cursor = con.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    con.commit()
    con.close()
    return data


def main():
    print("Currently listening in:", os.environ['active_subreddit'])

    print("Logging in as", os.environ.get('reddit_username'), dev_env)
    r = praw.Reddit(username=os.environ['reddit_username'],
                    password=os.environ['reddit_password'],
                    client_id=os.environ['client_id'],
                    client_secret=os.environ['client_secret'],
                    user_agent="Joe Rogan quote responder:v1.1")
    print("Logged in as", os.environ.get('reddit_username'), dev_env)
    print("Cooldown rate:", cooldown_time, "seconds &", "comment expiry:", comment_expiry_in_seconds, "seconds")

    fetch_keywords()
    fetch_replied_posts()
    fetch_blacklist()
    check_comments(r)


def check_comments(r):
    for comment in r.subreddit(os.environ['active_subreddit']).stream.comments():
        check_pm(r)
        user = comment.author
        user_not_self = comment.author != os.environ.get('reddit_username')
        comment_body = comment.body.lower()
        comment_is_new = comment.created_utc > time.time() - comment_expiry_in_seconds
        comment_url = "https://reddit.com" + comment.submission.permalink + comment.id
        comment_has_keyword_without_reply = comment.id not in posts.keys() and keyword_found_in_comment(comment_body)

        if not user_not_self and "ya yeet" in comment_body:
            parent = comment.parent()
            insert_to_blacklist(parent.author)

        if comment_has_keyword_without_reply and comment_is_new and user_not_self:
            if user_blacklisted(user):
                print(user, "requested to be blacklisted")
            elif user_in_cooldown(user):
                print(user, "posted", comment_url, "but is on cooldown for", remaining_cooldown(user))
            else:
                print("Keyword found, posted by", user, "at", comment_url)
                try:
                    if "!joe" in comment_body:
                        phrase = random.choice(keywords_phrases[random.choice(list(keywords_phrases.keys()))])
                        comment_reply(comment, phrase.strip())
                        print("Replied to comment", comment.id, "with:", phrase.strip())
                    else:
                        phrase = find_keyword_in_comment(comment_body)
                        comment_reply(comment, phrase)
                        print("Replied to comment", comment.id, "with:", phrase)

                except APIException as e:
                    traceback.print_exc(e)

            insert_posts(comment)
            cooldowns[comment.author] = time.time()


def check_pm(r):
    for pm in r.inbox.unread():
        if isinstance(pm, Message):
            user = pm.author
            subject = pm.subject
            message = pm.body

            print("PM from:", user, "Subject:", subject, "Message:", message)
            reply_subject = 'Re: ' + subject

            if "fuck off" in message or "fuck off" in subject:
                insert_to_blacklist(user)
                reply_message = "You have been unsubscribed from Joe Rogan's facts of life " \
                                "and will not be replied to again. \n" \
                                "If you decide to eventually reconsider your mistake, " \
                                "[click here](https://www.reddit.com/message/compose/?to=" \
                                + os.environ.get('reddit_username') + "&subject=im%20sorry&message=im%20sorry)"
                user.message(reply_subject, reply_message)
                pm.mark_read()
                print("Replied to PM with:", "\"" + reply_message + "\"")

            if "im sorry" in message or "im sorry" in subject and user_blacklisted(user):
                remove_from_blacklist(str(user))
                reply_message = "Welcome back freak bitches"
                user.message(reply_subject, reply_message)
                pm.mark_read()
                print("Replied to PM with:", "\"" + reply_message + "\"")


def comment_reply(comment, phrase):
    comment.reply(
        ">\"*" + str(phrase)
        + "*\" \n\n ^Joe ^Rogan  \n\n --- \n\n [^^^Click "
          "^^^here ^^^to ^^^tell ^^^me ^^^to ^^^get "
          "^^^lost ^^^or ^^^if ^^^something ^^^is "
          "^^^fucked]("
          "https://www.reddit.com/message/compose/?to=" + os.environ.get(
            'reddit_username') + "&subject=fuck%20off&message=fuck%20off)")


def keyword_found_in_comment(comment_body):
    for word in keywords_phrases.keys():
        if word.lower() in comment_body or "!joe" in comment_body:
            return True


def find_keyword_in_comment(comment_body):
    for word in keywords_phrases.keys():
        if word.lower() in comment_body:
            return keywords_phrases[word][random.randint(0, len(keywords_phrases[word]) - 1)]


def user_in_cooldown(author):
    if author in cooldowns:
        last_replied_post_timestamp = cooldowns[author]
        seconds_elapsed = (last_replied_post_timestamp + cooldown_time) - time.time()
        return seconds_elapsed > 0


def remaining_cooldown(author):
    if author in cooldowns:
        timestamp = cooldowns[author]
        return "{0} seconds".format(str(int(cooldown_time - (time.time() - timestamp))))


def user_blacklisted(author):
    return author in blacklist


def fetch_keywords():
    sql = "SELECT k.*, p.* " \
          "FROM keywords k " \
          "INNER JOIN keywords_phrases kp " \
          "ON kp.keyword_id = k.id " \
          "INNER JOIN phrases p " \
          "ON p.phrase = kp.phrase"
    data = execute_db_query(sql)

    for row in data:
        if row[1] not in keywords_phrases:
            keywords_phrases[row[1]] = []
        keywords_phrases[row[1]].append(row[2])

    print("Keyword and phrases list retrieved successfully")


def fetch_blacklist():
    sql = "SELECT username, blacklist FROM public.users"
    data = execute_db_query(sql)
    print("Blacklisted users fetched")

    for row in data:
        blacklist[row[0]] = time.time()
        print(row[0])


def fetch_replied_posts():
    sql = "SELECT post_id, timestamp FROM public.posts"
    data = execute_db_query(sql)
    print("Posts replied to fetched")

    for row in data:
        posts[row[0]] = time.time()


def insert_to_blacklist(user):
    blacklist[user] = time.time()
    sql = "INSERT INTO public.users(username, blacklist) VALUES (%s, %s)", (str(user), True)
    cursor = execute_db_query(sql)
    print(user, "blacklisted", cursor.rowcount)


def insert_posts(comment):
    posts[comment.id] = time.time()
    sql = "INSERT INTO public.posts(post_id, "'timestamp'") VALUES (%s, %s)", (comment.id, time.time())
    cursor = execute_db_query(sql)
    print(comment, "added to posts list, rows updated", cursor.rowcount)


def remove_from_blacklist(user):
    blacklist.pop(str(user))
    sql = "DELETE FROM public.users WHERE username = %s", [user]
    cursor = execute_db_query(sql)
    print(user, "removed from blacklist, rows updated", cursor.rowcount)


if __name__ == "__main__":
    main()
