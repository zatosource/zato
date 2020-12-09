# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import re
import string
from datetime import datetime

# ################################################################################################################################

_re_fs_safe_name = '[{}]'.format(string.punctuation + string.whitespace)

# ################################################################################################################################

def fs_safe_name(value):
    return re.sub(_re_fs_safe_name, '_', value)

# ################################################################################################################################

def fs_safe_now(_utcnow=datetime.utcnow):
    """ Returns a UTC timestamp with any characters unsafe for filesystem names removed.
    """
    return fs_safe_name(_utcnow().isoformat())

# ################################################################################################################################
