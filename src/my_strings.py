USER_AGENT = "MFAImageBot"

DB_FILE = "mfa.db"
SUBREDDIT_NAME = "malefashionadvice"

TODO_TEXT = "Sorry, this function has not been implemented yet.\n\n"
HELP_TEXT = (
    "Usage: I respond to comments starting with `!MFAImageBot` (case insensitive).  \n"
    "`!MFAImageBot help`: Print this help message.  \n"
    "`!MFAImageBot <album-link> 2, 3, 42`: I attempt to link the 2nd, 3rd, and 42nd images from <album-link>  \n"
    "`!MFAImageBot 2, 3, 42`: I attempt to link the 2nd, 3rd, and 42nd images from the album in the submission  \n"
    "Comma or whitespace separated lists of numbers are also cool: `!MFAImageBot 2,4,42` or `!MFAImageBot 2 4 42`  \n"
)
TAIL = (
    "\n\n---\nI am a bot! If you've found a bug you can open an issue "
    "[here.](https://github.com/AlexBurkey/MFAImageBot/issues/new?template=bug_report.md)  \n"
    "If you have an idea for a feature, you can submit the idea "
    "[here](https://github.com/AlexBurkey/MFAImageBot/issues/new?template=feature_request.md)  \n"
    "Version 1.3"
)
