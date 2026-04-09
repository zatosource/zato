# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import time
from uuid import uuid4

# Zato
from zato.common.util.api import ping_odoo
from zato.server.service import Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'outgoing_odoo'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Odoo connections.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_odoo_get_list_request'
        response_elem = 'zato_outgoing_odoo_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'host', Integer('port'), 'user', 'database', 'protocol',
            Integer('pool_size'))
        output_optional = ('client_type',)
        output_repeated = True

    def handle(self):
        items = self.server.rust_config_store.get_list(_entity_type)
        self.response.payload[:] = items

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Odoo connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_odoo_create_request'
        response_elem = 'zato_outgoing_odoo_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'host', Integer('port'), 'user', 'database', 'protocol',
            Integer('pool_size'))
        input_optional = ('client_type',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        data = {
            'name': input.name,
            'is_active': input.is_active,
            'host': input.host,
            'port': input.port,
            'user': input.user,
            'database': input.database,
            'protocol': input.protocol,
            'pool_size': input.pool_size,
            'password': uuid4().hex,
        }
        if input.get('client_type'):
            data['client_type'] = input.client_type

        name = input.name
        self.server.rust_config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an Odoo connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_odoo_edit_request'
        response_elem = 'zato_outgoing_odoo_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'host', Integer('port'), 'user', 'database', 'protocol',
            Integer('pool_size'))
        input_optional = ('client_type',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        target_id = str(input.id)
        old_name = None
        existing = None
        for item in self.server.rust_config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id:
                old_name = item['name']
                existing = self.server.rust_config_store.get(_entity_type, old_name)
                if not existing:
                    existing = dict(item)
                break
        if not old_name or not existing:
            raise Exception('Odoo connection with id `{}` not found'.format(target_id))

        existing.update({
            'id': input.id,
            'name': input.name,
            'is_active': input.is_active,
            'host': input.host,
            'port': input.port,
            'user': input.user,
            'database': input.database,
            'protocol': input.protocol,
            'pool_size': input.pool_size,
        })
        if input.get('client_type'):
            existing['client_type'] = input.client_type

        if old_name != input.name:
            self.server.rust_config_store.delete(_entity_type, old_name)

        self.server.rust_config_store.set(_entity_type, input.name, existing)

        self.response.payload.id = existing.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an Odoo connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_odoo_delete_request'
        response_elem = 'zato_outgoing_odoo_delete_response'
        input_required = ('id',)

    def handle(self):
        target_id = str(self.request.input.id)
        for item in self.server.rust_config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                self.server.rust_config_store.delete(_entity_type, item['name'])
                return
        raise Exception('Odoo connection with id `{}` not found'.format(target_id))

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of an Odoo connection.
    """
    password_required = False

    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_odoo_change_password_request'
        response_elem = 'zato_outgoing_odoo_change_password_response'
        input_required = 'id', 'password1', 'password2'

    def handle(self):
        input = self.request.input
        target_id = str(input.id)
        items = self.server.rust_config_store.get_list(_entity_type)
        for item in items:
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                item['password'] = input.password1
                self.server.rust_config_store.set(_entity_type, item['name'], item)
                return

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Pings an Odoo connection to check its configuration.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_odoo_ping_request'
        response_elem = 'zato_outgoing_odoo_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):
        target_id = str(self.request.input.id)
        items = self.server.rust_config_store.get_list(_entity_type)

        item_name = None
        for item in items:
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                item_name = item['name']
                break

        if not item_name:
            raise Exception('Could not find Odoo connection with id `{}`'.format(target_id))

        with self.outgoing.odoo[item_name].conn.client() as client:
            start_time = time()
            ping_odoo(client)
            response_time = time() - start_time
            self.response.payload.info = 'Ping OK, took:`{0:03.4f} s`'.format(response_time)

# ################################################################################################################################
# ################################################################################################################################
