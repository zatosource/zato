# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# JSON libraries used by Zato tend to be changed from time to time
# and this is the place where .dumps and .loads can be imported from
# so as not to require each part of Zato to know what library to use,
# unless they have some specific needs in which case they can just
# import their own required library themselves.

# stdlib
from datetime import date, timezone
from json import load, loads

# BSON
from bson import ObjectId

# uJSON
try:
    from ujson import dump, dumps as json_dumps
except ImportError:
    from json import dump, dumps as json_dumps

# Zato
from zato.common.typing_ import datetime_, datetimez

# ################################################################################################################################
# ################################################################################################################################

# These are needed for pyflakes

# Note that dumps is defined in a function below
dump  = dump

load  = load
loads = loads

# ################################################################################################################################
# ################################################################################################################################

_utc = timezone.utc

# ################################################################################################################################
# ################################################################################################################################

def _ensure_serializable(value, simple_type=(str, dict, int, float, list, tuple, set)):

    if value is not None:

        if not isinstance(value, simple_type):

            # Useful in various contexts
            if isinstance(value, (date, datetime_, datetimez)):

                # If it should be a time-zone-aware datetime object
                # but it does not have any TZ, assume UTC.
                if isinstance(value, datetimez):
                    if not value.tzinfo:
                        value = value.replace(tzinfo=_utc)

                # Now, we can format it as a string object
                value = value.isoformat()

            # Always use Unicode
            elif isinstance(value, bytes):
                value = value.decode('utf8')

            # For MongoDB queries
            elif isinstance(value, ObjectId):
                value = 'ObjectId({})'.format(value)

            # For Zato models
            elif hasattr(value, 'to_dict'):
                value = value.to_dict()

            else:
                # We do not know how to serialize it
                raise TypeError('Cannot serialize `{}` ({})'.format(value, type(value)))

    return value

# ################################################################################################################################

def dumps(data, indent=4):

    if data is not None:

        # Make sure we can serialize all the values ..
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = _ensure_serializable(value)

        # .. check if it's a list of models ..
        elif data and isinstance(data, list) and hasattr(data[0], 'to_dict'):
            _data = []
            for item in data:
                _item = item.to_dict()
                _data.append(_item)
            data = _data

        # .. serialize non-simple types ..
        else:
            data = _ensure_serializable(data)

    return json_dumps(data, indent=indent)

# ################################################################################################################################
