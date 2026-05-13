# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# This is an internal version of zato.common.json_ which only loads the core libraries,
# without any other additions. This is important in the CLI where every millisecond counts.

# stdlib
from datetime import date, datetime, time
from decimal import Decimal
from json import load, loads

# uJSON
try:
    from ujson import dump, dumps
except ImportError:
    from json import dump, dumps

load = load
dump = dump
_dumps = dumps

def handle_default(obj):
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, '_asdict'):
        return obj._asdict()
    if hasattr(obj, 'asdict'):
        return obj.asdict()
    raise TypeError('Object of type {} is not JSON serializable'.format(type(obj).__name__))

def dumps(obj, **kwargs):
    kwargs['default'] = handle_default
    return _dumps(obj, **kwargs)

json_dumps = dumps
json_loads = loads
