# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import warnings

# Silence SQLAlchemy 2.0 warnings
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

# Explicitly ignore the warning at the Python level
warnings.filterwarnings('ignore', message='.*MovedIn20Warning.*')
warnings.filterwarnings('ignore', message='.*these feature.*are not compatible with SQLAlchemy 2.0.*')

# dictalchemy
from zato.common.ext.dictalchemy import make_class_dictable

# SQLAlchemy
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base

# Zato
from zato.common.json_internal import json_dumps, json_loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

Base:'any_' = declarative_base()
make_class_dictable(Base)

# ################################################################################################################################
# ################################################################################################################################

class _JSON(TypeDecorator):
    """ Python 2.7 ships with SQLite 3.8 whereas it was 3.9 that introduced the JSON datatype.
    Because of it, we need our own wrapper around JSON data.
    """
    cache_ok = True  # This type is safe to use in a cache key

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
