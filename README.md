# About TweetArchiver

This small, simple Python script builds a database of a single user's Tweets locally. This database can be updated, and this script also provided simple functionality to print a random Tweet from the database. The original purpose of this script was similar to something like the "fortune" program, and my usage of it is printing out a random tweet from a specific Twitter user to the terminal every time I open a new one. This functionality is not directly coded within the script, but I show how I did it at the end of this document.

# Installation

This script requires Python 3.

Begin by downloading the repo, then run

```pip install -r requirements.txt```

or

```pip install tweepy```

as this script currently only requires tweepy as a dependency.

You will need to create a `token` file with a bearer token from Twitter. This allows the script to read tweets. Visit the Twitter [Developer Portal](https://developer.twitter.com) and sign up for a developer account. You will need to generate a bearer token, which is used to access publically available, read-only information on Twitter (such as a users tweets) The `token` file should contain the bearer token string and nothing else.

You will also need to find the user ID of the twitter account whose tweets you want to download and archive. This script provides a handy way of taking a username and returning this information.

```python script.py -g <username>```

The script returns the given user's display name, username, and user ID.

Open up the script, find the following variable, and change the user ID.

```user_id = <put user id here>```

The first time you run this script, it will create an empty, local, SQLite database called `tweets.db`. 

# Usage

The script can be run in any of the following modes, and uses GNU style `-<argument>` 

  - -p: print a random Tweet
  - -g <username>: get a user's ID based on their username
  - -u: update the Tweet database
  - -U: Force update the Tweet database

This script is best used when integrated with other programs. For instance, I use a Linux distro with systemd. I have a user service and a timer that updates the database daily. The `.service` and `.timer` files I use for this are included. They are user-ran, so to install them, place them in the directory where your systemd user service files are located (probably `~/.config/systemd/user/` and run the following commands

```
systemctl --user daemon-reload
systemctl --user enable tweetArchiver.timer
```

This should be sufficient to update the database daily.

If you use Windows, a distro that doesn't use systemd, or would rather use a different method of updating the database, you will have to find a way to implement this

Similarily, I simply added the following line to the end of my `.bashrc` file.

```echo `python <directory>/script.py -p```
