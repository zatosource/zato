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

# BSON
from bson import ObjectId

# simdjson is not available on Mac
try:
    from simdjson import load, loads
except ImportError:
    from ujson import load, loads

# uJSON
from ujson import dump, dumps as json_dumps

# Python 2/3 compatibility
from builtins import bytes

# ################################################################################################################################

# These are needed for pyflakes

# Note that dumps is defined in a function below
dump  = dump

load  = load
loads = loads

# ################################################################################################################################

def dumps(value, indent=4, expected=(str, dict, int, float, list, tuple, set)):

    if value is not None:

        if not isinstance(value, expected):

            # Useful in various contexts
            if isinstance(value, datetime):
                value = value.isoformat()

            # Always use Unicode
            elif isinstance(value, bytes):
                value = value.decode('utf8')

            # For MongoDB queries
            elif isinstance(value, ObjectId):
                value = 'ObjectId({})'.format(value)

            else:
                # We do not know how to serialize it
                raise TypeError('Cannot serialize `{}` ({})'.format(value, type(value)))

    return json_dumps(value, indent=indent)

# ################################################################################################################################

