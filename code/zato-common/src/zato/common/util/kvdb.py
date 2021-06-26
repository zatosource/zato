# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

def has_redis_sentinels(config):
    return config.get('use_redis_sentinels', False)

# ################################################################################################################################
