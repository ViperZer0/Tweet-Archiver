import tweepy
import sqlite3
import random
import sys
import os

#Linux account ID

class TweetRetriever():
    #UserID of Iinux account.
    #Put the user id of the account you want to archive here!
    user_id = 3394482083
    bearerTokenName = "token"
    dbName = "tweets.db"
    db = os.path.join(os.path.dirname(__file__),dbName)
    bearerTokenFile = os.path.join(os.path.dirname(__file__),bearerTokenName)

    def __init__(self):
        self.createDatabase()
        self.getToken()

    def getToken(self):
        with open(self.bearerTokenFile,"r") as tokenFile:
            #get only the first line
            self.bearer_token = tokenFile.read().splitlines()[0]

    def createDatabase(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        #Check if table exists. If it doesn't, create a new table.
        tableExists = cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='tweets'").fetchone()[0]
        if not tableExists:
            cursor.execute('''CREATE TABLE tweets(
                            ID UNSIGNED BIG INT PRIMARY KEY NOT NULL,
                            TEXT TEXT NOT NULL
                            );''')
            conn.commit()

        conn.close()

    def getTweetsFromDatabase(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM tweets").fetchall()
        return result
        
    def getLatestId(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        result = cursor.execute("SELECT MAX(id) FROM tweets;").fetchone()
        print("Latest ID: ", result[0])
        return result[0]

    #Optional since argument
    def getTweets(self,since=None):
        client = tweepy.Client(bearer_token = self.bearer_token)

        results = []
        r = client.get_users_tweets(id=self.user_id,max_results=100,since_id=since)
        if "next_token" in r.meta:
            n = r.meta["next_token"]
        else:
            n = None
        if(r.data):
            results = results + r.data
        while(n):
            r = client.get_users_tweets(id=self.user_id,max_results=100,pagination_token=n,since_id=since)
            if(r.data):
                results = results + r.data
            #If no next token we can proceed.
            if "next_token" in r.meta:
                n = r.meta["next_token"]
            else:
                print("Obtained {} new tweets".format(len(results)))
                return results

        print("Obtained {} new tweets".format(len(results)))
        return results
       
    def getAllTweets(self):
        print("Getting all tweets")
        return self.getTweets()

    def getLatestTweets(self):
        print("Getting latest tweets")
        since = self.getLatestId()
        return self.getTweets(since=since)

    def updateDatabase(self,allTweets=False):
        print("Updating database...")
        if(allTweets):
            tweets = self.getAllTweets()
        else:
            tweets = self.getLatestTweets()

        if len(tweets) > 0:
            tweetsData = map(lambda x: x.data, tweets)
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            #Quietly ignore any duplicate entries (when updating all tweets)
            cursor.executemany("INSERT OR IGNORE INTO tweets VALUES (:id, :text);", tweetsData)
            conn.commit()
            conn.close()


    def getRandomTweet(self):
        tweets = self.getTweetsFromDatabase()
        tweet = random.choice(tweets)
        return tweet
    
    def getUserId(self,username):
        client = tweepy.Client(bearer_token = self.bearer_token)
        response = client.get_user(username=username)
        return response

class Parser:
    def __init__(self,args,legend,helpStr):
        self.legend = legend
        self.args = args
        self.helpString = helpStr
         
    def help(self):
        print(self.helpString)

    def hasArg(self, arg):
        return self.legend[arg] in self.args
    
    def getArgPos(self, arg):
        return self.args.index(self.legend[arg]) 
    
if __name__ == '__main__':
    p = Parser(sys.argv,
            {
             'getUser':'-g',
             'printTweet':'-p',
             'updateTweets':'-u',
             'forceUpdate':'-U',
             'help':'-h'
             },
            ("Usage\n\tpython script.py [options]\n\nOptions:\n"
             "\t-g <username>\tGets <username>'s user id\n"
             "\t-p\t\tPrints a random tweet from the database\n"
             "\t-u\t\tUpdates database with tweets posted since last update\n"
             "\t-U\t\tTries to update as many tweets as possible. Use if the database is missing older tweets.\n"
             "\t-h\t\tPrints this help menu")
            )

    t = TweetRetriever()

    
    if p.hasArg("help"):
        p.help()
    elif p.hasArg("getUser"):
        #Get next argument
        pos = p.getArgPos("getUser") + 1
        user = t.getUserId(sys.argv[pos])
        print("Display Name: {}\nUsername: {}\nID: {}\n".format(user.data.name,user.data.username,user.data.id),end="")

    elif p.hasArg("forceUpdate"):
        t.updateDatabase(allTweets=True)

    elif p.hasArg("updateTweets") and not p.hasArg("forceUpdate"):
        t.updateDatabase(allTweets=False)

    elif p.hasArg("printTweet"):
        print(t.getRandomTweet()[1])

    else:
        p.help()

    
    

