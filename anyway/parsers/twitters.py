# -*- coding: utf-8 -*-
import json
from datetime import datetime

import logging
import tweepy
from flask.ext.sqlalchemy import SQLAlchemy
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from ..utilities import init_flask, time_delta, CsvReader, ImporterUI, truncate_tables,decode_hebrew

CONSUMER_KEY = 'xC8S9xrsS1pFa82EeFe5h2zjX'
CONSUMER_SECRET = 'GhC5nTdmhdhbPGFCGFbnMoK1OR1J7m2RdnnyxaVeKFJCr9kAVb'
ACCESS_TOKEN = '930058064773959681-NRoWXRzmQ8lWQdF3TYfbKE4EDlbz0GE'
ACCESS_TOKEN_SECRET = '3DLMcGV6UUgPFfLBU9SO8Ayo19g8l8H6JiAKP327Vzd8b'

app = init_flask()
db = SQLAlchemy(app)


# ##################################################################
class StdOutListener(StreamListener):
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


def main(load_history, delete_all):
    l = StdOutListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    # res = api.search(q='mda_israel',count=2)
    # query = u'התקבל דיווח במוקד 101 של מד"א'
    query = u'התקבל דיווח במוקד 101'
    cp1255 = 'cp1255'
    searched_tweets = [status._json for status in
                       tweepy.Cursor(api.search, q=query, lang='he', result_type="recent", tweet_mode='extended').items(
                           50)]
    json_strings = [json.dumps(json_obj) for json_obj in searched_tweets]
    for item in json_strings:
        struct = json.loads(item)
        # if(match_one(struct['full_text'],(u'...',u'אירוע דריסה',u'מאופניים חשמליים')) == True):
        #     continue
        # if(match_one(struct['full_text'],(u'שנפגע מרכב',u'רכב שהתהפך',u'שנפגע מרכב',u' ת"ד ')) == False):
        #     continue
        print struct['created_at'].encode('utf-8') + "-:-" + struct['full_text'].encode('utf-8')
        print "--------------------------\n"

    # stream = Stream(auth, l)


    # This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    # stream.filter(track=['mda_israel'])
    # stream.sample()


    # wipe all data first
    # if delete_all:
    #     tables = (RegisteredVehicle)
    #     logging.info("Deleting tables: " + ", ".join(table.__name__ for table in tables))
    #     for table in tables:
    #         db.session.query(table).delete()
    #         db.session.commit()

    # started = datetime.now()

    # db.session.commit()

def match_one(text,matches,encode='utf-8'):
    encoded = decode_hebrew(text,encode)
    for match in matches:
        if( encoded.find(match) >= 0):
            return True
    return False