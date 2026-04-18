# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

# Zato
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _is_oauth(item):
    st = item.get('sec_type')
    t = item.get('type')
    return st == 'bearer_token' or t == 'bearer_token'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Bearer token definitions available.
    """
    input = 'cluster_id', Int('-cur_page'), Bool('-paginate'), '-query'
    output = 'id', 'name', 'is_active', 'username', 'client_id_field', 'client_secret_field', 'grant_type', \
        '-auth_server_url', '-scopes', '-extra_fields', '-data_format'

    def handle(self):
        items = self.server.config_manager.get_list('security')
        out = [item for item in items if _is_oauth(item)]
        self.response.payload = self._paginate_list(out)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Bearer token definition.
    """
    input = 'cluster_id', 'name', 'is_active', 'username', 'client_id_field', \
        'client_secret_field', 'grant_type', 'data_format', '-auth_server_url', '-scopes', '-extra_fields'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        name = input.name

        if self.server.config_manager.get('security', name):
            raise Exception('Bearer token definition `{}` already exists'.format(name))

        self.server.config_manager.set('security', name, {
            'type': 'bearer_token',
            'name': name,
            'is_active': input.is_active,
            'username': input.username,
            'password': uuid4().hex,
            'client_id_field': input.client_id_field,
            'client_secret_field': input.client_secret_field,
            'grant_type': input.grant_type,
            'data_format': input.data_format,
            'auth_server_url': input.get('auth_server_url') or '',
            'scopes': input.get('scopes') or '',
            'extra_fields': input.get('extra_fields') or '',
        })

        item = self.server.config_manager.get('security', name)

        self.response.payload.id = item['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Bearer token definition.
    """
    input = 'id', 'cluster_id', 'name', 'is_active', 'username', 'client_id_field', \
        'client_secret_field', 'grant_type', 'data_format', '-auth_server_url', '-scopes', '-extra_fields'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input
        name = input.name

        items = self.server.config_manager.get_list('security')
        old_name = None
        for item in items:
            if _is_oauth(item) and str(item['id']) == str(input.id):
                old_name = item['name']
                break

        if not old_name:
            raise Exception('Bearer token definition not found')

        existing = self.server.config_manager.get('security', old_name)
        if not existing:
            raise Exception('Bearer token definition not found')

        if name != old_name:
            if self.server.config_manager.get('security', name):
                raise Exception('Bearer token definition `{}` already exists'.format(name))
            self.server.config_manager.delete('security', old_name)

        existing['name'] = name
        existing['is_active'] = input.is_active
        existing['username'] = input.username
        existing['password'] = existing.get('password', '')
        existing['client_id_field'] = input.client_id_field
        existing['client_secret_field'] = input.client_secret_field
        existing['grant_type'] = input.grant_type
        existing['data_format'] = input.data_format
        existing['auth_server_url'] = input.get('auth_server_url') or ''
        existing['scopes'] = input.get('scopes') or ''
        existing['extra_fields'] = input.get('extra_fields') or ''
        existing['type'] = 'bearer_token'

        self.server.config_manager.set('security', name, existing)

        self.response.payload.id = existing['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of a Bearer token definition.
    """
    password_required = False

    input = 'password', '-id', '-name'
    output = 'id',

    def handle(self):
        input = self.request.input
        name = input.get('name', '')

        password = self.server.decrypt(input.password) if input.password else ''

        if self.password_required:
            if not password:
                raise Exception('Password must not be empty')

        if not name and input.get('id'):
            for item in self.server.config_manager.get_list('security'):
                if _is_oauth(item) and str(item.get('id')) == str(input.id):
                    name = item['name']
                    break

        if not name:
            raise Exception('Either ID or name are required on input')

        existing = self.server.config_manager.get('security', name)
        if not existing:
            raise Exception('Bearer token definition not found')

        existing['password'] = password
        existing['type'] = 'bearer_token'
        self.server.config_manager.set('security', name, existing)

        self.response.payload.id = existing['id']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a Bearer token definition.
    """
    input = 'id'

    def handle(self):
        items = self.server.config_manager.get_list('security')
        target_name = None
        for item in items:
            if _is_oauth(item) and str(item.get('id')) == str(self.request.input.id):
                target_name = item['name']
                break

        if not target_name:
            raise Exception('Bearer token definition not found')

        self.server.config_manager.delete('security', target_name)

# ################################################################################################################################
# ################################################################################################################################
