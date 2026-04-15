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

class GetList(AdminService):
    _filter_by = 'name',

    input = Int('-cur_page'), Bool('-paginate'), '-query', '-cluster_id', '-needs_password'
    output = 'id', 'name', 'is_active', 'username', 'realm', '-password'

    def handle(self):
        items = self.server.config_store.get_list('security')
        out = []
        for item in items:
            if item.get('sec_type') == 'basic_auth' or item.get('type') == 'basic_auth':
                if self.request.input.get('needs_password') and item.get('password'):
                    item['password'] = self.crypto.decrypt(item['password'])
                out.append(item)
        self.response.payload = self._paginate_list(out)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):

    input = 'name', 'is_active', 'username', 'realm', '-cluster_id'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input

        existing = self.server.config_store.get('security', input.name)
        if existing:
            raise Exception('HTTP Basic Auth definition `{}` already exists'.format(input.name))

        password = uuid4().hex

        self.server.config_store.set('security', input.name, {
            'type': 'basic_auth',
            'name': input.name,
            'is_active': input.is_active,
            'username': input.username,
            'realm': input.realm or '',
            'password': password,
        })

        item = self.server.config_store.get('security', input.name)

        self.response.payload.id = item['id']
        self.response.payload.name = item['name']

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):

    input = 'name', 'is_active', 'username', 'realm', '-id', '-cluster_id', '-old_name'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input

        old_name = input.get('old_name') or input.name

        existing = self.server.config_store.get('security', old_name)
        if not existing:
            raise Exception('HTTP Basic Auth definition `{}` not found'.format(old_name))

        existing['name'] = input.name
        existing['is_active'] = input.is_active
        existing['username'] = input.username
        existing['realm'] = input.realm or ''
        existing['type'] = 'basic_auth'

        if old_name != input.name:
            self.server.config_store.delete('security', old_name)

        self.server.config_store.set('security', input.name, existing)

        item = self.server.config_store.get('security', input.name)

        self.response.payload.id = item['id']
        self.response.payload.name = item['name']

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):

    password_required = False

    input = 'password1', 'password2', '-id', '-name'
    output = 'id',

    def handle(self):
        input = self.request.input
        name = input.get('name') or ''

        if not name and input.get('id'):
            for item in self.server.config_store.get_list('security'):
                if item.get('id') == input.id:
                    name = item['name']
                    break

        if not name:
            raise Exception('Either ID or name are required on input')

        password1 = self.server.decrypt(input.password1) if input.password1 else ''
        password2 = self.server.decrypt(input.password2) if input.password2 else ''

        if password1 != password2:
            raise Exception('Passwords need to be the same')

        existing = self.server.config_store.get('security', name)
        if not existing:
            raise Exception('HTTP Basic Auth definition `{}` not found'.format(name))

        existing['password'] = password1
        self.server.config_store.set('security', name, existing)

        self.response.payload.id = existing['id']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):

    input = 'id',

    def handle(self):
        items = self.server.config_store.get_list('security')
        target_name = None
        for item in items:
            if item.get('id') == self.request.input.id:
                target_name = item['name']
                break

        if not target_name:
            raise Exception('HTTP Basic Auth definition with id `{}` not found'.format(self.request.input.id))

        self.server.config_store.delete('security', target_name)

# ################################################################################################################################
# ################################################################################################################################
