# -*- coding: utf-8 -*-
# from datetime import datetime
import logging

from facebook import GraphAPI, GraphAPIError
from flask.ext.sqlalchemy import SQLAlchemy
from itertools import repeat
import requests
import pickle
import re
from googlemaps import geocoding, Client as GMapClient

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
KEY_EVENT_ADDRESS = 'addr'
KEY_EVENT_DESCRIBE = 'desc'

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
            extracted = parser.extract(post)
            if KEY_EVENT_ADDRESS in extracted:
                geocode = geocoding.geocode(self._gmapclient, address=extracted[KEY_EVENT_ADDRESS], region='il')
                if len(geocode) > 0:
                    location = geocode[0]['geometry']['location']
                    print extracted[KEY_EVENT_DESCRIBE] +' --- '+extracted[KEY_EVENT_ADDRESS] + ': (Lat:{0},Lng:{1})'.format(location['lat'], location['lng'])


class EhudHazalaParser(object):
    def extract(self, post):
        return {}


class MadaParser(object):
    @staticmethod
    def _find_one_of(msg, cases):
        if not isinstance(cases, basestring):
            for case in cases:
                spot = msg.find(case)
                if spot > 0:
                    return {'at': spot, 'of': case, 'end': spot + len(case)}
        else:
            spot = msg.find(cases)
            if spot > 0:
                return {'at': spot, 'of': cases, 'end': spot + len(cases)}
        return None

    @staticmethod
    def _extract_describe(text, from_pos):
        parts = text[:from_pos].strip(u' ')
        parts = parts.split()
        del (parts[0])
        del (parts[0])
        return u' '.join(parts)

    def extract(self, post):
        details = {}
        msg = post['message']
        case_of = self._find_one_of(msg, (u'נפגע מרכב', u'על תאונה', u'רוכב אופנוע'))
        if case_of is not None:
            subject = msg[
                      msg.find(MADA_TEXT_INDICATOR) + len(MADA_TEXT_INDICATOR):msg.find(MADA_END_ADDRESS_MARKER)]

            # near_of = self.find_address(subject,(u'בסמוך',u'סמוך'))
            roud_of = self._find_one_of(subject, (u'בכביש'))
            if roud_of is not None:
                details[KEY_EVENT_DESCRIBE] = self._extract_describe(subject, roud_of['at'])
                searchin = subject[roud_of['end']:].strip(u' .')
                searchin_parts = searchin.split()
                searchin_parts.insert(0, u'כביש')
                try:
                    part_pos = searchin_parts.index(u'לכיוון')
                    searchin_parts = searchin_parts[:part_pos]
                    result = u' '.join(searchin_parts)
                except ValueError as e:
                    return details
                details[KEY_EVENT_ADDRESS] = result.replace(u'על גשר', '').replace(u'סמוך ל', '')
                return details
            address_of = self._find_one_of(subject, (u' ברחוב', u" ברח'", u' בשדרות', u" בשד'", u' בדרך'))
            if address_of is not None:
                details[KEY_EVENT_DESCRIBE] = self._extract_describe(subject, address_of['at'])
                searchin = subject[address_of['end']:].strip(u' .')
                for city in _city_criteria:
                    criteria = u'ב' + city.search_heb
                    criteria_pos = searchin.find(criteria)
                    if city.shortname_heb != None and criteria_pos < 0:  # if we have short name and we can not find match
                        criteria = u'ב' + city.shortname_heb
                        criteria_pos = searchin.find(criteria)
                    if criteria_pos >= 0:
                        details[KEY_EVENT_ADDRESS] = searchin[:criteria_pos].strip() + u' ' + city.search_heb
                        break

        return details


def main():
    handler = ProcessHandler()
    if not handler.read_data:
        logging.debug('no data to process,abort')
        return
    handler.process()
