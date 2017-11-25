# -*- coding: utf-8 -*-
import json
from datetime import datetime
import logging
from flask.ext.sqlalchemy import SQLAlchemy
from ..utilities import init_flask, time_delta, decode_hebrew
import facebook

PAGE_NEWS_UPDATES_CODE = '601595769890923'

# APP_... from app dashboard
APP_ID = '156391101644523'
APP_SECRET = '8012d05ce67928871140ca924f29b58f'
# CLIENT_SECRET = '5823a2f9c966291009b8a42fb52b8cdf'

app = init_flask()
db = SQLAlchemy(app)


# ##################################################################


def main():
    api = facebook.GraphAPI()
    try:
        api.access_token = api.get_app_access_token(APP_ID, APP_SECRET)
    except facebook.GraphAPIError as e:
        logging.error('can not obtain access token,abort (%s)'.format(e.message))
        return

    try:
        response_posts = api.get_object(PAGE_NEWS_UPDATES_CODE+'/posts')
        for post in response_posts['data']:
            if post.has_key('message'):
                msg = post['message']
                if msg.find(u'התקבל דיווח במוקד 101') < 0:
                    continue
                print post['id']+'::'+post['created_time']+"-:-"+msg+"\n"
    except facebook.GraphAPIError as e:
        logging.error('can not obtain posts,abort (%s)'.format(e.message))
