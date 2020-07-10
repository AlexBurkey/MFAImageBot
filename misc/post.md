Link: https://imgur.com/a/jWvLA

Hello, this is MFAImageBot! A bot built to help directly link images from large inspiration albums. 

Ever been scrolling through an [awesome album](https://imgur.com/a/jWvLA) and you just *had* to know where the sweet killshots in image 42 came from? So you make a comment asking for help, but since you're on your phone you just ask "What are those dope kicks in #42?" and don't link the photo. No harm no foul.

However, anyone who wants to help you out will have to go back to the album and count all the way to image 42 just to see if they even know or not! This bot is intended to solve that problem and make this a lot easier. 

## Usage  
The bot listens for comments which begin with `!MFAImageBot` and then attempts to fullfil the request in the comment.

There are three main commands: 
* `help`: Prints a help message
* `link`: Takes in a link to an Imgur album/gallery and a number. Responds with a direct link to the requested image
* `op`: Goes and looks in the Reddit submission's link for the requested image.

Here's the help message:  
> `!MFAImageBot help`: Print this help message.  
> `!MFAImageBot link <album-link> <number>`: Attempts to directly link the <number> image from <album-link>  
> `!MFAImageBot op <number>`: Attempts to directly link the <number> image from the album in the submission

The bot will (should) ignore everything after the correct commands and inputs. So you can make a comment with text after the commands and numbers without issue, [like this one.](https://www.reddit.com/r/malefashionadvice/comments/goj5w8/converse_mfa_footwear_basics_6/frgmcys/?context=1) 

Also, *anyone* can call this bot *anywhere* within /r/malefashionadvice. So if someone asks about a particular image, but doesn't link it, feel free to call the bot. It should respond in less than ~1m if Imgur's API and Reddit are working properly. 

## Code  
I've open-sourced the code for this bot [here](https://github.com/AlexBurkey/MFAImageBot) if you'd like to contribute ideas or anything. I'm working on this mostly as a personal project for my own knowledge/learning benefit but feel free to clone, fork, submit PRs, etc. 

If you find a bug please open an issue [here](https://github.com/AlexBurkey/MFAImageBot/issues/new?assignees=AlexBurkey&labels=bug&template=bug_report.md&title=) or just PM/message the bot.

If you have an idea for a feature/enhancement you can suggest it [here.](https://github.com/AlexBurkey/MFAImageBot/issues/new?assignees=AlexBurkey&labels=enhancement&template=feature_request.md&title=)

## Restrictions/FYIs  
* The bot only works with Imgur albums/galleries. Imgur is by-far the most common image host for these things, but it will definitely not work for other endpoints right now.
* Imgur albums and the API can be kind of weird if the images in the album have been rearranged. I'm not sure if this is just a propagation issue on Imgur's side or if it permenantly breaks an album's numbering from the API's standpoint.
* The `op` command (currently) only works if the reddit submission is a link-post to an Imgur album/gallery. It doesn't look through the text of self-posts.
* The bot is currently setup to only monitor comments in /r/malefashionadvice and won't work if you call it in a post body or in another subreddit.
* I expect this bot to break occasionally as I'm building up testing and such. If you run into a weird issue you can PM the bot or [open an issue.](https://github.com/AlexBurkey/MFAImageBot/issues/new?assignees=AlexBurkey&labels=bug&template=bug_report.md&title=) Think of this as a beta.

I'll be around for a bit to answer any questions. I also made this post an image post so feel free to test it out!

Credit for the album goes to the famous /u/jdbee from [this post](https://www.reddit.com/r/malefashionadvice/comments/17zyk1/100_outfit_compilations_a_collection_of/)