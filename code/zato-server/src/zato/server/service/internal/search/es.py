# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.exception import BadRequest
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'elastic_search'

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

class GetList(AdminService):
    """ Returns a list of ElasticSearch connections.
    """
    input = 'cluster_id'
    output = ('id', 'name', Bool('is_active'), 'hosts', Int('timeout'), 'body_as', '-opaque1')
    output_repeated = True

    def handle(self):
        items = self.server.config_store.get_list(_entity_type)
        self.response.payload[:] = items

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates an ElasticSearch connection.
    """
    input = ('cluster_id', 'name', Bool('is_active'), 'hosts', Int('timeout'), 'body_as', '-opaque1')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_store

        if store.get(_entity_type, input.name):
            raise BadRequest(self.cid, 'An ElasticSearch connection `{}` already exists in this cluster'.format(input.name))

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'hosts': input.hosts,
            'timeout': int(input.timeout),
            'body_as': input.body_as,
        }
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1

        store.set(_entity_type, input.name, data)
        saved = store.get(_entity_type, input.name) or data
        self.response.payload.id = saved.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an ElasticSearch connection.
    """
    input = ('id', 'cluster_id', 'name', Bool('is_active'), 'hosts', Int('timeout'), 'body_as', '-opaque1')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_store

        old = _item_by_id(store.get_list(_entity_type), input.id)
        if not old:
            raise BadRequest(self.cid, 'No such an ElasticSearch connection `{}` in this cluster'.format(input.name))

        old_name = old.get('name')
        if old_name != input.name:
            other = store.get(_entity_type, input.name)
            if other and str(other.get('id')) != str(input.id):
                raise BadRequest(self.cid, 'An ElasticSearch connection `{}` already exists in this cluster'.format(input.name))

        data = dict(old)
        data.update({
            'id': old.get('id', input.id),
            'name': input.name,
            'is_active': input.is_active,
            'hosts': input.hosts,
            'timeout': int(input.timeout),
            'body_as': input.body_as,
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
    """ Deletes an ElasticSearch connection.
    """
    input = ('-id', '-name', '-should_raise_if_missing')

    def handle(self):
        input = self.request.input
        store = self.server.config_store
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
                raise BadRequest(self.cid, 'Could not find an ElasticSearch connection instance with {} `{}`'.format(
                    attr_name, attr_value))
            return

        store.delete(_entity_type, item['name'])

# ################################################################################################################################
