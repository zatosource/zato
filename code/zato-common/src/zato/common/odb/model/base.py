# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# dictalchemy
from dictalchemy import make_class_dictable

# SQLAlchemy
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base

# Zato
from zato.common.json_internal import json_dumps, json_loads

# ################################################################################################################################

Base = declarative_base()
make_class_dictable(Base)

# ################################################################################################################################
# ################################################################################################################################

class _JSON(TypeDecorator):
    """ Python 2.7 ships with SQLite 3.8 whereas it was 3.9 that introduced the JSON datatype.
    Because of it, we need our own wrapper around JSON data.
    """
    @property
    def python_type(self):
        return object

    impl = Text

    def process_bind_param(self, value, dialect):
        return json_dumps(value)

    def process_literal_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value != 'null':
            try:
                return json_loads(value)
            except(ValueError, TypeError):
                return None

# ################################################################################################################################
# ################################################################################################################################
