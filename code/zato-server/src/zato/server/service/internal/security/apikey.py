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

def _is_apikey(item):
    return item.get('sec_type') == 'apikey' or item.get('type') == 'apikey'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of API keys available.
    """

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_apikey_get_list_request'
        response_elem = 'zato_security_apikey_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'username'
        output_optional:'any_' = 'header'

    def handle(self) -> 'None':
        items = self.server.rust_config_store.get_list('security')
        out = [item for item in items if _is_apikey(item)]
        self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new API key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_create_request'
        response_elem = 'zato_security_apikey_create_response'
        input_required = 'name', 'is_active'
        input_optional:'any_' = 'cluster_id', 'header'
        output_required = 'id', 'name', 'header'

    def handle(self) -> 'None':
        input = self.request.input
        name = input.name
        header = input.header or self.server.api_key_header

        if self.server.rust_config_store.get('security', name):
            raise Exception('API key `{}` already exists'.format(name))

        self.server.rust_config_store.set('security', name, {
            'type': 'apikey',
            'name': name,
            'is_active': input.is_active,
            'username': 'Zato-Not-Used-' + uuid4().hex,
            'password': self.server.encrypt(uuid4().hex),
            'header': header,
        })

        item = self.server.rust_config_store.get('security', name)

        self.response.payload.id = item['id']
        self.response.payload.name = name
        self.response.payload.header = header

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an API key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_edit_request'
        response_elem = 'zato_security_apikey_edit_response'
        input_required = 'id', 'name', 'is_active'
        input_optional:'any_' = 'cluster_id', 'header'
        output_required = 'id', 'name', 'header'

    def handle(self) -> 'None':
        input = self.request.input
        name = input.name
        header = input.header or self.server.api_key_header

        items = self.server.rust_config_store.get_list('security')
        old_name = None
        for item in items:
            if _is_apikey(item) and str(item['id']) == str(input.id):
                old_name = item['name']
                break

        if not old_name:
            raise Exception('API key not found')

        existing = self.server.rust_config_store.get('security', old_name)
        if not existing:
            raise Exception('API key not found')

        if name != old_name:
            if self.server.rust_config_store.get('security', name):
                raise Exception('API key `{}` already exists'.format(name))
            self.server.rust_config_store.delete('security', old_name)

        existing['name'] = name
        existing['is_active'] = input.is_active
        existing['username'] = existing.get('username', '')
        existing['password'] = existing.get('password', '')
        existing['header'] = header
        existing['type'] = 'apikey'

        self.server.rust_config_store.set('security', name, existing)

        self.response.payload.id = existing['id']
        self.response.payload.name = name
        self.response.payload.header = header

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of an API key.
    """
    password_required = False

    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_change_password_request'
        response_elem = 'zato_security_apikey_change_password_response'
        input_required = 'password1', 'password2'
        input_optional = 'id', 'name'
        output_required = 'id',

    def handle(self) -> 'None':
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
                if _is_apikey(item) and str(item.get('id')) == str(input.id):
                    name = item['name']
                    break

        if not name:
            raise Exception('Either ID or name are required on input')

        existing = self.server.rust_config_store.get('security', name)
        if not existing:
            raise Exception('API key not found')

        existing['password'] = password1
        existing['type'] = 'apikey'
        self.server.rust_config_store.set('security', name, existing)

        self.response.payload.id = existing['id']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an API key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_apikey_delete_request'
        response_elem = 'zato_security_apikey_delete_response'
        input_required = 'id'

    def handle(self) -> 'None':
        items = self.server.rust_config_store.get_list('security')
        target_name = None
        for item in items:
            if _is_apikey(item) and str(item.get('id')) == str(self.request.input.id):
                target_name = item['name']
                break

        if not target_name:
            raise Exception('API key not found')

        self.server.rust_config_store.delete('security', target_name)

# ################################################################################################################################
# ################################################################################################################################
