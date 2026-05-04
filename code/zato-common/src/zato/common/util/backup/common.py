# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys

# Zato
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

def json_response(success:'bool', **kwargs:'str') -> 'str':
    result = {'success': success}
    result.update(kwargs)
    out = dumps(result)
    return out

# ################################################################################################################################

def write_response(response:'str') -> 'None':
    sys.stdout.write(response)
    sys.stdout.write('\n')
    sys.stdout.flush()

# ################################################################################################################################
# ################################################################################################################################
