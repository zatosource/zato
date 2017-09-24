# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import CACHE as _COMMON_CACHE
from zato.common.broker_message import CACHE
from zato.common.odb.model import Cache, CacheMemcached
from zato.common.odb.query import cache_memcached_list
from zato.server.service.internal import AdminService
from zato.server.service.internal.cache import common_instance_hook
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'cache_builtin'
model = CacheMemcached
label = 'a Memcached cache definition'
broker_message = CACHE
broker_message_prefix = 'MEMCACHED_'
list_func = cache_memcached_list

# ################################################################################################################################

instance_hook = common_instance_hook

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = CacheMemcached.name,
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
