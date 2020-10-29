# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common.api import UNITTEST

# ################################################################################################################################

logger = logging.getLogger(__name__)

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

    def execute(self, query, *args, **kwargs):
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
