# -*- coding: utf-8 -*-
# from datetime import datetime
import logging

from facebook import GraphAPI, GraphAPIError
from flask.ext.sqlalchemy import SQLAlchemy
from itertools import repeat
import requests
import re
import pickle
from googlemaps import geocoding, Client as GMapClient

from ..models import City
from ..utilities import init_flask

PAGE_NEWS_UPDATES_CODE = '601595769890923'

# APP_... from app dashboard
APP_ID = '1975701242713132'
APP_SECRET = '180b55edfaf8e995d726c06002d08042'
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
        with open('dumppost139.txt', 'rb') as fh:
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
        # if msg.find(MADA_TEXT_INDICATOR) >= 0:
        #     return self._parsers_dict[MADA_TEXT_INDICATOR]
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
            # add more then one KEY_EVENT_ADDRESS to look for location
            if KEY_EVENT_ADDRESS in extracted:
                addresses = extracted[KEY_EVENT_ADDRESS]
                if not isinstance(addresses, basestring):
                    for addresse in addresses:
                        geocode = geocoding.geocode(self._gmapclient, address=addresse, region='il')
                        if len(geocode) > 0:
                            location = geocode[0]['geometry']['location']
                            print extracted[KEY_EVENT_DESCRIBE] +' --- '+addresse + ': (Lat:{0},Lng:{1})'.format(location['lat'], location['lng'])
                            break
                else:
                    geocode = geocoding.geocode(self._gmapclient, address=addresses, region='il')
                    if len(geocode) > 0:
                        location = geocode[0]['geometry']['location']
                        print extracted[KEY_EVENT_DESCRIBE] + ' --- ' + \
                              extracted[KEY_EVENT_ADDRESS] + ': (Lat:{0},Lng:{1})'.format(location['lat'], location['lng'])
                    else:
                        print extracted[KEY_EVENT_ADDRESS]


class ProviderParserBase(object):
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
    def _remove_number_of_words(msg,words=1,front=True):
        parts = msg.strip(u' ').split()
        while(words > 0):
            words -= 1
            if front:
                del (parts[-1])
            else:
                del (parts[0])
        return u' '.join(parts)



class EhudHazalaParser(ProviderParserBase):

    @staticmethod
    def _dot_split_first_part(msg):
        parts = msg.split(u'.')
        return parts[0]

    @staticmethod
    def _prepare_address_cases(address, append=''):
        address = append+address.replace(u'בסמוך ל', u'ליד ').strip(u'.')
        if address.find(u'צומת') > 0:
            return (address,address.replace(u'צומת',''))
        return address

    def extract(self, post):
        return {}
        # msg = post['message']
        # details = {}
        # relative_case_of = self._find_one_of(msg, (u'נפגע מ',u'נפגעה מ',u'תאונת דרכים', u'על תאונה', u'רוכב אופנוע',u'רוכב קטנוע',u'פגיעת רכב',u'תאונה עם'))
        # if relative_case_of is not None:
        #     print msg
        #     # parts = self._find_one_of(msg,(u'טופל ע"י',u'טיפול רפואי ראשוני',u'טיפול ראשוני'))
        #     print relative_case_of['of']
        #     roud_of = self._find_one_of(msg, (u' בכביש',u' כביש'))
        #     if roud_of is not None:
        #         parts =msg.split(relative_case_of['of'])
        #         details[KEY_EVENT_DESCRIBE] = parts[0]
        #         # re.search(r'[{0}]\D+\d+' % u',.' +u' כביש',.............
        #         roud_parts = parts[-1].split(roud_of['of'])
        #         address = self._dot_split_first_part(roud_parts[1])
        #         details[KEY_EVENT_ADDRESS] = self._prepare_address_cases(address,u'כביש ')
        #         print details[KEY_EVENT_ADDRESS]
        #         print "-------------------------------------------------"
        #     else:
        #         print msg
        #         print "+++++++++++++++++++++++++++++++++++++++++++++++++"
        # else:
        #     print msg
        #     print "*****************************************************"
        # return details


class MadaParser(ProviderParserBase):

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
        relative_case_of = self._find_one_of(msg, (u'נפגע מרכב', u'על תאונה', u'רוכב אופנוע'))
        if relative_case_of is not None:
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
