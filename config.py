# -*- coding: utf-8 -*-
import os

#
# This is the configuration file of the application
#
# Please make sure you don't store here any secret information and use environment
# variables
#


SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SENDGRID_USERNAME = os.environ.get('SENDGRID_USERNAME')
SENDGRID_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
SQLALCHEMY_POOL_RECYCLE = 60
if "postgres" in SQLALCHEMY_DATABASE_URI:
    MARKER_INDEX_PROVIDER_TYPE = "PostgreSQL"
else:
    MARKER_INDEX_PROVIDER_TYPE = "SQLite"
if MARKER_INDEX_PROVIDER_TYPE == "PostgreSQL":
    BUILD_MARKER_INDEX_SQL_FILE = './static/data/sql/postgresql-buildrtreeindex.sql'
else:
    BUILD_MARKER_INDEX_SQL_FILE = './static/data/sql/sqlite-buildrtreeindex.sql'

SECRET_KEY = 'aiosdjsaodjoidjioewnioewfnoeijfoisdjf'

# available languages
LANGUAGES = {
    'en': 'English',
    'he': 'עברית',
}