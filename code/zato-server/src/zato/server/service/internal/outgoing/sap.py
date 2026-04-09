# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import time
from uuid import uuid4

# Zato
from zato.common.util.api import ping_sap
from zato.server.service import Integer
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'outgoing_sap'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of SAP RFC connections.
    """
    input = 'cluster_id'
    output = 'id', 'name', 'is_active', 'host', 'user', 'client', 'sysid', Integer('pool_size'), '-sysnr', '-router'

    def handle(self):
        items = self.server.config_store.get_list(_entity_type)
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new SAP RFC connection.
    """
    input = 'cluster_id', 'name', 'is_active', 'host', 'user', 'client', 'sysid', Integer('pool_size'), '-sysnr', '-router'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        data = {
            'name': input.name,
            'is_active': input.is_active,
            'host': input.host,
            'user': input.user,
            'client': input.client,
            'sysid': input.sysid,
            'pool_size': input.pool_size,
            'password': uuid4().hex,
        }
        if input.get('sysnr'):
            data['sysnr'] = input.sysnr
        if input.get('router'):
            data['router'] = input.router

        name = input.name
        self.server.config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a SAP RFC connection.
    """
    input = 'id', 'cluster_id', 'name', 'is_active', 'host', 'user', 'client', 'sysid', Integer('pool_size'), \
        '-sysnr', '-router'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        target_id = str(input.id)
        old_name = None
        existing = None
        for item in self.server.config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id:
                old_name = item['name']
                existing = self.server.config_store.get(_entity_type, old_name)
                if not existing:
                    existing = dict(item)
                break
        if not old_name or not existing:
            raise Exception('SAP connection with id `{}` not found'.format(target_id))

        existing.update({
            'id': input.id,
            'name': input.name,
            'is_active': input.is_active,
            'host': input.host,
            'user': input.user,
            'client': input.client,
            'sysid': input.sysid,
            'pool_size': input.pool_size,
        })
        if input.get('sysnr'):
            existing['sysnr'] = input.sysnr
        if input.get('router'):
            existing['router'] = input.router

        if old_name != input.name:
            self.server.config_store.delete(_entity_type, old_name)

        self.server.config_store.set(_entity_type, input.name, existing)

        self.response.payload.id = existing.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a SAP RFC connection.
    """
    input = 'id'

    def handle(self):
        target_id = str(self.request.input.id)
        for item in self.server.config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                self.server.config_store.delete(_entity_type, item['name'])
                return
        raise Exception('SAP connection with id `{}` not found'.format(target_id))

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of a SAP connection.
    """
    password_required = False

    input = 'id', 'password1', 'password2'

    def handle(self):
        input = self.request.input
        target_id = str(input.id)
        items = self.server.config_store.get_list(_entity_type)
        for item in items:
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                item['password'] = input.password1
                self.server.config_store.set(_entity_type, item['name'], item)
                return

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Pings a SAP connection to check its configuration.
    """
    input = 'id'
    output = 'info'

    def handle(self):
        target_id = str(self.request.input.id)
        items = self.server.config_store.get_list(_entity_type)

        item_name = None
        for item in items:
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                item_name = item['name']
                break

        if not item_name:
            raise Exception('Could not find SAP connection with id `{}`'.format(target_id))

        with self.outgoing.sap[item_name].conn.client() as client:
            start_time = time()
            ping_sap(client)
            response_time = time() - start_time
            self.response.payload.info = 'Ping OK, took:`{0:03.4f} s`'.format(response_time)

# ################################################################################################################################
# ################################################################################################################################
