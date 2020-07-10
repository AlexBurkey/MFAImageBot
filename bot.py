#!/usr/bin/env python3
import re
import os
import sys
import praw
import json
import sqlite3
import requests
from string import Template
from dotenv import load_dotenv
import my_strings as ms
import helpers as h


# References praw-ini file
BATSIGNAL = '!mfaimagebot'
IMGUR_ALBUM_API_URL = 'https://api.imgur.com/3/album/${album_hash}/images'
IMGUR_GALLERY_API_URL = 'https://api.imgur.com/3/gallery/album/${gallery_hash}'
DIRECT_LINK_TEMPLATE = '[Direct link to image #${index}](${image_link})  \nImage number ${index} from album ${album_link}'

def run():
    r = praw.Reddit(USER_AGENT)
    load_dotenv()  # Used for imgur auth
    # TODO: verify that the db path is valid.
    #   A single file is fine but dirs are not created if they don't exist
    print("Looking for comments...")
    for comment in r.subreddit(SUBREDDIT_NAME).stream.comments():
        if check_batsignal(comment.body) and not check_has_responded(comment):
            response = ms.HELP_TEXT
            tokens = h.get_and_split_first_line(comment.body)
            # More than 100 tokens on the first line. 
            # I'm not dealing with that
            if len(tokens) > 100:
                db_obj = h.reply_and_upvote(comment, response=ms.HELP_TEXT, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue

            # Check for help
            if parse_comment(tokens)['help']:
                db_obj = h.reply_and_upvote(comment, response=ms.HELP_TEXT, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue

            index = parse_comment(tokens)['index']
            if index == -1:
                db_obj = h.reply_and_upvote(comment, response=ms.HELP_TEXT, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue

            # TODO: Wrap/deal with possible exceptions from parsing imgur url
            comment_imgur_url = parse_comment(tokens)['imgur_url']
            
            # Check/parse imgur
            album_link_map = None
            album_link = None
            if comment_imgur_url is not None:
                album_link_map = parse_imgur_url(comment_imgur_url)
                album_link = comment_imgur_url
            elif h.is_imgur_url(comment.submission.url):
                album_link_map = parse_imgur_url(comment.submission.url)
                album_link = comment.submission.url
            else:
                # No imgur link found. Respond
                response = 'Sorry, no imgur link found in your comment or the link of the OP.'
                db_obj = h.reply_and_upvote(comment, response=response, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue
            
            album_link_type = album_link_map['type']
            album_link_id   = album_link_map['id']
            
            # TODO: Wrap in try/except
            request_url = build_request_url(album_link_type, album_link_id)
            
            r = send_imgur_api_request(request_url)
            if r is not None and r.status_code == 200:
                response = None
                image_link = None
                try:
                    # Parse request and set response text
                    image_link = get_direct_image_link(r.json(), album_link_type, index)
                    s = Template(DIRECT_LINK_TEMPLATE)
                    response = s.substitute(index=index, image_link=image_link, album_link=album_link)
                except IndexError:
                    response = 'Sorry that index is out of bounds.'
                db_obj = h.reply_and_upvote(comment, response=response, respond=RESPOND)
                add_comment_to_db(db_obj)
                print(f"Request url: {request_url}")
                print(f'Image link: {image_link}')
                continue 
            else:  # Status code not 200
                # TODO: Deal with status codes differently, like if imgur is down or I don't have the env configured
                print(f'Status Code: {r.status_code}')
                response = f'Sorry, {album_link} is probably not an existing imgur album, or Imgur is down.'
                db_obj = h.reply_and_upvote(comment, response=response, respond=RESPOND)
                add_comment_to_db(db_obj)
                print(f"Request url: {request_url}")
                continue


def check_batsignal(comment_body):
    """
    Returns True if the comment body starts with the batsignal '!mfaimagebot'. Otherwise False.
    Case insensitive.

    >>> check_batsignal('!MFAImageBot test')
    True
    >>> check_batsignal('!mfaimagebot test')
    True
    >>> check_batsignal('!MfAiMaGeBoT test')
    True
    >>> check_batsignal(' !MFAImageBot test')
    False
    >>> check_batsignal('!Test test')
    False
    >>> check_batsignal('?MFAImageBot test')
    False
    """
    text = comment_body.lower()
    return text.startswith(BATSIGNAL)


def check_has_responded(comment):
    """
    Returns True if the comment hash is in the database and we've already responded to it. Otherwise False.

    fetchone() is not None --> a row exists
    a row exists iff hash is in DB AND we have responded to it.
    """
    # TODONE: Using 0 (false) for has_responded will probably be a better query
    #       since the DB should really only keep comments we have responded to
    # UPDATE: We keep all comments in the DB, but update the value if responded.
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT * FROM comments WHERE comment_hash=:hash AND has_responded=1', {"hash": comment.id})
    val = (cur.fetchone() is not None)
    conn.close()
    return val


def parse_comment(tokens):
    pairs = {'index': -1, 'imgur_url': None, 'help': False}
    # Find the numbers in the tokens
    for s in tokens:
        # Look for help
        if s.lower() == 'help':
            pairs['help'] = True
            break
        # Find the numbers in the tokens
        if h.isInt(s):
            pairs['index'] = int(s)
        # Find imgur URL in the tokens
        if h.is_imgur_url(s):
            pairs['imgur_url'] = s
    return pairs


def build_request_url(imgur_link_type, imgur_link_id):
    """
    Create the Imgur Request URL.
    Imgur Galleries and Albums have different endpoints.
    Any other resource type hasn't been implemented/might not exist.
    TODO: doctests
    """
    if imgur_link_type == 'album':
        s = Template(IMGUR_ALBUM_API_URL)
        return s.substitute(album_hash=imgur_link_id)
    elif imgur_link_type == 'gallery':
        s = Template(IMGUR_GALLERY_API_URL)
        return s.substitute(gallery_hash=imgur_link_id)
    else:
        raise ValueError('Sorry, that imgur resource hasn\'t been implemented yet.')


def send_imgur_api_request(request_url):
    """
    Send API request to Imgur
    TODO: doctests
    """
    # Send the request
    client_id = os.getenv('IMGUR_CLIENT_ID')
    headers = {'Authorization': f'Client-ID {client_id}'}
    return requests.get(request_url, headers=headers)


def bot_action(c, verbose=True, respond=False):
    response_text = 'bot_action text'
    response_type = None
    # TODO: Get the first line only
    tokens = c.body.split()
    # If there's a command in the comment parse and react
    # Break this out into a "parse_comment_tokens" function
    #   Alternatively "set_response_text" or something
    if len(tokens) > 1:
        response_type = tokens[1].lower()
        if response_type == 'help':
            response_text = ms.HELP_TEXT
        elif response_type == 'link' or response_type == 'op':
            # TODO: Wrapping the whole thing in a try-catch is a code smell
            try:
                link_index_album = get_direct_image_link(c, tokens[:4])
                image_link = link_index_album['image_link']
                index = link_index_album['index']
                album_link = link_index_album['album_link']
                s = Template(DIRECT_LINK_TEMPLATE)
                response_text = s.substitute(index=index, image_link=image_link, album_link=album_link)
            except ValueError as e:
                print(str(e))
                response_text = str(e)
            except IndexError:
                response_text = 'Sorry that index is out of bounds.'
        else:
            response_text = ms.TODO_TEXT + ms.HELP_TEXT
    # Otherwise print the help text
    else:
        response_text = ms.HELP_TEXT

    if respond:
        c.reply(response_text + ms.TAIL)
        c.upvote()

    # Adding everything to the DB
    # TODO: Make "responded" more dependent on whether we were actually able to respond to the comment.
    #   and not just what the bot is being told to do.
    db_obj = {'hash': c.id, 'has_responded': respond, 'response_type': response_type}
    print(f"Hash: {db_obj['hash']}")
    print(f"Has responded: {db_obj['has_responded']}")
    print(f"Response type: {db_obj['response_type']}")
    add_comment_to_db(db_obj)

    # Logging
    if verbose:
        tokens = c.body.encode("UTF-8").split()
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Comment Body: ")
        print(c.body.encode("UTF-8"))
        print(f"Tokens: {tokens}")
        print("Response comment body: ")
        print(response_text.encode("UTF-8"))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")



def get_direct_image_link(r_json, imgur_link_type, index):
    """
    Parse Imgur API request response JSON for the direct image link.
    If the index is out of bounds will throw an IndexError.

    TODO: Tests for this are sorely needed. Unsure what happens with all of this refactoring.
    I _think_ only an IndexError is thrown now.
    """
    if imgur_link_type == 'gallery':
        # Gallery: g_response.data.images[index].link
        return r_json['data']['images'][index-1]['link']
    elif imgur_link_type == 'album':
        # Album: a_response.data[index].link
        return r_json['data'][index-1]['link']
    else:
        raise ValueError('This should be unreachable. Please respond to this comment or open an issue so I see it.')   


def get_index_from_string(str):
    """
    Wrap this in a try-except because I don't like the error message

    >>> get_index_from_string('1')
    1
    >>> get_index_from_string('1.1')
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "1.1" doesn't look like an integer to me.
    >>> get_index_from_string('notAnInt')
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "notAnInt" doesn't look like an integer to me.
    """
    index = None
    try:
        index = int(str)
    except ValueError:
        raise ValueError(f'Sorry, "{str}" doesn\'t look like an integer to me.')
    return index


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
    ValueError: Sorry, "http://not-imgur.com/altd8Ld.png" is not a valid imgur URL
    >>> parse_imgur_url('tftp://imgur.com/gallery/59npG') is None
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "tftp://imgur.com/gallery/59npG" is not a valid imgur URL
    >>> parse_imgur_url('Blah') is None
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "Blah" is not a valid imgur URL
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


def is_number_list(string):
    """
    Trying to build a method to check for lists for numbers

    >>> is_number_list('1,2,3')
    True
    >>> parse_imgur_url('HtTP://imgur.COM:80/gallery/59npG')
    {'id': '59npG', 'type': 'gallery'}
    >>> parse_imgur_url('https://i.imgur.com/altd8Ld.png')
    {'id': 'altd8Ld', 'type': 'image'}
    >>> parse_imgur_url('https://i.stack.imgur.com/ELmEk.png')
    {'id': 'ELmEk', 'type': 'image'}
    >>> parse_imgur_url('http://not-imgur.com/altd8Ld.png') is None
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "http://not-imgur.com/altd8Ld.png" is not a valid imgur URL
    >>> parse_imgur_url('tftp://imgur.com/gallery/59npG') is None
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "tftp://imgur.com/gallery/59npG" is not a valid imgur URL
    >>> parse_imgur_url('Blah') is None
    Traceback (most recent call last):
      ...
    ValueError: Sorry, "Blah" is not a valid imgur URL
    """
    match = re.match(r'^[1-9]+(,[1-9]+)*$', string)

def add_comment_to_db(db_dict):
    """
    Adds the comment and its info to the database
    """
    # print(f"Hash: {db_dict['hash']}")
    print(f"Has responded: {db_dict['has_responded']}")
    print(f"Response text: ")
    print(f"{db_dict['response_text']}")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # https://stackoverflow.com/questions/19337029/insert-if-not-exists-statement-in-sqlite
    cur.execute('INSERT OR REPLACE INTO comments VALUES (:hash, :has_responded, :response_text)', db_dict)
    conn.commit()
    conn.close()


def db_setup(db_file):
    print("Setting up DB...")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS comments (
        comment_hash  TEXT       NOT NULL  UNIQUE,
        has_responded INTEGER    DEFAULT 0,
        response_text TEXT       DEFAULT NULL,
        CHECK(has_responded = 0 OR has_responded = 1)
    )''')
    conn.commit()
    conn.close()
    print("Done!")


if __name__ == '__main__':
    env = sys.argv[1]
    USER_AGENT = ''
    DB_FILE = ''
    SUBREDDIT_NAME = ''
    RESPOND = False
    print(f"Running bot in env: {env}")
    
    if env == 'test':
        USER_AGENT = 'MFAImageBotTest'
        DB_FILE = 'test.db'
        SUBREDDIT_NAME = 'mybottestenvironment'
        RESPOND = False
    elif env == 'prod':
        USER_AGENT = ms.USER_AGENT
        DB_FILE = ms.DB_FILE
        SUBREDDIT_NAME = ms.SUBREDDIT_NAME
        RESPOND = True
    else:
        print("Not a valid environment: test or prod.")
        print("Exiting...")
        sys.exit()
    # file-scope vars are set above
    print(f"User agent: {USER_AGENT}")
    print(f"DB file: {DB_FILE}")
    print(f"Subreddit name: {SUBREDDIT_NAME}")
    print(f"Respond: {RESPOND}")
    print("~~~~~~~~~~")
    db_setup(DB_FILE)  # TODO: set db file path as CLI parameter
    run()
