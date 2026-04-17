# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService
from zato_server_core import next_id

# ################################################################################################################################
# ################################################################################################################################

def _get_sec_name_by_id(server, sec_base_id):
    """ Look up security definition name from its ID via the config store.
    """
    for item in server.config_store.get_list('security'):
        if item.get('id') == sec_base_id:
            return item['name']
    raise Exception('Security definition with id `{}` not found'.format(sec_base_id))

def _sec_user_id(server, sec_name):
    """ Resolve a sec-def name to its `user_id`. Raises if unknown.
    """
    item = server.config_store.get('security', sec_name)
    if item is not None:
        return item['id']
    resolved = server.sec_user_id(sec_name)
    if resolved is None:
        raise Exception('Cannot resolve user_id for sec-def `{}`'.format(sec_name))
    return resolved

def _merged_acl_for_user(server, sec_name, extra_row=None, exclude_perm_id=None):
    """ Merged pub/sub pattern lists for `sec_name` as they would look
    after `extra_row` is added and `exclude_perm_id` is removed.
    """
    rows = []
    for perm_row in server.config_store.get_list('pubsub_permission'):
        if perm_row['security'] != sec_name:
            continue
        if exclude_perm_id is not None and perm_row['id'] == exclude_perm_id:
            continue
        rows.append(perm_row)
    if extra_row is not None:
        rows.append(extra_row)

    pub_patterns = []
    sub_patterns = []
    for row in rows:
        for pub_item in row['pub'] or []:
            if pub_item and pub_item not in pub_patterns:
                pub_patterns.append(pub_item)
        for sub_item in row['sub'] or []:
            if sub_item and sub_item not in sub_patterns:
                sub_patterns.append(sub_item)
    return pub_patterns, sub_patterns

def _push_acl(server, user_id, pub_patterns, sub_patterns):
    if pub_patterns or sub_patterns:
        server.broker_client.set_acl(user_id, pub_patterns, sub_patterns)
    else:
        server.broker_client.remove_acl(user_id)

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

        user_id = _sec_user_id(self.server, sec_name)

        with self.server.auth_update_lock(user_id):
            perm_id = next_id()
            data['id'] = perm_id

            new_pub, new_sub = _merged_acl_for_user(self.server, sec_name, extra_row=data)
            _push_acl(self.server, user_id, new_pub, new_sub)

            self.server.config_store.set('pubsub_permission', perm_id, data)

        self.response.payload.id = perm_id
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

        perm_id = input.id
        sec_base_id = input.sec_base_id
        sec_name = _get_sec_name_by_id(self.server, sec_base_id)

        pub = input.get('pub') or []
        sub = input.get('sub') or []

        if isinstance(pub, str):
            pub = [pattern.strip() for pattern in pub.split(',') if pattern.strip()]
        if isinstance(sub, str):
            sub = [pattern.strip() for pattern in sub.split(',') if pattern.strip()]

        user_id = _sec_user_id(self.server, sec_name)

        with self.server.auth_update_lock(user_id):
            data = {
                'id': perm_id,
                'security': sec_name,
                'sec_base_id': sec_base_id,
                'pub': pub,
                'sub': sub,
            }

            new_pub, new_sub = _merged_acl_for_user(
                self.server, sec_name, extra_row=data, exclude_perm_id=perm_id,
            )
            _push_acl(self.server, user_id, new_pub, new_sub)

            self.server.config_store.delete('pubsub_permission', perm_id)
            self.server.config_store.set('pubsub_permission', perm_id, data)

        self.response.payload.id = perm_id
        self.response.payload.security = sec_name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub permission.
    """
    input = 'id',

    def handle(self):
        perm_id = self.request.input.id
        existing = self.server.config_store.get('pubsub_permission', perm_id)
        if existing is None:
            return

        sec_name = existing['security']
        user_id = _sec_user_id(self.server, sec_name)

        with self.server.auth_update_lock(user_id):
            new_pub, new_sub = _merged_acl_for_user(
                self.server, sec_name, exclude_perm_id=perm_id,
            )
            _push_acl(self.server, user_id, new_pub, new_sub)

            self.server.config_store.delete('pubsub_permission', perm_id)

# ################################################################################################################################
# ################################################################################################################################
