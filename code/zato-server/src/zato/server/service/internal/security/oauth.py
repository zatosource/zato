# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# Zato
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _is_oauth(item):
    st = item.get('sec_type')
    t = item.get('type')
    return st in ('oauth', 'bearer_token') or t in ('oauth', 'bearer_token')

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Bearer token definitions available.
    """

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_oauth_get_list_request'
        response_elem = 'zato_security_oauth_get_list_response'
        input_required = 'cluster_id'
        output_required = 'id', 'name', 'is_active', 'username', 'client_id_field', 'client_secret_field', 'grant_type'
        output_optional = 'auth_server_url', 'scopes', 'extra_fields', 'data_format'

    def handle(self):
        items = self.server.rust_config_store.get_list('security')
        out = [item for item in items if _is_oauth(item)]
        self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Bearer token definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_create_request'
        response_elem = 'zato_security_oauth_create_response'
        input_required = 'cluster_id', 'name', 'is_active', 'username', 'client_id_field', \
            'client_secret_field', 'grant_type', 'data_format'
        input_optional = 'auth_server_url', 'scopes', 'extra_fields'
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input
        name = input.name

        if self.server.rust_config_store.get('security', name):
            raise Exception('Bearer token definition `{}` already exists'.format(name))

        self.server.rust_config_store.set('security', name, {
            'type': 'oauth',
            'name': name,
            'is_active': input.is_active,
            'username': input.username,
            'password': uuid4().hex,
            'client_id_field': input.client_id_field,
            'client_secret_field': input.client_secret_field,
            'grant_type': input.grant_type,
            'data_format': input.data_format,
            'auth_server_url': input.get('auth_server_url', ''),
            'scopes': input.get('scopes', ''),
            'extra_fields': input.get('extra_fields', ''),
        })

        item = self.server.rust_config_store.get('security', name)

        self.response.payload.id = item['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a Bearer token definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_edit_request'
        response_elem = 'zato_security_oauth_edit_response'
        input_required = 'id', 'cluster_id', 'name', 'is_active', 'username', 'client_id_field', \
            'client_secret_field', 'grant_type', 'data_format'
        input_optional = 'auth_server_url', 'scopes', 'extra_fields'
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input
        name = input.name

        items = self.server.rust_config_store.get_list('security')
        old_name = None
        for item in items:
            if _is_oauth(item) and str(item['id']) == str(input.id):
                old_name = item['name']
                break

        if not old_name:
            raise Exception('Bearer token definition not found')

        existing = self.server.rust_config_store.get('security', old_name)
        if not existing:
            raise Exception('Bearer token definition not found')

        if name != old_name:
            if self.server.rust_config_store.get('security', name):
                raise Exception('Bearer token definition `{}` already exists'.format(name))
            self.server.rust_config_store.delete('security', old_name)

        existing['name'] = name
        existing['is_active'] = input.is_active
        existing['username'] = input.username
        existing['password'] = existing.get('password', '')
        existing['client_id_field'] = input.client_id_field
        existing['client_secret_field'] = input.client_secret_field
        existing['grant_type'] = input.grant_type
        existing['data_format'] = input.data_format
        existing['auth_server_url'] = input.get('auth_server_url', '')
        existing['scopes'] = input.get('scopes', '')
        existing['extra_fields'] = input.get('extra_fields', '')
        existing['type'] = 'oauth'

        self.server.rust_config_store.set('security', name, existing)

        self.response.payload.id = existing['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of a Bearer token definition.
    """
    password_required = False

    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_change_password_request'
        response_elem = 'zato_security_oauth_change_password_response'
        input_required = 'password1', 'password2'
        input_optional = 'id', 'name'
        output_required = 'id',

    def handle(self):
        input = self.request.input
        name = input.get('name', '')

        password1 = self.server.decrypt(input.password1) if input.password1 else ''
        password2 = self.server.decrypt(input.password2) if input.password2 else ''

        if self.password_required:
            if not password1:
                raise Exception('Password must not be empty')
            if not password2:
                raise Exception('Password must be repeated')

        if password1 != password2:
            raise Exception('Passwords need to be the same')

        if not name and input.get('id'):
            for item in self.server.rust_config_store.get_list('security'):
                if _is_oauth(item) and str(item.get('id')) == str(input.id):
                    name = item['name']
                    break

        if not name:
            raise Exception('Either ID or name are required on input')

        existing = self.server.rust_config_store.get('security', name)
        if not existing:
            raise Exception('Bearer token definition not found')

        existing['password'] = password1
        existing['type'] = 'oauth'
        self.server.rust_config_store.set('security', name, existing)

        self.response.payload.id = existing['id']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a Bearer token definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_oauth_delete_request'
        response_elem = 'zato_security_oauth_delete_response'
        input_required = 'id'

    def handle(self):
        items = self.server.rust_config_store.get_list('security')
        target_name = None
        for item in items:
            if _is_oauth(item) and str(item.get('id')) == str(self.request.input.id):
                target_name = item['name']
                break

        if not target_name:
            raise Exception('Bearer token definition not found')

        self.server.rust_config_store.delete('security', target_name)

# ################################################################################################################################
# ################################################################################################################################
