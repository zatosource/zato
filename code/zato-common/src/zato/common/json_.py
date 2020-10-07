# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# JSON libraries used by Zato tend to be changed from time to time
# and this is the place where .dumps and .loads can be imported from
# so as not to require each part of Zato to know what library to use,
# unless they have some specific needs in which case they can just
# import their own required library themselves.

# stdlib
from datetime import datetime

# simdjson
from simdjson import dump, dumps as json_dumps, load, loads

# Python 2/3 compatibility
from builtins import bytes

# ################################################################################################################################

# These are needed for pyflakes

# Note that dumps is defined in a function below
dump  = dump

load  = load
loads = loads

# ################################################################################################################################

def default_json_handler(value):

    # Useful in various contexts
    if isinstance(value, datetime):
        return value.isoformat()

    # Always use Unicode
    elif isinstance(value, bytes):
        return value.decode('utf8')

    # For MongoDB queries
    elif isinstance(value, ObjectId):
        return 'ObjectId({})'.format(value)

    # We do not know how to serialize it
    raise TypeError('Cannot serialize `{}`'.format(value))

# ################################################################################################################################

def dumps(value, indent=4):
    return json_dumps(value, default=default_json_handler, indent=indent)

# ################################################################################################################################

