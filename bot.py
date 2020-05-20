#!/usr/bin/env python3
import re
import os
import praw
import json
import requests
from string import Template
from dotenv import load_dotenv

#References praw-ini file
UA = 'MFAImageBot'
HELP_TEXT = ("Usage: I respond to comments starting with `!MFAImageBot`.  \n"
                "`!MFAImageBot help`: Print this help message.  \n"
                "`!MFAImageBot link <album-link> <number>`: Attempts to directly link the <number> image from <album-link>  \n"
                "`!MFAImageBot link <number>`: Attempts to directly link the <number> image from the album in the submission  \n"
            )
TODO_TEXT = "Sorry, this function has not been implemented yet.\n\n"

IMGUR_ALBUM_API_URL = 'https://api.imgur.com/3/album/${album_hash}/images'
IMGUR_GALLERY_API_URL = f''
DIRECT_LINK_TEMPLATE = '[#${index}](${image_link})  \nImage number ${index} from album ${album_link}'
SUBREDDIT_NAME = "mybottestenvironment"
#subreddit_name = "goodyearwelt"
BATSIGNAL = '!MFAImageBot'
TAIL = ("\n\n---\nI am a bot! If you've found a bug you can open an issue "
        "[here.](https://github.com/AlexBurkey/MFAImageBot/issues/new?template=bug_report.md)  \n"
        "If you have an idea for a feature, you can submit the idea "
        "[here](https://github.com/AlexBurkey/MFAImageBot/issues/new?template=feature_request.md)")

def check_condition(c):
    """
    Checks to see if the text body of a comment starts with the bat signal.

    If it does, we want to try and process the comment and respond to it.
    """
    text = c.body
    return text.startswith(BATSIGNAL)

def bot_action(c, verbose=True, respond=False):
    response_text = 'bot_action text'
    tokens = c.body.split()
    # If there's a command in the comment parse and react
    # Break this out into a "parse_comment_tokens" function
    #   Alternatively "set_response_text" or something
    if len(tokens) > 1:
        if tokens[1].lower() == 'help':
            print("Help path")
            response_text = HELP_TEXT
        elif tokens[1].lower() == 'link':
            print("Link path")
            # TODO: Wrapping the whole thing in a try-catch is a code smell
            try: 
                link_index_album = get_direct_image_link(c, tokens)
                image_link = link_index_album['image_link']
                index = link_index_album['index']
                album_link = link_index_album['album_link']
                s = Template(DIRECT_LINK_TEMPLATE)
                response_text = s.substitute(index=index, image_link=image_link, album_link=album_link)
            except ValueError as e:
                print(str(e))
                response_text = str(e) + TAIL
            except IndexError:
                response_text = 'Sorry that index is out of bounds.' + TAIL
        else:
            print("Fall through path")
            response_text = TODO_TEXT + HELP_TEXT
    # Otherwise print the help text
    else:
        response_text = HELP_TEXT
    
    if respond:
        c.reply(response_text + TAIL)
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
    if len(tokens) < 4:
        print('Not enough parameters for `link` command.')
        raise ValueError('Not enough parameters for `link` command.')
    imgur_url = tokens[2]
    image_link = ''
    # Wrap this in a try-except because I don't like the error message
    try:
        index = int(tokens[3])
    except ValueError:
        raise ValueError(f'Sorry, "{tokens[3]}" doesn\'t look like an integer to me.')

    # This raises an exception and is fine
    link_type_and_id = parse_imgur_url(imgur_url)
    r = None
    if link_type_and_id is not None:
        # Each type of Imgur resource has its own endpoint: album vs gallery
        #   so we send requests separately
        if link_type_and_id['type'] == 'album':
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

    # TODO: Verify that the index is an integer and in-bounds
    # TODO: The structure of galleries and albums is different
    # Gallery: g_response.data.images[index].link
    # Album: a_response.data[index].link
    if r is not None and r.status_code == 200:
        # happy path for now
        r_json = r.json()
        image_link = r_json['data'][index]['link']
        print(f'Image link: {image_link}')
        return {'image_link': image_link, 'index': index, 'album_link': imgur_url}
    else:  # Status code not 200
        print(f'Status Code: {r.status_code}')
        raise ValueError(f'Sorry, {imgur_url} is probably not an existing imgur album.')
    

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
        raise ValueError('Sorry, "{}" is not a valid imgur URL'.format(url))
    return {
        'id': match.group('id'),
        'type': 'album' if match.group('album') else
                'gallery' if match.group('gallery') else
                'image',
    }

if __name__ == '__main__':
    r = praw.Reddit(UA)
    load_dotenv()  # Used for imgur auth

    for comment in r.subreddit(SUBREDDIT_NAME).stream.comments():
        if check_condition(comment):
            print(f"Comment hash: {comment}")  # TODO: offload this and check the comment before responding
            # set 'respond=True' to activate bot responses. Must be logged in.
            # TODO: Set respond bool as CLI input value
            bot_action(comment, respond=False)