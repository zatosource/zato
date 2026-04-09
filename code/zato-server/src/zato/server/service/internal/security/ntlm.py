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

def _is_ntlm(item):
    return item.get('sec_type') == 'ntlm' or item.get('type') == 'ntlm'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of NTLM definitions available.
    """

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_ntlm_get_list_request'
        response_elem = 'zato_security_ntlm_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'username')

    def handle(self):
        items = self.server.rust_config_store.get_list('security')
        out = [item for item in items if _is_ntlm(item)]
        self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new NTLM definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_ntlm_create_request'
        response_elem = 'zato_security_ntlm_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'username')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        name = input.name

        if self.server.rust_config_store.get('security', name):
            raise Exception('NTLM definition `{}` already exists'.format(name))

        self.server.rust_config_store.set('security', name, {
            'type': 'ntlm',
            'name': name,
            'is_active': input.is_active,
            'username': input.username,
            'password': uuid4().hex,
        })

        item = self.server.rust_config_store.get('security', name)

        self.response.payload.id = item['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an NTLM definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_ntlm_edit_request'
        response_elem = 'zato_security_ntlm_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'username')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        name = input.name

        items = self.server.rust_config_store.get_list('security')
        old_name = None
        for item in items:
            if _is_ntlm(item) and str(item['id']) == str(input.id):
                old_name = item['name']
                break

        if not old_name:
            raise Exception('NTLM definition not found')

        existing = self.server.rust_config_store.get('security', old_name)
        if not existing:
            raise Exception('NTLM definition not found')

        if name != old_name:
            if self.server.rust_config_store.get('security', name):
                raise Exception('NTLM definition `{}` already exists'.format(name))
            self.server.rust_config_store.delete('security', old_name)

        existing['name'] = name
        existing['is_active'] = input.is_active
        existing['username'] = input.username
        existing['password'] = existing.get('password', '')
        existing['type'] = 'ntlm'

        self.server.rust_config_store.set('security', name, existing)

        self.response.payload.id = existing['id']
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of an NTLM definition.
    """
    password_required = False

    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_ntlm_change_password_request'
        response_elem = 'zato_security_ntlm_change_password_response'
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
                if _is_ntlm(item) and str(item.get('id')) == str(input.id):
                    name = item['name']
                    break

        if not name:
            raise Exception('Either ID or name are required on input')

        existing = self.server.rust_config_store.get('security', name)
        if not existing:
            raise Exception('NTLM definition not found')

        existing['password'] = password1
        existing['type'] = 'ntlm'
        self.server.rust_config_store.set('security', name, existing)

        self.response.payload.id = existing['id']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an NTLM definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_security_ntlm_delete_request'
        response_elem = 'zato_security_ntlm_delete_response'
        input_required = ('id',)

    def handle(self):
        items = self.server.rust_config_store.get_list('security')
        target_name = None
        for item in items:
            if _is_ntlm(item) and str(item.get('id')) == str(self.request.input.id):
                target_name = item['name']
                break

        if not target_name:
            raise Exception('NTLM definition not found')

        self.server.rust_config_store.delete('security', target_name)

# ################################################################################################################################
# ################################################################################################################################
