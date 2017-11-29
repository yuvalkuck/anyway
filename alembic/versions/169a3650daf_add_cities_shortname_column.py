# -*- coding: utf-8 -*-
"""add cities shortname column

Revision ID: 169a3650daf
Revises: 6708baa8438
Create Date: 2017-11-29 15:02:33.226000

"""

# revision identifiers, used by Alembic.
revision = '169a3650daf'
down_revision = '6708baa8438'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer
import six

TABLE_NAME = 'cities'
_assign_symbol_shotname = {
    8300: u'ראשל"צ',
    3000: u'י-ם',
    5000: u'ת"א'
}


def downgrade():
    op.drop_column(TABLE_NAME, 'shortname_heb')


def upgrade():
    op.add_column(TABLE_NAME,
                  sa.Column('shortname_heb', sa.String(length=50), nullable=True))

    cities_table = table(TABLE_NAME,
                         column('symbol_code', Integer()),
                         column('shortname_heb', String())
                         )

    for symbol, shortname in six.iteritems(_assign_symbol_shotname):
        op.execute(
            cities_table.update().
                where(cities_table.c.symbol_code == symbol).
                values({'shortname_heb': shortname})
        )
