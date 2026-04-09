# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

def _get_sec_name_by_id(server, sec_base_id):
    """ Look up security definition name from its ID via the config store.
    """
    for item in server.config_store.get_list('security'):
        if item.get('id') == sec_base_id:
            return item['name']
    raise Exception('Security definition with id `{}` not found'.format(sec_base_id))

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub permissions.
    """
    input = 'cluster_id',
    output = 'id', 'name', 'pattern', 'access_type', 'sec_base_id', 'subscription_count'

    def handle(self):
        items = self.server.config_store.get_list('pubsub_permission')
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub permission.
    """
    input = 'sec_base_id', 'pattern', 'access_type', '-cluster_id'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input

        if not input.pattern or not input.pattern.strip():
            raise Exception('At least one pattern is required')

        patterns = [item.strip() for item in input.pattern.splitlines() if item.strip()]

        if not patterns:
            raise Exception('At least one valid pattern is required')

        sec_name = _get_sec_name_by_id(self.server, input.sec_base_id)

        data = {
            'security': sec_name,
            'name': sec_name,
            'sec_base_id': input.sec_base_id,
            'access_type': input.access_type,
            'pattern': '\n'.join(patterns),
        }

        self.server.config_store.set('pubsub_permission', sec_name, data)

        self.response.payload.id = sec_name
        self.response.payload.name = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission.
    """
    input = 'id', 'sec_base_id', 'pattern', 'access_type', '-cluster_id'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input

        if not input.pattern or not input.pattern.strip():
            raise Exception('At least one pattern is required')

        patterns = [item.strip() for item in input.pattern.splitlines() if item.strip()]

        if not patterns:
            raise Exception('At least one valid pattern is required')

        sec_name = _get_sec_name_by_id(self.server, input.sec_base_id)

        data = {
            'id': input.id,
            'security': sec_name,
            'name': sec_name,
            'sec_base_id': input.sec_base_id,
            'access_type': input.access_type,
            'pattern': '\n'.join(patterns),
        }

        self.server.config_store.set('pubsub_permission', sec_name, data)

        self.response.payload.id = input.id
        self.response.payload.name = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission.
    """
    input = 'id',

    def handle(self):
        input_id = self.request.input.id

        for item in self.server.config_store.get_list('pubsub_permission'):
            if item.get('id') == input_id or item.get('security') == input_id:
                sec_name = item.get('security') or item.get('name')
                self.server.config_store.delete('pubsub_permission', sec_name)
                return

        raise Exception('Pub/sub permission with id `{}` not found'.format(input_id))

# ################################################################################################################################
# ################################################################################################################################
