import json
from datetime import datetime
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

# Variables that contains the user credentials to access Twitter API
ACCESS_TOKEN = '735619136512876544-ZrsV4Jq2zYwEJP4MjsGM4SU91ulMu86'
ACCESS_SECRET = 'Q3WYKph1q5CiyG3ikP6Kqo3moS5vG7B3I9ahKySLEG2YZ'
CONSUMER_KEY = 'UZ8rM65YgfwrM3YlWoOFBeR2g'
CONSUMER_SECRET = 'WzrwttbWi3uykeXngDsEkiFkECcfBW9gTSNmtFOuHFXqrkFzQy'

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Streaming API
twitter_stream = TwitterStream(auth=oauth)
iterator = twitter_stream.statuses.sample() # Get a sample

# REST API
# twitter = Twitter(auth=oauth)
# iterator = twitter.search.tweets(
#     q='UC Irvine',
#     geocode = [37.781157,-122.398720,1],
#     result_type='recent', lang='en', count=5)
# iterator = twitter_stream.statuses.filter(track='water', lang='en')


def get_tweet_iterator(q, locations):
    return twitter_stream.statuses.filter(track=q, locations=locations, language='en')

