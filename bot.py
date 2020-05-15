#!/usr/bin/env python3
import re
import praw

# Provide a descriptive user-agent string. Explain what your bot does, reference
# yourself as the author, and offer some preferred contact method. A reddit
# username is sufficient, but nothing wrong with adding an email in here.
UA = 'MFAImageBot'
HELP_TEXT = """
Usage: I respond to comments starting with `!MFAImageBot`.  \n
`!MFAImageBot help`: Print this help message.  \n
`!MFAImageBot link <album-link> <number>`: Attempts to directly link the <number> image from <album-link>  \n
`!MFAImageBot link <number>`: Attempts to directly link the <number> image from the album in the submission  \n
"""
TODO_TEXT = """
Sorry, this function has not been implemented yet.\n\n
"""
subreddit_name = "mybottestenvironment"
#subreddit_name = "goodyearwelt"
bot_batsignal = '!MFAImageBot'
tail = "\n\nI am a bot."

def check_condition(c):
    """
    Checks to see if the text body of a comment starts with the bat signal.

    If it does, we want to try and process the comment and respond to it.
    """
    text = c.body
    return text.startswith(bot_batsignal)

def bot_action(c, verbose=True, respond=False):
    response_text = 'bot_action text'
    if respond:
        print(f"Responding to comment: {c}")
        tokens = c.body.split()
        # If there's a command in the comment parse and react
        if len(tokens) > 1:
            if tokens[1].lower() == 'help':
                print("Help path")
                response_text = HELP_TEXT
            elif tokens[1].lower() == 'link':
                print("Link path")
                response_text = TODO_TEXT + HELP_TEXT
            else:
                print("Fall through path")
                response_text = TODO_TEXT + HELP_TEXT
        # Otherwise print the help text
        else:
            response_text = HELP_TEXT
        c.reply(response_text + tail)
    
    # Logging
    if verbose:
        tokens = c.body.encode("UTF-8").split()
        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Comment Body: ")
        print(c.body.encode("UTF-8"))
        print(f"Tokens: {tokens}")
        print("Response comment body: ")
        print(response_text.encode("UTF-8"))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

if __name__ == '__main__':
    r = praw.Reddit(UA)

    for comment in r.subreddit(subreddit_name).stream.comments():
        print(f"Comment hash: {comment}")
        if check_condition(comment):
            # set 'respond=True' to activate bot responses. Must be logged in.
            bot_action(comment, respond=True)