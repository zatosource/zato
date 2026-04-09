# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Boolean
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'outgoing_ftp'

_get_output = 'id', 'name', 'is_active', 'host', 'port', '-user', '-acct', '-timeout', Boolean('-dircache'), '-default_directory'

# ################################################################################################################################
# ################################################################################################################################

class GetByID(AdminService):
    """ Returns an FTP connection by its ID.
    """
    input = 'cluster_id', 'id'
    output = _get_output

    def handle(self):
        target_id = str(self.request.input.id)
        items = self.server.config_store.get_list(_entity_type)
        for item in items:
            if str(item.get('id')) == target_id:
                self.response.payload = item
                return

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing FTP connections.
    """
    input = 'cluster_id'
    output = _get_output
    output_repeated = True

    def handle(self):
        items = self.server.config_store.get_list(_entity_type)
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing FTP connection.
    """
    input = 'cluster_id', 'name', 'is_active', 'host', 'port', Boolean('dircache'), '-user', '-acct', '-timeout', \
        '-default_directory'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        data = {}
        for key in ('name', 'is_active', 'host', 'port', 'dircache', 'user', 'acct', 'timeout', 'default_directory'):
            value = input.get(key)
            if value is not None and value != '':
                data[key] = value

        name = input.name
        self.server.config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing FTP connection.
    """
    input = 'id', 'cluster_id', 'name', 'is_active', 'host', 'port', Boolean('dircache'), '-user', '-acct', '-timeout', \
        '-default_directory'
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
            raise Exception('Outgoing FTP connection with id `{}` not found'.format(target_id))

        for key in ('name', 'is_active', 'host', 'port', 'dircache', 'user', 'acct', 'timeout', 'default_directory'):
            value = input.get(key)
            if value is not None and value != '':
                existing[key] = value
        existing['id'] = input.id
        existing['name'] = input.name

        if old_name != input.name:
            self.server.config_store.delete(_entity_type, old_name)

        self.server.config_store.set(_entity_type, input.name, existing)

        self.response.payload.id = existing.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing FTP connection.
    """
    input = 'id'

    def handle(self):
        target_id = str(self.request.input.id)
        for item in self.server.config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                self.server.config_store.delete(_entity_type, item['name'])
                return
        raise Exception('Outgoing FTP connection with id `{}` not found'.format(target_id))

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of an outgoing FTP connection.
    """
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
