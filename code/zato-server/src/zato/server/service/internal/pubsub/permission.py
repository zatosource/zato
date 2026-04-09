# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

def _get_sec_name_by_id(server, sec_base_id):
    """ Look up security definition name from its ID via the config store.
    """
    for item in server.rust_config_store.get_list('security'):
        if item.get('id') == sec_base_id:
            return item['name']
    raise Exception('Security definition with id `{}` not found'.format(sec_base_id))

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub permissions.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_permission_get_list_request'
        response_elem = 'zato_pubsub_permission_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'pattern', 'access_type', 'sec_base_id', 'subscription_count'

    def handle(self):
        items = self.server.rust_config_store.get_list('pubsub_permission')
        self.response.payload[:] = items

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub permission.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_create_request'
        response_elem = 'zato_pubsub_permission_create_response'
        input_required = 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id'
        output_required = 'id', 'name'

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

        self.server.rust_config_store.set('pubsub_permission', sec_name, data)

        self.response.payload.id = sec_name
        self.response.payload.name = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_edit_request'
        response_elem = 'zato_pubsub_permission_edit_response'
        input_required = 'id', 'sec_base_id', 'pattern', 'access_type'
        input_optional = 'cluster_id',
        output_required = 'id', 'name'

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

        self.server.rust_config_store.set('pubsub_permission', sec_name, data)

        self.response.payload.id = input.id
        self.response.payload.name = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_permission_delete_request'
        response_elem = 'zato_pubsub_permission_delete_response'
        input_required = 'id',

    def handle(self):
        input_id = self.request.input.id

        for item in self.server.rust_config_store.get_list('pubsub_permission'):
            if item.get('id') == input_id or item.get('security') == input_id:
                sec_name = item.get('security') or item.get('name')
                self.server.rust_config_store.delete('pubsub_permission', sec_name)
                return

        raise Exception('Pub/sub permission with id `{}` not found'.format(input_id))

# ################################################################################################################################
# ################################################################################################################################
