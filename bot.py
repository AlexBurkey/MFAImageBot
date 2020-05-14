#!/usr/bin/env python3
import re
import praw

# Provide a descriptive user-agent string. Explain what your bot does, reference
# yourself as the author, and offer some preferred contact method. A reddit
# username is sufficient, but nothing wrong with adding an email in here.
UA = 'MFAImageBot'
subreddit_name = "mybottestenvironment"
#subreddit_name = "goodyearwelt"
bot_batsignal = '!MFAImageBot'
tail = "\n\nI am a bot."

def check_condition(c):
    text = c.body
    return text.startswith(bot_batsignal)

def bot_action(c, verbose=True, respond=False):
    response_text = 'bot_action text'
    # Logging
    if verbose:
        print(c.body.encode("UTF-8"))
        print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
        print(response_text.encode("UTF-8"))

    if respond:
        print(f"Responding to comment: {c}")
        c.reply(response_text + tail)

if __name__ == '__main__':
    r = praw.Reddit(UA)

    
    for comment in r.subreddit(subreddit_name).stream.comments():
        print(f"Comment hash: {comment}")
        if check_condition(comment):
            # set 'respond=True' to activate bot responses. Must be logged in.
            bot_action(comment, respond=True)