#!/usr/bin/env python3
import re
import os
import praw
import json
import requests
from string import Template
from dotenv import load_dotenv

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

IMGUR_ALBUM_API_URL = 'https://api.imgur.com/3/album/${album_hash}/images'
IMGUR_GALLERY_API_URL = f''
DIRECT_LINK_TEMPLATE = '[#${index}](${image_link})  \nImage number ${index} from album ${album_link}'
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
    #print(f"Responding to comment: {c}")
    tokens = c.body.split()
    # If there's a command in the comment parse and react
    if len(tokens) > 1:
        if tokens[1].lower() == 'help':
            print("Help path")
            response_text = HELP_TEXT
        elif tokens[1].lower() == 'link':
            print("Link path")
            # TODO: Figure out what to do if we get a failure
            link_index_album = get_direct_image_link(c, tokens)
            image_link = link_index_album['image_link']
            index = link_index_album['index']
            album_link = link_index_album['album_link']
            s = Template(DIRECT_LINK_TEMPLATE)
            response_text = s.substitute(index=index, image_link=image_link, album_link=album_link)
        else:
            print("Fall through path")
            response_text = TODO_TEXT + HELP_TEXT
    # Otherwise print the help text
    else:
        response_text = HELP_TEXT
    if respond:
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


def get_direct_image_link(comment, tokens):
    """
    Gets the direct link to an image from an imgur album based on index.
    Tokens should look like: ['!MFAImageBot', 'link', '<imgur-link>', '<index>']
    """
    imgur_url = tokens[2]
    index = tokens[3]
    image_link = ''
    link_type_and_id = None

    try:
        link_type_and_id = parse_imgur_url(imgur_url)
    except ValueError:
        print(f"Oops, {imgur_url} is not a valid imgur link!") 
    r = None
    if link_type_and_id is not None:
        if link_type_and_id['type'] == 'album':
            # send request to album endpoint
            # TODO: Set client ID and secret for Imgur API?
            s = Template(IMGUR_ALBUM_API_URL)
            url = s.substitute(album_hash=link_type_and_id['id'])
            client_id = os.getenv('IMGUR_CLIENT_ID')
            headers = {'Authorization' : f'Client-ID {client_id}'}
            print(f"Request url: {url}")
            r = requests.get(url, headers=headers)
        elif link_type_and_id['type'] == 'gallery':
            # send request to gallery endpoint
            return None
        else: 
            return None

    # Verify that the index is an integer and in-bounds
    if r is not None and r.status_code == 200:
        # happy path for now
        r_json = r.json()
        image_link = r_json['data'][int(index)]['link']
        print(f'Image link: {image_link}')

    # Return direct link
    return {'image_link': image_link, 'index': index, 'album_link': imgur_url}

# Lol yanked this whole thing from SE
# https://codereview.stackexchange.com/questions/204316/imgur-url-parser
def parse_imgur_url(url):
    """
    Extract the type and id from an Imgur URL.

    >>> parse_imgur_url('http://imgur.com/a/cjh4E')
    {'id': 'cjh4E', 'type': 'album'}
    >>> parse_imgur_url('HtTP://imgur.COM:80/gallery/59npG')
    {'id': '59npG', 'type': 'gallery'}
    >>> parse_imgur_url('https://i.imgur.com/altd8Ld.png')
    {'id': 'altd8Ld', 'type': 'image'}
    >>> parse_imgur_url('https://i.stack.imgur.com/ELmEk.png')
    {'id': 'ELmEk', 'type': 'image'}
    >>> parse_imgur_url('http://not-imgur.com/altd8Ld.png') is None
    Traceback (most recent call last):
      ...
    ValueError: "http://not-imgur.com/altd8Ld.png" is not a valid imgur URL
    >>> parse_imgur_url('tftp://imgur.com/gallery/59npG') is None
    Traceback (most recent call last):
      ...
    ValueError: "tftp://imgur.com/gallery/59npG" is not a valid imgur URL
    >>> parse_imgur_url('Blah') is None
    Traceback (most recent call last):
      ...
    ValueError: "Blah" is not a valid imgur URL
    """
    match = re.match(
        r'^(?i:https?://(?:[^/:]+\.)?imgur\.com)(:\d+)?'
        r'/(?:(?P<album>a/)|(?P<gallery>gallery/))?(?P<id>\w+)',
        url
    )
    if not match:
        raise ValueError('"{}" is not a valid imgur URL'.format(url))
    return {
        'id': match.group('id'),
        'type': 'album' if match.group('album') else
                'gallery' if match.group('gallery') else
                'image',
    }

if __name__ == '__main__':
    r = praw.Reddit(UA)
    load_dotenv()

    for comment in r.subreddit(subreddit_name).stream.comments():
        if check_condition(comment):
            print(f"Comment hash: {comment}")
            # set 'respond=True' to activate bot responses. Must be logged in.
            # TODO: Set respond bool as CLI input value
            bot_action(comment, respond=False)