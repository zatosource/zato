# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# Zato
from zato.server.service import Int, Bool
from zato.server.service.internal import AdminService

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
    input = 'cluster_id', Int('-cur_page'), Bool('-paginate'), '-query'
    output = 'id', 'name', 'is_active', 'username', '-header'

    def handle(self) -> 'None':
        items = self.server.config_manager.get_list('security')
        out = [item for item in items if _is_apikey(item)]
        self.response.payload = self._paginate_list(out)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new API key.
    """
    input = 'name', 'is_active', '-cluster_id', '-header'
    output = 'id', 'name', 'header'

    def handle(self) -> 'None':
        input = self.request.input
        name = input.name
        header = input.header or self.server.api_key_header

        if self.server.config_manager.get('security', name):
            raise Exception('API key `{}` already exists'.format(name))

        self.server.config_manager.set('security', name, {
            'type': 'apikey',
            'name': name,
            'is_active': input.is_active,
            'username': 'Zato-Not-Used-' + uuid4().hex,
            'password': self.server.encrypt(uuid4().hex),
            'header': header,
        })

        item = self.server.config_manager.get('security', name)

        self.response.payload.id = item['id']
        self.response.payload.name = name
        self.response.payload.header = header

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an API key.
    """
    input = 'id', 'name', 'is_active', '-cluster_id', '-header'
    output = 'id', 'name', 'header'

    def handle(self) -> 'None':
        input = self.request.input
        name = input.name
        header = input.header or self.server.api_key_header

        items = self.server.config_manager.get_list('security')
        old_name = None
        for item in items:
            if _is_apikey(item) and str(item['id']) == str(input.id):
                old_name = item['name']
                break

        if not old_name:
            raise Exception('API key not found')

        existing = self.server.config_manager.get('security', old_name)
        if not existing:
            raise Exception('API key not found')

        if name != old_name:
            if self.server.config_manager.get('security', name):
                raise Exception('API key `{}` already exists'.format(name))
            self.server.config_manager.delete('security', old_name)

        existing['name'] = name
        existing['is_active'] = input.is_active
        existing['username'] = existing.get('username', '')
        existing['password'] = existing.get('password', '')
        existing['header'] = header
        existing['type'] = 'apikey'

        self.server.config_manager.set('security', name, existing)

        self.response.payload.id = existing['id']
        self.response.payload.name = name
        self.response.payload.header = header

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of an API key.
    """
    password_required = False

    input = 'password', '-id', '-name'
    output = 'id',

    def handle(self) -> 'None':
        input = self.request.input
        name = input.get('name', '')

        password = self.server.decrypt(input.password) if input.password else ''

        if self.password_required:
            if not password:
                raise Exception('Password must not be empty')

        if not name and input.get('id'):
            for item in self.server.config_manager.get_list('security'):
                if _is_apikey(item) and str(item.get('id')) == str(input.id):
                    name = item['name']
                    break

        if not name:
            raise Exception('Either ID or name are required on input')

        existing = self.server.config_manager.get('security', name)
        if not existing:
            raise Exception('API key not found')

        existing['password'] = password
        existing['type'] = 'apikey'
        self.server.config_manager.set('security', name, existing)

        self.response.payload.id = existing['id']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an API key.
    """
    input = 'id',

    def handle(self) -> 'None':
        items = self.server.config_manager.get_list('security')
        target_name = None
        for item in items:
            if _is_apikey(item) and str(item.get('id')) == str(self.request.input.id):
                target_name = item['name']
                break

        if not target_name:
            raise Exception('API key not found')

        self.server.config_manager.delete('security', target_name)

# ################################################################################################################################
# ################################################################################################################################
