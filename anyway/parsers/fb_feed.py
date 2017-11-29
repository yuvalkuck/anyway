# -*- coding: utf-8 -*-
# from datetime import datetime
import logging

from facebook import GraphAPI, GraphAPIError
from flask.ext.sqlalchemy import SQLAlchemy

from ..models import City
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
            self._api.access_token = self._api.get_app_access_token(APP_ID, APP_SECRET)
            self._posts = []
            self._city_criteria = []
        except GraphAPIError as e:
            logging.error('can not obtain access token,abort (%s)'.format(e.message))

    def has_access(self):
        return self._api.access_token is not None

    def read_data(self):

        # self._posts = [
        #     {
        #         'message': u'*דובר מד"א, זכי הלר  בשעה 20:31 התקבל דיווח במוקד 101 של מד"א במרחב איילון על רוכב אופניים חשמליים שנפגע מרכב בשדרות דוד המלך בלוד. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח אסף הרופא  צעיר כבן 22 במצב בינוני עם חבלות ראש ובגב.'},
        #     {
        #         'message': u'*דובר מד"א, זכי הלר  בשעה 20:56 התקבל דיווח במוקד 101 של מד"א במרחב ירושלים על צעיר שנדקר ככה"נ במהלך קטטה ברח\' צונדק בשכונת רמות בירושלים. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח צעיר כבן 25 במצב בהכרה עם פצע דקירה בפלג גופו העליון.'},
        #     {
        #         'message': u'*דובר מד"א, זכי הלר  בשעה 18:50 התקבל דיווח במוקד 101 של מד"א במרחב גלבוע על תאונה חזיתית בין שני כלי רכב בכביש 79 בין משהד לציפורי. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח 2 פצועים במצב בינוני, מהם: גבר כבן 64 עם חבלת חזה מפונה לבי"ח העמק.  וגבר כבן 49 עם חבלת חזה מפונה לבי"ח האיטלקי בנצרת.'},
        #     {
        #         'message': u'*דובר מד"א, זכי הלר  בשעה 17:07 התקבל דיווח במוקד 101 של מד"א במרחב איילון על רוכב אופניים חשמליים שנפגע מרכב בשדרות מיכה רייסר בלוד. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח אסף הרופא  ילד כבן 11 במצב בינוני עם חבלת ראש.'},
        #     {
        #         'message': u'*דובר מד"א, זכי הלר  בשעה 13:34 התקבל דיווח במוקד 101 של מד"א במרחב ירדן על רוכב אופנוע שהחליק בשטח, סמוך לקיבוץ גדות. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח זיו בצפת צעיר כבן 24 במצב בינוני, עם חבלות בגב ובגפיים.'},
        #     {
        #         'message': u'*דובר מד"א, זכי הלר :*הבוקר בשעה 05:51 התקבל דיווח במוקד 101 של מד"א במרחב נגב, על הולך רגל שנפגע מרכב ברחוב נסים אלקיים, סמוך למועדון הפורום. בבאר שבע. חובשים ופראמדיקים של מד"א העניקו טיפול רפואי ופינו לבי"ח סורוקה צעיר כבן 22 במצב בינוני עם חבלות בבטן ובגפיים.'},
        #     {
        #         'message': u'*דובר מד"א, זכי הלר  בשעה 08:49 התקבל דיווח במוקד 101 של מד"א במרחב נגב על שני רוכבי אופניים שהחליקו בשביל עפר סמוך למושב מסלול. חובשים ופראמדיקים של מד"א העניקו טיפול רפואי ופינו לבי"ח סורוקה גבר כבן 48 במצב בינוני, עם חבלות בראש, בחזה ובגפיים, ופצוע נוסף במצב קל.'}
        #     {
        #         'message': u' בשעה 08:11 התקבל דיווח במוקד 101 של מד"א במרחב איילון על אופנוע שנפגע מרכב ברחוב יוסף לישנסקי פינת האצ"ל בראשל"צ. חובשים ופראמדיקים של מד"א מעניקים טיפול רפואי ומפנים לבי"ח אסף הרופא צעיר כבן 26 במצב בינוני עם חבלות בגפיים.  ופצוע נוסף במצב קל לבי"ח וולפסון.'}
        # ]
        # return True

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
        suitable_posts = []
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
                        suitable_posts.append({
                            'post': post,
                            'searchin': subject[address_of:].strip(u' .'),
                        })

        if not suitable_posts:
            return  # we found nothing - no need to process anything
        self._city_criteria = db.session.query(City.search_heb,City.shortname_heb, City.symbol_code) \
            .order_by(City.search_priority.desc()) \
            .all()
        for post in suitable_posts:
            print post['post']['message']+"\n"
            for city in self._city_criteria:
                criteria = u'ב' + city.search_heb
                criteria_pos = post['searchin'].find(criteria)
                if city.shortname_heb != None and criteria_pos < 0: # if we have short name and we can not find match
                    criteria = u'ב' + city.shortname_heb
                    criteria_pos = post['searchin'].find(criteria)
                if criteria_pos >= 0:
                    post['city_symbol_code'] = city.symbol_code
                    post['city_pos'] = criteria_pos
                    post['search_address'] = post['searchin'][:criteria_pos].strip()
                    break # we just find it, there is no reason to continue

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
    parser = ProcessParser()
    if not parser.read_data():
        logging.debug('no data to process,abort')
        return
    parser.parse()

# WITH onlycity AS
#   (SELECT m.id,
#           m.severity,
#           m.created,
#           extract(dow from m.created) day_of_week,
#           m."dayType" day_type,
#           c.search_heb as city_name,
#    			c.search_priority,
#    			strpos(c.search_heb, m.address) as address_index,
#    			ROW_NUMBER() OVER(PARTITION BY m.id ORDER BY c.search_priority desc, strpos(c.search_heb, m.address) desc) as rn
