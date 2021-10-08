#!/usr/bin/env python3
import os
import re
import sqlite3
import sys
from string import Template

from . import helpers as h
from . import my_strings as ms
import praw  # pylint: disable=import-error
import requests  # pylint: disable=import-error
from dotenv import load_dotenv  # pylint: disable=import-error

# References praw-ini file
BATSIGNALS = ("!mfaimagebot", "!mfaib", "!mfa", "!imagebot", "!ibot")
IMGUR_ALBUM_API_URL = "https://api.imgur.com/3/album/${album_hash}/images"
IMGUR_GALLERY_API_URL = "https://api.imgur.com/3/gallery/album/${gallery_hash}"
DIRECT_LINK_TEMPLATE = "[Direct link to image #${index}](${image_link})  \n"
DIRECT_LINK_ALBUM_TEMPLATE = "Image(s) number ${indexes} from album ${album_link}"


def run():
    r = praw.Reddit(USER_AGENT)
    load_dotenv()  # Used for imgur auth
    # TODO: verify that the db path is valid.
    #   A single file is fine but dirs are not created if they don't exist
    print("Looking for comments...")
    for comment in r.subreddit(SUBREDDIT_NAME).stream.comments():
        if check_batsignal(comment.body) and not check_has_responded(comment):
            print("-------------------------------------------------")
            response = ms.HELP_TEXT
            tokens = h.get_and_split_first_line(comment.body)
            # More than 100 tokens on the first line.
            # I'm not dealing with that
            if len(tokens) > 100:
                db_obj = h.reply_and_upvote(
                    comment, response=ms.HELP_TEXT, respond=RESPOND
                )
                add_comment_to_db(db_obj)
                continue

            pairs = parse_comment(tokens)
            # Check for help
            if pairs["help"]:
                db_obj = h.reply_and_upvote(
                    comment, response=ms.HELP_TEXT, respond=RESPOND
                )
                add_comment_to_db(db_obj)
                continue

            indexes = pairs["indexes"]
            if len(indexes) == 0:
                db_obj = h.reply_and_upvote(
                    comment, response=ms.HELP_TEXT, respond=RESPOND
                )
                add_comment_to_db(db_obj)
                continue

            # TODO: Wrap/deal with possible exceptions from parsing imgur url
            comment_imgur_url = pairs["imgur_url"]

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
                response = (
                    "Sorry, no imgur link found in your comment or the link of the OP."
                )
                db_obj = h.reply_and_upvote(comment, response=response, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue

            album_link_type = album_link_map["type"]
            album_link_id = album_link_map["id"]

            # TODO: Wrap in try/except
            request_url = build_request_url(album_link_type, album_link_id)

            r = send_imgur_api_request(request_url)
            print(f"Status Code: {r.status_code}")
            print(f"Request url: {request_url}")
            if r is not None and r.status_code == 200:
                # Iterate through indexes and build response text.
                response = ""
                for index in indexes:
                    image_link = None
                    try:
                        # Parse request and set response text
                        image_link = get_direct_image_link(
                            r.json(), album_link_type, index
                        )
                        print(f"Image link: {image_link}")
                        s = Template(DIRECT_LINK_TEMPLATE)
                        response += s.substitute(
                            index=index, image_link=image_link, album_link=album_link
                        )
                    except IndexError:
                        response += f"Sorry {index} is out of bounds.\n"
                response += f"Image(s) numbered {indexes} from album {album_link}"
                db_obj = h.reply_and_upvote(comment, response=response, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue
            else:  # Status code not 200
                # TODO: Deal with status codes differently, like if imgur is down or I don't have the env configured
                response = f"Sorry, {album_link} is probably not an existing imgur album, or Imgur is down."
                db_obj = h.reply_and_upvote(comment, response=response, respond=RESPOND)
                add_comment_to_db(db_obj)
                continue


def check_batsignal(comment_body):
    """
    Returns True if the comment body starts with the batsignal "!mfaimagebot". Otherwise False.
    Case insensitive.
    """
    text = comment_body.lower()
    return text.startswith(BATSIGNALS)


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
    cur.execute(
        "SELECT * FROM comments WHERE comment_hash=:hash AND has_responded=1",
        {"hash": comment.id},
    )
    val = cur.fetchone() is not None
    conn.close()
    return val


def parse_comment(tokens):
    """
    Expected input: one line split on whitespace
    Behavior: Parse each token and look for "help", integers, and an imgur url.
    Returns: dictionary containing whether "help" was specified, the list of integers, and imgur URL
    """
    pairs = {"indexes": [], "imgur_url": None, "help": False}
    # Find the numbers in the tokens
    for s in tokens:
        # Look for help
        if s.lower() == "help":
            pairs["help"] = True
            break
        # Find the numbers in the tokens
        if h.isInt(s):
            pairs["indexes"].append(int(s))
        # Find imgur URL in the tokens
        if h.is_imgur_url(s):
            pairs["imgur_url"] = s
    return pairs


def build_request_url(imgur_link_type, imgur_link_id):
    """
    Create the Imgur Request URL.
    Imgur Galleries and Albums have different endpoints.
    Any other resource type hasn't been implemented/might not exist.
    TODO: doctests
    """
    if imgur_link_type == "album":
        s = Template(IMGUR_ALBUM_API_URL)
        return s.substitute(album_hash=imgur_link_id)
    elif imgur_link_type == "gallery":
        s = Template(IMGUR_GALLERY_API_URL)
        return s.substitute(gallery_hash=imgur_link_id)
    else:
        raise ValueError("Sorry, that imgur resource hasn't been implemented yet.")


def send_imgur_api_request(request_url):
    """
    Send API request to Imgur
    TODO: doctests
    """
    # Send the request
    client_id = os.getenv("IMGUR_CLIENT_ID")
    headers = {"Authorization": f"Client-ID {client_id}"}
    return requests.get(request_url, headers=headers)


def get_direct_image_link(r_json, imgur_link_type, index):
    """
    Parse Imgur API request response JSON for the direct image link.
    If the index is out of bounds will throw an IndexError.

    TODO: Tests for this are sorely needed. Unsure what happens with all of this refactoring.
    I _think_ only an IndexError is thrown now.
    """
    if imgur_link_type == "gallery":
        # Gallery: g_response.data.images[index].link
        return r_json["data"]["images"][index - 1]["link"]
    elif imgur_link_type == "album":
        # Album: a_response.data[index].link
        return r_json["data"][index - 1]["link"]
    else:
        raise ValueError(
            "This should be unreachable. Please respond to this comment or open an issue so I see it."
        )


# Lol yanked this whole thing from SE
# https://codereview.stackexchange.com/questions/204316/imgur-url-parser
def parse_imgur_url(url):
    """
    Extract the type and id from an Imgur URL.
    """
    match = re.match(
        r"^(?i:https?://(?:[^/:]+\.)?imgur\.com)(:\d+)?"
        r"/(?:(?P<album>a/)|(?P<gallery>gallery/))?(?P<id>\w+)",
        url,
    )
    if not match:
        raise ValueError('Sorry, "{}" is not a valid imgur URL'.format(url))
    return {
        "id": match.group("id"),
        "type": "album"
        if match.group("album")
        else "gallery"
        if match.group("gallery")
        else "image",
    }


def add_comment_to_db(db_dict):
    """
    Adds the comment and its info to the database
    """
    # print(f"Hash: {db_dict['hash']}")
    print(f"Has responded: {db_dict['has_responded']}")
    print("Response text: ")
    print(f"{db_dict['response_text']}")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    # https://stackoverflow.com/questions/19337029/insert-if-not-exists-statement-in-sqlite
    cur.execute(
        "INSERT OR REPLACE INTO comments VALUES (:hash, :has_responded, :response_text)",
        db_dict,
    )
    conn.commit()
    conn.close()


def db_setup(db_file):
    print("Setting up DB...")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS comments (
        comment_hash  TEXT       NOT NULL  UNIQUE,
        has_responded INTEGER    DEFAULT 0,
        response_text TEXT       DEFAULT NULL,
        CHECK(has_responded = 0 OR has_responded = 1)
        )"""
    )
    conn.commit()
    conn.close()
    print("Done!")


if __name__ == "__main__":
    env = sys.argv[1]
    USER_AGENT = ""
    DB_FILE = ""
    SUBREDDIT_NAME = ""
    RESPOND = False
    print(f"Running bot in env: {env}")

    if env == "test":
        USER_AGENT = "MFAImageBotTest"
        DB_FILE = "test.db"
        SUBREDDIT_NAME = "mybottestenvironment"
        RESPOND = False
    elif env == "prod":
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
