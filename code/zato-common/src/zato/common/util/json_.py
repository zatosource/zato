# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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

# Library pysimdjson is temporarily disabled
if False:
    from simdjson import loads as json_loads # type: ignore
    JSONParser = SIMDJSONParser # type: ignore
else:
    from json import loads as json_loads
    JSONParser = BasicParser

# ################################################################################################################################
# ################################################################################################################################
