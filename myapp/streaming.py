from slistener import SListener
import time, tweepy, sys

access_token = "910959552-p9y6OBNwRsnLhGtOMgjt9JAd92wKDtJNnNeKi9vo"
access_token_secret = "FvTR8DcgoPsltx85O2kWoTGRbf5i3ZbuxMLOmOiDSUXtp"
consumer_key = "I3mYarCeqcXTukjMvjVEt0Uml"
consumer_secret = "bdDaxeL5A7Hwg9L49rmZZPvJr3XdzTyg2frZtQGyElZcGzPRLz"

CONSUMER_KEY, CONSUMER_SECRET = '', '' # dev.twitter.com to get yours
USER_KEY, USER_SECRET = '', ''

def main():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    track = ["#carrotnight"]

    listen = SListener(api, 'myprefix')
    stream = tweepy.Stream(auth, listen)

    print "Streaming started..."

    try:
        stream.filter(track = track)
    except:
        print "error!"
        stream.disconnect()

if __name__ == '__main__':
    main()
