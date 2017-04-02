# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import CACHE as _COMMON_CACHE
from zato.common.broker_message import CACHE
from zato.common.odb.model import CacheBuiltin
from zato.common.odb.query import cache_builtin_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'cache_built'
model = CacheBuiltin
label = 'a cache definition'
broker_message = CACHE
broker_message_prefix = 'BUILTIN_'
list_func = cache_builtin_list
request_as_is = ('max_size', 'max_item_size')

def instance_hook(service, input, instance, attrs):
    instance.sync_method = _COMMON_CACHE.SYNC_METHOD.ASYNC.id

class GetList(AdminService):
    _filter_by = CacheBuiltin.name,
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
