import re
import my_strings

def isInt(s):
    """
    Helper function to see if a string is an int.
    TODO: Add doctests
    """
    try: 
        int(s)
        return True
    except ValueError:
        return False


def is_imgur_url(s):
    """
    Returns truthy value if s is an imgur URL. None otherwise. But this should work with an if.

    Just ripped the regex from the parse method. The group names aren't needed really.
    TODO: Add doctests
    """
    return re.match(
        r'^(?i:https?://(?:[^/:]+\.)?imgur\.com)(:\d+)?'
        r'/(?:(?P<album>a/)|(?P<gallery>gallery/))?(?P<id>\w+)',
        s
    )

def get_and_split_first_line(string):
    """
    Given a string return a list of the tokens in the first line.

    TODO: doctests
    """
    return string.splitlines()[0].split()

def reply_and_upvote(c, response, respond=False):
    """
    Respond to and upvote comment.

    Returns DB Object. This is a bad idea
    """
    print('-------------------------------------------------')
    if respond:
        print(f'Responding to comment{c.permalink}')
        c.reply(response + my_strings.TAIL)
        c.upvote()
    else:
        print(f'Not responding to comment {c.permalink}')
    
    print('Comment text: ')
    print(f'{c.body}')
    # Adding everything to the DB
    # TODO: Make "responded" more dependent on whether we were actually able to respond to the comment.
    #   and not just what the bot is being told to do.
    return {'hash': c.id, 'has_responded': respond, 'response_text': response}