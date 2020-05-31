There are a lot of versions of PRAW out there and a lot of guides using really outdated versions of it.
Using a comment stream makes monitoring an single subreddit (or a list) really easy.
Use a "batsignal" for your bot. I find it easier to parse comments that way than looking in my inbox for mentions. It also lets you keep your inbox open for actual inquiries and messages. 
Imgur's API is kind of annoying. Each resource has a hash that you need but it's only unique *within that resource block*. That means that it's possible to submit a valid request to the imgur album, gallery, and image API endpoints with the same hash and get back up to 3 different results. I found a function on stack exchange which has a bunch of regex I haven't bothered to validate but it hasn't crashed my bot (yet). 
Managing API keys is really annoying. PRAW has a fairly straightforward management system, but setting up Imgur's keys even for anonymous requests to public resources proved to be a bit of a pain. I just used `python-dotenv` since it's pretty straightforward. 

## Performance
I'm unsure if this method will work at the scale of a subreddit which has nearly 2.3m subscribers. Not sure how fast the comments move.

## Deployment
Options:
* Small AWS EC2 instance
    * I will never ever use lambda for this. It's a nightmare to get the python libaries packaged up correctly last time I tried. Just use a damn server. 
* Heroku: I haven't explored this just yet but from what I know it's a popular choice to host small bots like this.
    Terrible choice. Heroku is mainly for things like webservers and has preset packages and things. It is absolutely not built to host a reddit bot.
* RPi: This will probably be the most straight forward solution even if it's not the most stable. Unsure what the performance will look like.
    Current choice. It's easy to access, "free", and it doens't seem like there's any performance issues with the bot or with running a pi-hole on it at the same time. 

## Environment Management
Things to think about
* Python version
* Versions of all of your modules
* Things like .env files 

## Project management
Using even the simplest tools like TODOs in the code as you think of them is helpful. 
You also need to think on a macro level. Larger ticket refactorings, feature additions, design choices. I like using GH issues to track them. It lives with the code, supports MD, and you can tie branches and PRs to the issues. Even for a small project like this, keeping up with making TODOs all the time and making Issues at the end of each session are really helpful at being able to pick up after a while away from the project. Also make sure you don't neglect your wiki/README like I do.

## Testing
Using GH Actions to setup some automated testing. `doctest` seems like a nice way to test some of the methods. Another option is `pytest`.