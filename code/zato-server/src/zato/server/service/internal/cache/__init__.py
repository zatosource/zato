# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.odb.model import Cache

# ################################################################################################################################

def common_instance_hook(self, input, instance, attrs):
    """ A common instance hook that checks if the cache instance currently saved is the default one,
    and if so, finds all other definitions and make sure they are not default anymore.
    """
    if attrs.is_create_edit and instance.is_default:

        with attrs._meta_session.no_autoflush:
            attrs._meta_session.query(Cache).\
                filter(Cache.is_default.is_(True)).\
                filter(Cache.id != instance.id).\
                update({'is_default':False})

# ################################################################################################################################
