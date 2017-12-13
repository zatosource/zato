# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# dictalchemy
from dictalchemy.utils import asdict

# Zato
from zato.common import CACHE as _COMMON_CACHE
from zato.common.broker_message import CACHE
from zato.common.odb.model import CacheBuiltin
from zato.common.odb.query import cache_builtin_list
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.internal.cache import common_instance_hook
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'cache_builtin'
model = CacheBuiltin
label = 'a built-in cache definition'
broker_message = CACHE
broker_message_prefix = 'BUILTIN_'
list_func = cache_builtin_list
output_optional_extra = ['current_size']

# ################################################################################################################################

instance_hook = common_instance_hook

# ################################################################################################################################

def response_hook(self, input, _ignored, attrs, service_type):
    if service_type == 'get_list':
        for item in self.response.payload:
            item.current_size = self.cache.get_size(_COMMON_CACHE.TYPE.BUILTIN, item.name)

# ################################################################################################################################

class Get(AdminService):

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id')
        output_required = ('name', 'is_active', 'is_default', 'cache_type', Int('max_size'), Int('max_item_size'),
            Bool('extend_expiry_on_get'), Bool('extend_expiry_on_set'), 'sync_method', 'persistent_storage',
            Int('current_size'))

    def handle(self):
        response = asdict(self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.cache_id))
        response['current_size'] = self.cache.get_size(_COMMON_CACHE.TYPE.BUILTIN, response['name'])

        self.response.payload = response

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

class Clear(AdminService):

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id')

    def handle(self):
        cache = self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.cache_id)
        self.cache.clear(_COMMON_CACHE.TYPE.BUILTIN, cache.name)

# ################################################################################################################################
