# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import CACHE as _COMMON_CACHE
from zato.common.exception import BadRequest
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'cache'
_skip_if_exists = True

# ################################################################################################################################
# ################################################################################################################################

def _item_by_id(items, id_):
    sid = str(id_)
    for item in items:
        if str(item.get('id')) == sid:
            return item
    return None

# ################################################################################################################################
# ################################################################################################################################

def _clear_other_defaults(server, current_name):
    store = server.config_manager
    for item in store.get_list(_entity_type):
        name = item.get('name')
        if name == current_name or not item.get('is_default'):
            continue
        data = dict(item)
        data['is_default'] = False
        store.set(_entity_type, name, data)

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    """ Returns configuration of a cache definition.
    """
    input = 'cluster_id', 'id'
    output = 'name', Bool('is_active'), Bool('is_default'), 'cache_type', Int('max_size'), Int('max_item_size'), \
        Bool('extend_expiry_on_get'), Bool('extend_expiry_on_set'), 'sync_method', 'persistent_storage', \
        Int('current_size')

    def handle(self):
        item = _item_by_id(self.server.config_manager.get_list(_entity_type), self.request.input.id)
        if not item:
            raise BadRequest(self.cid, 'Could not find cache_builtin instance with id `{}`'.format(self.request.input.id))

        response = dict(item)
        response.setdefault('cache_type', _COMMON_CACHE.TYPE.BUILTIN)
        try:
            response['current_size'] = self.cache.get_size(_COMMON_CACHE.TYPE.BUILTIN, response['name'])
        except Exception:
            response['current_size'] = 0

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of built-in cache definitions.
    """
    input = 'cluster_id', Int('-cur_page'), Bool('-paginate'), '-query'
    output = 'id', 'name', Bool('is_active'), Bool('is_default'), 'cache_type', Int('max_size'), \
        Int('max_item_size'), Bool('extend_expiry_on_get'), Bool('extend_expiry_on_set'), 'sync_method', \
        'persistent_storage', Int('current_size'), '-opaque1'

    def handle(self):
        items = []
        for raw in self.server.config_manager.get_list(_entity_type):
            item = dict(raw)
            item.setdefault('cache_type', _COMMON_CACHE.TYPE.BUILTIN)
            try:
                item['current_size'] = self.cache.get_size(_COMMON_CACHE.TYPE.BUILTIN, item['name'])
            except Exception:
                item['current_size'] = 0
            items.append(item)

        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a built-in cache definition.
    """
    input = 'cluster_id', 'name', Bool('is_active'), Bool('is_default'), 'cache_type', Int('max_size'), \
        Int('max_item_size'), Bool('extend_expiry_on_get'), Bool('extend_expiry_on_set'), 'sync_method', \
        'persistent_storage', '-opaque1'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id

        store = self.server.config_manager
        existing = store.get(_entity_type, input.name)
        if existing and _skip_if_exists:
            self.response.payload.id = existing.get('id', input.name)
            self.response.payload.name = input.name
            return

        if existing and not _skip_if_exists:
            raise BadRequest(self.cid, 'A built-in cache definition `{}` already exists in this cluster'.format(input.name))

        if input.is_default:
            _clear_other_defaults(self.server, None)

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'is_default': input.is_default,
            'max_size': int(input.max_size),
            'max_item_size': int(input.max_item_size),
            'extend_expiry_on_get': input.extend_expiry_on_get,
            'extend_expiry_on_set': input.extend_expiry_on_set,
            'sync_method': input.sync_method,
            'persistent_storage': input.persistent_storage,
        }
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1

        store.set(_entity_type, input.name, data)
        saved = store.get(_entity_type, input.name) or data

        cache_config = Bunch()
        cache_config.name = input.name
        cache_config.cache_type = _COMMON_CACHE.TYPE.BUILTIN
        cache_config.is_active = input.is_active
        cache_config.is_default = input.is_default
        cache_config.max_size = int(input.max_size)
        cache_config.max_item_size = int(input.max_item_size)
        cache_config.extend_expiry_on_get = input.extend_expiry_on_get
        cache_config.extend_expiry_on_set = input.extend_expiry_on_set
        cache_config.sync_method = input.sync_method
        cache_config.persistent_storage = input.persistent_storage
        self.cache.create(cache_config)

        self.response.payload.id = saved.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a built-in cache definition.
    """
    input = 'id', 'cluster_id', 'name', Bool('is_active'), Bool('is_default'), 'cache_type', Int('max_size'), \
        Int('max_item_size'), Bool('extend_expiry_on_get'), Bool('extend_expiry_on_set'), 'sync_method', \
        'persistent_storage', '-opaque1'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_manager

        old = _item_by_id(store.get_list(_entity_type), input.id)
        if not old:
            raise BadRequest(self.cid, 'No such a built-in cache definition `{}` in this cluster'.format(input.name))

        old_name = old.get('name')
        if old_name != input.name:
            other = store.get(_entity_type, input.name)
            if other and str(other.get('id')) != str(input.id):
                raise BadRequest(self.cid, 'A built-in cache definition `{}` already exists in this cluster'.format(input.name))

        if input.is_default:
            _clear_other_defaults(self.server, input.name)

        data = dict(old)
        data.update({
            'id': old.get('id', input.id),
            'name': input.name,
            'is_active': input.is_active,
            'is_default': input.is_default,
            'max_size': int(input.max_size),
            'max_item_size': int(input.max_item_size),
            'extend_expiry_on_get': input.extend_expiry_on_get,
            'extend_expiry_on_set': input.extend_expiry_on_set,
            'sync_method': input.sync_method,
            'persistent_storage': input.persistent_storage,
        })
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1

        if old_name != input.name:
            store.delete(_entity_type, old_name)
        store.set(_entity_type, input.name, data)

        saved = store.get(_entity_type, input.name) or data
        self.response.payload.id = saved.get('id', input.id)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a built-in cache definition.
    """
    input = '-id', '-name', '-should_raise_if_missing'

    def handle(self):
        input = self.request.input
        store = self.server.config_manager
        input_id = input.get('id')
        input_name = input.get('name')

        if not (input_id or input_name):
            raise BadRequest(self.cid, 'Either id or name is required on input')

        item = None
        if input_id:
            item = _item_by_id(store.get_list(_entity_type), input_id)
        if not item and input_name:
            item = store.get(_entity_type, input_name)

        if not item:
            if input.get('should_raise_if_missing', True):
                attr_name = 'id' if input_id else 'name'
                attr_value = input_id if input_id else input_name
                raise BadRequest(self.cid, 'Could not find a built-in cache definition instance with {} `{}`'.format(
                    attr_name, attr_value))
            return

        store.delete(_entity_type, item['name'])

# ################################################################################################################################
# ################################################################################################################################

class Clear(AdminService):
    """ Clears out a cache by its ID - deletes all keys and values.
    """
    input = 'cluster_id', 'id'

    def handle(self):
        item = _item_by_id(self.server.config_manager.get_list(_entity_type), self.request.input.id)
        if not item:
            raise BadRequest(self.cid, 'Could not find cache_builtin instance with id `{}`'.format(self.request.input.id))
        self.cache.clear(_COMMON_CACHE.TYPE.BUILTIN, item['name'])

# ################################################################################################################################
