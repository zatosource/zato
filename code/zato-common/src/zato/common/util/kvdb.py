# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
#from zato.common.util.eval_ import as_bool

# ################################################################################################################################

def has_redis_sentinels(config):
    return config.get('use_redis_sentinels', False)

# ################################################################################################################################
