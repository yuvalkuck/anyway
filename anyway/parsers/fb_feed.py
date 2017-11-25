# -*- coding: utf-8 -*-
# from datetime import datetime
import logging

from facebook import GraphAPI, GraphAPIError
from flask.ext.sqlalchemy import SQLAlchemy

from ..utilities import init_flask

PAGE_NEWS_UPDATES_CODE = '601595769890923'

# APP_... from app dashboard
APP_ID = '156391101644523'
APP_SECRET = '8012d05ce67928871140ca924f29b58f'

app = init_flask()
db = SQLAlchemy(app)


# ##################################################################

class ProcessParser(object):
    def __init__(self):
        try:
            self._api = GraphAPI()
            self._api.access_token = self._api.get_app_access_token(APP_ID, APP_SECRET)
            self._posts = ()
        except GraphAPIError as e:
            logging.error('can not obtain access token,abort (%s)'.format(e.message))

    def has_access(self):
        return self._api.access_token is not None

    def read_data(self):
        if not self.has_access():
            return False
        try:
            response_posts = self._api.get_object(PAGE_NEWS_UPDATES_CODE + '/posts')
            self._posts = response_posts['data']
        except GraphAPIError as e:
            logging.error('can not obtain posts,abort (%s)'.format(e.message))
            return False
        return True

    def parse(self):
        for post in self._posts:
            if post.has_key('message'):
                msg = post['message']
                if msg.find(u'התקבל דיווח במוקד 101') < 0:
                    continue
                if self.has_one_of(msg, (u'נפגע מרכב', u'על תאונה', u'רוכב אופנוע', u'')):
                    print msg + "\n"

    def has_one_of(self, msg, cases):
        for case in cases:
            if msg.find(case) > 0:
                return True
        return False



def main():
    parser = ProcessParser()
    if not parser.read_data():
        logging.debug('no data to process,abort')
        return
    parser.parse()
