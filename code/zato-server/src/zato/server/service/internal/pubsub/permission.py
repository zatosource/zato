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
    input = '-cluster_id',

    def handle(self):
        items = self.server.config_store.get_list('pubsub_permission')
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub permission.
    """
    input = 'sec_base_id', '-pub', '-sub', '-cluster_id'
    output = 'id', 'security'

    def handle(self):
        input = self.request.input

        sec_base_id = input.sec_base_id
        sec_name = _get_sec_name_by_id(self.server, sec_base_id)

        pub = input.get('pub') or []
        sub = input.get('sub') or []

        if isinstance(pub, str):
            pub = [t.strip() for t in pub.split(',') if t.strip()]
        if isinstance(sub, str):
            sub = [t.strip() for t in sub.split(',') if t.strip()]

        data = {
            'security': sec_name,
            'sec_base_id': sec_base_id,
            'pub': pub,
            'sub': sub,
        }

        self.server.config_store.set('pubsub_permission', sec_base_id, data)

        stored = self.server.config_store.get('pubsub_permission', sec_base_id)
        self.response.payload.id = stored['id']
        self.response.payload.security = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission.
    """
    input = 'id', 'sec_base_id', '-pub', '-sub', '-cluster_id'
    output = 'id', 'security'

    def handle(self):
        input = self.request.input

        sec_base_id = input.sec_base_id
        sec_name = _get_sec_name_by_id(self.server, sec_base_id)
        old_key = str(input.id)

        pub = input.get('pub') or []
        sub = input.get('sub') or []

        if isinstance(pub, str):
            pub = [t.strip() for t in pub.split(',') if t.strip()]
        if isinstance(sub, str):
            sub = [t.strip() for t in sub.split(',') if t.strip()]

        # Find the old entry by its ID and delete it if the key changed
        for item in self.server.config_store.get_list('pubsub_permission'):
            if str(item.get('id')) == old_key:
                old_sec_base_id = item.get('sec_base_id', '')
                if old_sec_base_id and old_sec_base_id != sec_base_id:
                    self.server.config_store.delete('pubsub_permission', old_sec_base_id)
                break

        data = {
            'security': sec_name,
            'sec_base_id': sec_base_id,
            'pub': pub,
            'sub': sub,
        }

        self.server.config_store.set('pubsub_permission', sec_base_id, data)

        stored = self.server.config_store.get('pubsub_permission', sec_base_id)
        self.response.payload.id = stored['id']
        self.response.payload.security = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission.
    """
    input = 'id',

    def handle(self):
        input_id = self.request.input.id

        for item in self.server.config_store.get_list('pubsub_permission'):
            if str(item.get('id')) == str(input_id) or item.get('sec_base_id') == str(input_id):
                key = item.get('sec_base_id') or item.get('security')
                self.server.config_store.delete('pubsub_permission', key)
                return

        raise Exception('Pub/sub permission with id `{}` not found'.format(input_id))

# ################################################################################################################################
# ################################################################################################################################
