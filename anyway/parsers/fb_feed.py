# -*- coding: utf-8 -*-
# from datetime import datetime
import logging

from facebook import GraphAPI, GraphAPIError
from flask.ext.sqlalchemy import SQLAlchemy
from itertools import repeat
import requests
import pickle
import re
from googlemaps import geocoding,Client as GMapClient

from ..models import City
from ..utilities import init_flask

PAGE_NEWS_UPDATES_CODE = '601595769890923'

# APP_... from app dashboard
APP_ID = '156391101644523'
APP_SECRET = '8012d05ce67928871140ca924f29b58f'
MADA_END_ADDRESS_MARKER = u'חובשים ופראמדיקים'
MADA_TEXT_INDICATOR = u'התקבל דיווח במוקד 101 של מד"א במרחב'
EHUD_TEXT_INDICATOR = u'דוברות איחוד הצלה:'
IGNORE_STORY_INDICATOR = u'‎עדכוני חדשות‎ shared a link'
GOOGLE_API_KEY = 'AIzaSyBzx2_S-94XmcLqWpydr9EZRmouik0x__s'
STR_LEN_AT_ROAD = len(u'בכביש')
STR_LEN_TO_DIRECTION = len(u'לכיוון')

app = init_flask()
db = SQLAlchemy(app)

_city_criteria = db.session.query(City.search_heb, City.shortname_heb, City.symbol_code) \
    .order_by(City.search_priority.desc()) \
    .all()


# ##################################################################

class ProcessHandler(object):
    def __init__(self):
        try:
            self._api = GraphAPI()
            # self._api.access_token = self._api.get_app_access_token(APP_ID, APP_SECRET)
            self._posts = []
            self._parsers_dict = {
                MADA_TEXT_INDICATOR: MadaParser(),
                EHUD_TEXT_INDICATOR: EhudHazalaParser()
            }
            self._gmapclient = GMapClient(GOOGLE_API_KEY)
        except GraphAPIError as e:
            logging.error('can not obtain access token,abort (%s)'.format(e.message))

    def has_access(self):
        return self._api.access_token is not None

    @property
    def read_data(self):
        with open('dumppost254.txt', 'rb') as fh:
            self._posts = pickle.Unpickler(fh).load()
        return True

        if not self.has_access():
            return False
        try:
            response_posts = self._api.get_object(PAGE_NEWS_UPDATES_CODE + '/posts')
            self._posts = response_posts['data']
            for idx in repeat(None, 10):
                response_posts = requests.request('GET', response_posts['paging']['next']).json()
                self._posts += response_posts['data']
        except GraphAPIError as e:
            logging.error('can not obtain posts,abort (%s)'.format(e.message))
            return False
        return True

    def get_provider_parser(self, msg):
        if msg.find(MADA_TEXT_INDICATOR) >= 0:
            return self._parsers_dict[MADA_TEXT_INDICATOR]
        if msg.find(EHUD_TEXT_INDICATOR) >= 0:
            return self._parsers_dict[EHUD_TEXT_INDICATOR]
        return None

    def process(self):
        for post in self._posts:
            if 'message' not in post:
                if 'story' in post:
                    post['message'] = post['story']
                else:
                    continue

            parser = self.get_provider_parser(post['message'])
            if parser is None:
                continue
            extract_address = parser.extract(post)
            if extract_address is None:
                continue
            geocode = geocoding.geocode(self._gmapclient,address=extract_address,region='il')
            if len(geocode) < 1:
                print extract_address
            else:
                location = geocode[0]['geometry']['location']
                print extract_address + ': (Lat:{0},Lng:{1})'.format(location['lat'],location['lng'])

class EhudHazalaParser(object):
    def extract(self, post):
        return None


class MadaParser(object):
    @staticmethod
    def has_one_of(msg, cases):
        for case in cases:
            if msg.find(case) > 0:
                return True
        return False

    @staticmethod
    def find_address(msg, cases):
        for case in cases:
            spot = msg.find(case)
            if spot > 0:
                return spot + len(case)
        return 0

    def extract(self, post):
        msg = post['message']
        if self.has_one_of(msg, (u'נפגע מרכב', u'על תאונה', u'רוכב אופנוע')):
            subject = msg[
                      msg.find(MADA_TEXT_INDICATOR) + len(MADA_TEXT_INDICATOR):msg.find(MADA_END_ADDRESS_MARKER)]

            # near_of = self.find_address(subject,(u'בסמוך',u'סמוך'))
            at_roud = subject.find(u'בכביש')
            if at_roud > 0:
                searchin = subject[STR_LEN_AT_ROAD+at_roud:].strip(u' .')
                searchin_parts = searchin.split()
                searchin_parts.insert(0,u'כביש')
                try:
                    part_pos = searchin_parts.index(u'לכיוון')
                    searchin_parts = searchin_parts[:part_pos]
                    result = u' '.join(searchin_parts)
                except ValueError as e:
                    return None
                return result.replace(u'על גשר', '').replace(u'סמוך ל','')
            address_of = self.find_address(subject, (u' ברחוב', u" ברח'", u' בשדרות', u" בשד'", u' בדרך'))
            if address_of > 0:
                searchin = subject[address_of:].strip(u' .')
                for city in _city_criteria:
                    criteria = u'ב' + city.search_heb
                    criteria_pos = searchin.find(criteria)
                    if city.shortname_heb != None and criteria_pos < 0:  # if we have short name and we can not find match
                        criteria = u'ב' + city.shortname_heb
                        criteria_pos = searchin.find(criteria)
                    if criteria_pos >= 0:
                        return searchin[:criteria_pos].strip()+u' '+city.search_heb
        return None


def main():
    handler = ProcessHandler()
    if not handler.read_data:
        logging.debug('no data to process,abort')
        return
    handler.process()
