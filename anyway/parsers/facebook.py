# -*- coding: utf-8 -*-
import json
from datetime import datetime
import logging
import facebook
from flask.ext.sqlalchemy import SQLAlchemy
from ..utilities import init_flask, time_delta, decode_hebrew

CONSUMER_KEY = 'xC8S9xrsS1pFa82EeFe5h2zjX'
CONSUMER_SECRET = 'GhC5nTdmhdhbPGFCGFbnMoK1OR1J7m2RdnnyxaVeKFJCr9kAVb'
ACCESS_TOKEN = '930058064773959681-NRoWXRzmQ8lWQdF3TYfbKE4EDlbz0GE'
ACCESS_TOKEN_SECRET = '3DLMcGV6UUgPFfLBU9SO8Ayo19g8l8H6JiAKP327Vzd8b'

app = init_flask()
db = SQLAlchemy(app)

# ##################################################################


def main():
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