# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

"""
A set of settings kept in an SQLite database.
"""

# stdlib
import os
from logging import getLogger

# SQLAlchemy
from sqlalchemy import Column, create_engine, Integer, Sequence, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

Base = declarative_base()

# ################################################################################################################################

class Setting(Base):
    __tablename__ = 'settings'
    __table_args__ = (UniqueConstraint('name'), {})

    id = Column(Integer, Sequence('settings_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(Text, nullable=True)
    data_type = Column(String(20), nullable=False)

# ################################################################################################################################

class DATA_TYPE:
    INTEGER = 'integer'
    STRING = 'string'

data_type_handler = {
    DATA_TYPE.INTEGER: int,
    DATA_TYPE.STRING: lambda value: value,
}

# ################################################################################################################################

class SettingsDB(object):
    """ Keeps simple settings in an SQLite database. It's new in 3.0 so to ease in migration from pre-3.0 releases
    the class takes care itself of making sure that its underlying database actually exists - a future Zato version
    will simply assume that it does.
    """
    def __init__(self, db_path, session):
        self.db_path = db_path
        self.session = session

        # Older environments did not have this database
        if not os.path.exists(self.db_path):
            self.create_db()

    def get_engine(self):
        return create_engine('sqlite:///{}'.format(self.db_path))

    def create_db(self):
        Base.metadata.create_all(self.get_engine())

    def get(self, name, default=None, needs_object=False):
        data = self.session.query(Setting).\
            filter(Setting.name==name).\
            first() or None

        if needs_object:
            return data

        return data_type_handler[data.data_type](data.value) if data else default

    def set(self, name, value, data_type=DATA_TYPE.INTEGER):
        s = self.get(name, needs_object=True) or Setting()
        s.name = name
        s.value = value
        s.data_type = data_type

        self.session.add(s)
        self.session.commit()

# ################################################################################################################################
