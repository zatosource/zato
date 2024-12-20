# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# dictalchemy
from zato.common.ext.dictalchemy.utils import asdict

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import CACHE as _COMMON_CACHE
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
get_list_docs = 'built-in cache definitions'
broker_message = CACHE
broker_message_prefix = 'BUILTIN_'
list_func = cache_builtin_list
skip_create_integrity_error = True
skip_if_exists = True
skip_input_params = ['cache_id']
output_optional_extra = ['current_size', 'cache_id']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    # Common functionality first ..
    common_instance_hook(self, input, instance, attrs)

    # .. now, if this is an update, we need to ensure that we have
    # a handle to cache_id. It will be provided on input from web-admin
    # but enmasse will not have it so we need to look it up ourselfves.
    if not input.get('cache_id'):
        if attrs.is_edit:
            with attrs._meta_session.no_autoflush:
                result = attrs._meta_session.query(CacheBuiltin.cache_id).\
                    filter(CacheBuiltin.id==input.id).\
                    filter(CacheBuiltin.cluster_id==self.server.cluster_id).\
                    one()

            instance.cache_id = result.cache_id

# ################################################################################################################################

def response_hook(self, input, _ignored, attrs, service_type):

    if service_type == 'create_edit':
        self.response.payload.cache_id = self.response.payload.id

    elif service_type == 'get_list':

        for item in self.response.payload:

            # Note that below we are catching a KeyError in get_size.
            # This is because we know that item.name exists in the database,
            # otherwise we would not have found it during the iteration,
            # but it may not exist yet in RAM. This will happen when enmasse
            # runs with a fresh cluster - the database may be updated but our in-RAM
            # storage not yet.

            try:
                item.current_size = self.cache.get_size(_COMMON_CACHE.TYPE.BUILTIN, item.name)
            except KeyError:
                item.current_size = 0

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    if service_type == 'delete':
        input.cache_type = _COMMON_CACHE.TYPE.BUILTIN

# ################################################################################################################################

class Get(AdminService):
    """ Returns configuration of a cache definition.
    """
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

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = CacheBuiltin.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################

class Clear(AdminService):
    """ Clears out a cache by its ID - deletes all keys and values.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'cache_id')

    def handle(self):
        cache = self.server.odb.get_cache_builtin(self.server.cluster_id, self.request.input.cache_id)
        self.cache.clear(_COMMON_CACHE.TYPE.BUILTIN, cache.name)

# ################################################################################################################################
