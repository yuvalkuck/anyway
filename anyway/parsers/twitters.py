# -*- coding: utf-8 -*-
import csv
import json
import glob
import io
import logging
import os
import re
import sys
from datetime import datetime
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream

import six
from flask.ext.sqlalchemy import SQLAlchemy

from ..models import RegisteredVehicle, City
from ..utilities import init_flask, time_delta

# Headless servers cannot use GUI file dialog and require raw user input
fileDialog = True
try:
    import tkFileDialog
except (ValueError, ImportError):
    fileDialog = False

app = init_flask()
db = SQLAlchemy(app)


# ##################################################################
class StdOutListener(StreamListener):
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


def main(delete_all):
    CONSUMER_KEY = 'xC8S9xrsS1pFa82EeFe5h2zjX'
    CONSUMER_SECRET = 'GhC5nTdmhdhbPGFCGFbnMoK1OR1J7m2RdnnyxaVeKFJCr9kAVb'
    ACCESS_TOKEN = '930058064773959681-NRoWXRzmQ8lWQdF3TYfbKE4EDlbz0GE'
    ACCESS_TOKEN_SECRET = '3DLMcGV6UUgPFfLBU9SO8Ayo19g8l8H6JiAKP327Vzd8b'

    l = StdOutListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    # res = api.search(q='mda_israel',count=2)
    # query = u'התקבל דיווח במוקד 101 של מד"א'
    query = u'התקבל דיווח במוקד 101'
    cp1255 = 'cp1255'
    searched_tweets = [status._json for status in tweepy.Cursor(api.search, q=query,lang='he',result_type="recent",tweet_mode='extended').items(50)]
    json_strings = [json.dumps(json_obj) for json_obj in searched_tweets]
    for item in json_strings:
        struct = json.loads(item)
        if( struct['full_text'].encode('utf-8').find('...') >= 0):
            continue
        # if( struct['text'].find(u'דוברות מד"א') > 0):
        #     continue
        print struct['created_at'].encode('utf-8')+"-:-"+struct['full_text'].encode('utf-8')
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

    started = datetime.now()

    # db.session.commit()
