# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# SQLAlchemy
from sqlalchemy.dialects import mysql, sqlite
from sqlalchemy.sql.selectable import Select

# Zato
from zato.common import UNITTEST

# Python 2/3 compatibility
from past.builtins import basestring

# ################################################################################################################################

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class QueryCtx(object):
    __slots__ = 'idx', 'is_string', 'query', 'string', 'select'

    def __init__(self):
        self.idx = None       # type: int
        self.is_string = None # type: bool
        self.query = None     # type: object
        self.string = None    # type: str
        self.select = None    # type: Select

    def to_dict(self):
        return {
            'idx': self.idx,
            'is_string': self.is_string,
            'query': self.query,
            'string': self.string,
            'select': self.select,
        }

# ################################################################################################################################
# ################################################################################################################################

class UnittestCursor(object):

    def __init__(self, result=None):
        self.result = result or []

    def close(self, *args, **kwargs):
        pass

    def fetchall(self, *args, **kwargs):
        return self.result or []

    def _getter(self, *args, **kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################

class UnittestSession(object):

    def __init__(self, engine):
        # type: (UnittestEngine)
        self.engine = engine

    def execute(self, query, *args, **kwargs):

        # Increase the execution counter each time we are invoked
        self.engine.config['query_idx'] += 1

        query_ctx = QueryCtx()
        query_ctx.idx = self.engine.config['query_idx']
        query_ctx.is_string = isinstance(query, basestring)
        query_ctx.query = query

        if query_ctx.is_string:
            query_ctx.string = query

        elif isinstance(query, Select):
            query_ctx.select = query

        callback_func = self.engine.config['callback_func']
        data = callback_func(query_ctx)

        return UnittestCursor(data)

    def begin(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################

class UnittestEngine(object):
    """ An SQL engine used only in unittests, one that does not actually connect to any database.
    """
    name = UNITTEST.SQL_ENGINE

    def __init__(self, engine_url, config):
        # type: (str, dict)
        self.engine_url = engine_url
        self.config = config

        # How many times we have been called, counted from 0, hence we start from -1
        self.config['query_idx'] = -1

    def connect(self):
        return UnittestSession(self)

    _contextual_connect = connect

# ################################################################################################################################
# ################################################################################################################################

class SQLRow(object):
    def __init__(self, data=None):
        self.data = data # type: object

    def __getitem__(self, key):
        return getattr(self.data, key.name, None)

# ################################################################################################################################
# ################################################################################################################################
