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

# Zato
from zato.common import UNITTEST

# ################################################################################################################################

if 0:
    from sqlalchemy.sql.selectable import Select

    Select = Select

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class QueryInfo(object):
    __slots__ = 'idx', 'is_string', 'data', 'string', 'select'

    def __init__(self):
        self.idx = None       # type: int
        self.is_string = None # type: bool
        self.data = None      # type: object
        self.string = None # type: str
        self.select = None     # type: Select

# ################################################################################################################################

class UnittestCursor(object):

    def __init__(self, result=None):
        self.result = result

    def close(self, *args, **kwargs):
        pass

    def fetchall(self, *args, **kwargs):
        return self.result or []

    def _getter(self, *args, **kwargs):
        pass

# ################################################################################################################################

class UnittestSession(object):

    def __init__(self, engine):
        # type: (UnittestEngine)
        self.engine = engine

        # How many times we have been called
        self.idx = 0

    def execute(self, query, *args, **kwargs):

        # Increase the execution counter each time we are invoked
        self.idx += 1

        if not isinstance(query, basestring):
            compiled = query.compile(dialect=mysql.dialect())
            print(109, type(query))
            print(111, compiled)
            print(112, compiled.bind_names)
            print(113, compiled.params)
            print(114, compiled)
            print(115, compiled.binds)
            for name in sorted(dir(compiled)):
                print(222, name)
            print(333, self.engine)
        return UnittestCursor()

    def begin(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

# ################################################################################################################################

class UnittestEngine(object):
    """ An SQL engine used only in unittests, one that does not actually connect to any database.
    """
    name = UNITTEST.SQL_ENGINE

    def __init__(self, engine_url, config):
        # type: (str, dict)
        self.engine_url = engine_url
        self.config = config

    def connect(self):
        return UnittestSession(self)

    _contextual_connect = connect

# ################################################################################################################################
