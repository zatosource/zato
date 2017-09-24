# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import CACHE as _COMMON_CACHE
from zato.common.broker_message import CACHE
from zato.common.odb.model import Cache, CacheBuiltin
from zato.common.odb.query import cache_builtin_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'cache_builtin'
model = CacheBuiltin
label = 'a cache definition'
broker_message = CACHE
broker_message_prefix = 'BUILTIN_'
list_func = cache_builtin_list
output_optional_extra = ['current_size']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    # If the cache instance currently saved is the default one, find all other definitions and make sure they are not default.
    if attrs.is_create_edit and instance.is_default:

        with attrs._meta_session.no_autoflush:
            attrs._meta_session.query(Cache).\
                filter(Cache.is_default.is_(True)).\
                filter(Cache.id.isnot(instance.id)).\
                update({'is_default':False})

# ################################################################################################################################

def response_hook(self, input, _ignored, attrs, service_type):
    if service_type == 'get_list':
        for item in self.response.payload:
            item.current_size = self.cache.get_size(_COMMON_CACHE.TYPE.BUILTIN, item.name)

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = CacheBuiltin.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    __metaclass__ = DeleteMeta

# ################################################################################################################################
