from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from slistener import SListener
import time, tweepy, sys, json, urllib2, ast

from klout import *

import tweepy

access_token = "910959552-p9y6OBNwRsnLhGtOMgjt9JAd92wKDtJNnNeKi9vo"
access_token_secret = "FvTR8DcgoPsltx85O2kWoTGRbf5i3ZbuxMLOmOiDSUXtp"
consumer_key = "I3mYarCeqcXTukjMvjVEt0Uml"
consumer_secret = "bdDaxeL5A7Hwg9L49rmZZPvJr3XdzTyg2frZtQGyElZcGzPRLz"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def auth_twitter(str):
    print str
    print 'entered in auth twitter function'
    access_token = "910959552-p9y6OBNwRsnLhGtOMgjt9JAd92wKDtJNnNeKi9vo"
    access_token_secret = "FvTR8DcgoPsltx85O2kWoTGRbf5i3ZbuxMLOmOiDSUXtp"
    consumer_key = "I3mYarCeqcXTukjMvjVEt0Uml"
    consumer_secret = "bdDaxeL5A7Hwg9L49rmZZPvJr3XdzTyg2frZtQGyElZcGzPRLz"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    track = ["#carrotnight"]

    listen = SListener(api, 'tweets')
    stream = tweepy.Stream(auth, listen)

    print "Streaming started..."

    try:
        stream.filter(track = track)
    except Exception, e:
        print "error!", e
        stream.disconnect()

# Create your views here.
def first_page(request):
    #auth_twitter('amol')
    print 'hello first_page'
    return render_to_response("index.html", {}, context_instance = RequestContext(request))

def tweet_json(request):
    f = open('tweets.json')
    json_string = f.read()
    data = json.loads(json_string)

    return HttpResponse(json.dumps(data), content_type="application/json")

def analysis(request, screenName):
    # Make the Klout object
    k = Klout('c5ezradb4k9w4zku5ut6mwd6', secure=True)

    # Get kloutId of the user by inputting a twitter screenName
    kloutId = k.identity.klout(screenName=screenName).get('id')

    # Get klout score of the user
    score = k.user.score(kloutId=kloutId, timeout=5).get('score')

    print "User's klout score is: %s" % (score)

    influence = k.user.influence(kloutId=kloutId)

    topics = k.user.topics(kloutId=kloutId)

    #print "User's influencers_count is: %s" % (influencers_count)

    #print "User's topics list is: %s" % (topics_length)

    user = api.get_user(screenName)

    alltweets = []

    new_tweets = api.user_timeline(screen_name = screenName,count=200)


    alltweets.extend(new_tweets)

    oldest = alltweets[-1].id - 1

    while len(alltweets) < 1000 and len(new_tweets) > 0:
		#print "getting tweets before %s" % (oldest)

		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screenName,count=200,max_id=oldest)

		#save most recent tweets
		alltweets.extend(new_tweets)

		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

		#print "...%s tweets downloaded so far" % (len(alltweets))

    values = {'data': []}
    timewise_split = [0]*24

    for tweet in alltweets:
        values['data'].append({'content': tweet.text, 'lang': 'en'})
        timewise_split[tweet.created_at.hour] += 1

    print timewise_split
    url = 'http://sentimentanalyzer.appspot.com/api/classify.json'
    data = json.dumps(values)
    response = urllib2.urlopen(url, data)
    page = response.read()

    polarity_sum = 0
    total_tweets = 0
    page = ast.literal_eval(page)

    print page
    for p in page['data']:
        total_tweets += 1
        polarity_sum += p['score']

    if total_tweets != 0:
        polarity = float(polarity_sum)/total_tweets
    else:
        polarity = -1

    '''
    print alltweets, '@$%^&*&^%$#$%^&*'
    screen_names, hashtags, urls, media, symbols = extract_tweet_entities(alltweets)
    print json.dumps(screen_names[0:5], indent=1)
    print json.dumps(hashtags[0:5], indent=1)
    print json.dumps(urls[0:5], indent=1)
    print json.dumps(media[0:5], indent=1)
    print json.dumps(symbols[0:5], indent=1)
    '''

    resp = {}
    resp['score'] = score
    resp['influence'] = influence
    resp['topics'] = topics
    resp['followers_count'] = user.followers_count
    resp['friends_count'] = user.friends_count
    resp['statuses_count'] = user.statuses_count
    resp['screen_name'] = user.screen_name
    resp['name'] = user.name
    resp['profile_image_url'] = user.profile_image_url
    resp['total_tweets'] = total_tweets
    resp['polarity'] = int(polarity*100)
    resp['npolarity'] = 100 - resp['polarity']

    return render_to_response("index3.html", resp, context_instance = RequestContext(request))

def extract_tweet_entities(statuses):
    if len(statuses) == 0:
        return [], [], [], [], []

    print statuses
    screen_names = [ user_mention.screen_name
                        for status in statuses
                            for entity in status.entities
                                for user_mention in entity.user_mentions ]
    hashtags = [ hashtag['text']
                    for status in statuses
                        for hashtag in status['entities']['hashtags'] ]
    urls = [ url['expanded_url']
                for status in statuses
                    for url in status['entities']['urls'] ]
    symbols = [ symbol['text']
                    for status in statuses
                        for symbol in status['entities']['symbols'] ]
    # In some circumstances (such as search results), the media entity # may not appear
    if status['entities'].has_key('media'):
        media = [ media['url']
                        for status in statuses
                            for media in status['entities']['media'] ]
    else:
        media = []

    return screen_names, hashtags, urls, media, symbols # Sample usage
