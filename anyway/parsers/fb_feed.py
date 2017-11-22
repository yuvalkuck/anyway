# -*- coding: utf-8 -*-
import json
from datetime import datetime
import logging
from flask.ext.sqlalchemy import SQLAlchemy
from ..utilities import init_flask, time_delta, decode_hebrew
import facebook

ACCESS_PAGE_ID = u'עדכוני-חדשות-601595769890923'

APP_ID = '156391101644523'
APP_SECRET = '02137c44e7ce09b1e708bc8edc9e7c69'
CLIENT_SECRET = '5823a2f9c966291009b8a42fb52b8cdf'
KIT_API_VER = '1.0'

app = init_flask()
db = SQLAlchemy(app)

# ##################################################################


def main():
    api = facebook.GraphAPI()
    access_token = api.get_app_access_token(APP_ID,APP_SECRET)
    pass
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