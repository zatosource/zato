# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads as json_loads

# pysimdjson
try:
    from simdjson import Parser as SIMDJSONParser # type: ignore
except ImportError:
    has_simdjson = False
else:
    has_simdjson = True

# ################################################################################################################################
# ################################################################################################################################

class BasicParser:
    def parse(self, value):
        return json_loads(value)

# ################################################################################################################################
# ################################################################################################################################

if has_simdjson:
    JSONParser = SIMDJSONParser # type: ignore
else:
    JSONParser = BasicParser

# ################################################################################################################################
# ################################################################################################################################
