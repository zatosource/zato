# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# This is an internal version of zato.common.json_ which only loads the core libraries,
# without any other additions. This is important in the CLI where every millisecond counts.

# stdlib
from json import load, loads

# uJSON
from ujson import dump, dumps

load = load
dump = dump

json_dumps = dumps
json_loads = loads
