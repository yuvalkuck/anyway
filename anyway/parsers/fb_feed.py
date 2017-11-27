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
PARSE_START_INDICATOR = u'חובשים ופראמדיקים'
PARSE_END_INDICATOR = u'התקבל דיווח במוקד 101 של מד"א במרחב'
REGEX_HEBREW_RANGE = u'ת..א'

app = init_flask()
db = SQLAlchemy(app)


# ##################################################################

class ProcessParser(object):
    def __init__(self):
        try:
            self._api = GraphAPI()
            # self._api.access_token = self._api.get_app_access_token(APP_ID, APP_SECRET)
            self._posts = ()
        except GraphAPIError as e:
            logging.error('can not obtain access token,abort (%s)'.format(e.message))

    def has_access(self):
        return self._api.access_token is not None

    def read_data(self):

        self._posts = (
            {
                'message': u'*דובר מד"א, זכי הלר  בשעה 20:31 התקבל דיווח במוקד 101 של מד"א במרחב איילון על רוכב אופניים חשמליים שנפגע מרכב בשדרות דוד המלך בלוד. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח אסף הרופא  צעיר כבן 22 במצב בינוני עם חבלות ראש ובגב.'},
            {
                'message': u'*דובר מד"א, זכי הלר  בשעה 20:56 התקבל דיווח במוקד 101 של מד"א במרחב ירושלים על צעיר שנדקר ככה"נ במהלך קטטה ברח\' צונדק בשכונת רמות בירושלים. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח צעיר כבן 25 במצב בהכרה עם פצע דקירה בפלג גופו העליון.'},
            {
                'message': u'*דובר מד"א, זכי הלר  בשעה 18:50 התקבל דיווח במוקד 101 של מד"א במרחב גלבוע על תאונה חזיתית בין שני כלי רכב בכביש 79 בין משהד לציפורי. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח 2 פצועים במצב בינוני, מהם: גבר כבן 64 עם חבלת חזה מפונה לבי"ח העמק.  וגבר כבן 49 עם חבלת חזה מפונה לבי"ח האיטלקי בנצרת.'},
            {
                'message': u'*דובר מד"א, זכי הלר  בשעה 17:07 התקבל דיווח במוקד 101 של מד"א במרחב איילון על רוכב אופניים חשמליים שנפגע מרכב בשדרות מיכה רייסר בלוד. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח אסף הרופא  ילד כבן 11 במצב בינוני עם חבלת ראש.'},
            {
                'message': u'*דובר מד"א, זכי הלר  בשעה 13:34 התקבל דיווח במוקד 101 של מד"א במרחב ירדן על רוכב אופנוע שהחליק בשטח, סמוך לקיבוץ גדות. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח זיו בצפת צעיר כבן 24 במצב בינוני, עם חבלות בגב ובגפיים.'},
            {
                'message': u'*דובר מד"א, זכי הלר :*הבוקר בשעה 05:51 התקבל דיווח במוקד 101 של מד"א במרחב נגב, על הולך רגל שנפגע מרכב ברחוב נסים אלקיים, סמוך למועדון הפורום. בבאר שבע. חובשים ופראמדיקים של מד"א העניקו טיפול רפואי ופינו לבי"ח סורוקה צעיר כבן 22 במצב בינוני עם חבלות בבטן ובגפיים.'},
            {
                'message': u'*דובר מד"א, זכי הלר  בשעה 08:49 התקבל דיווח במוקד 101 של מד"א במרחב נגב על שני רוכבי אופניים שהחליקו בשביל עפר סמוך למושב מסלול. חובשים ופראמדיקים של מד"א העניקו טיפול רפואי ופינו לבי"ח סורוקה גבר כבן 48 במצב בינוני, עם חבלות בראש, בחזה ובגפיים, ופצוע נוסף במצב קל.'}
        )
        return True
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
                if msg.find(PARSE_END_INDICATOR) < 0:
                    continue
                if self.has_one_of(msg, (u'נפגע מרכב', u'על תאונה', u'רוכב אופנוע')):
                    subject = msg[
                              msg.find(PARSE_END_INDICATOR) + len(PARSE_END_INDICATOR):msg.find(PARSE_START_INDICATOR)]
                    address_of = self.find_address(subject, (u'ברחוב', u"ברח'", u'בשדרות', u"בשד'", u'בדרך'))
                    if address_of > 0:
                        address = subject[address_of:]
                        print address + "\n"

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


def main():
    #    msg = u'*דובר מד"א, זכי הלר  בשעה 20:31 התקבל דיווח במוקד 101 של מד"א במרחב איילון על רוכב אופניים חשמליים שנפגע מרכב בשדרות דוד המלך בלוד. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח אסף הרופא  צעיר כבן 22 במצב בינוני עם חבלות ראש ובגב.'
    # msg = u'כרמל על רוכב אופנוע שנפגע ממשאית בכביש 70 על גשר מחלף יגור לכיוון צפון.'
    # subject = msg[msg.find(PARSE_END_INDICATOR) + len(PARSE_END_INDICATOR):msg.find(PARSE_START_INDICATOR)]

    parser = ProcessParser()
    if not parser.read_data():
        logging.debug('no data to process,abort')
        return
    parser.parse()
