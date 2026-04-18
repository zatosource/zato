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

def _get_security_by_id(server, sec_base_id):
    """ Look up security definition name from its ID via the config store.
    """
    for item in server.config_store.get_list('security'):
        if item['id'] == sec_base_id:
            return item['name']
    raise Exception('Security definition with id `{}` not found'.format(sec_base_id))

def _get_user_id(server, security):
    """ Resolve a security definition name to its user_id. Raises if unknown.
    """
    item = server.config_store.get('security', security)
    if item is not None:
        return item['id']
    resolved = server.sec_user_id(security)
    if resolved is None:
        raise Exception('Cannot resolve user_id for security definition `{}`'.format(security))
    return resolved

def _merged_acl_for_user(server, security, extra_row=None, exclude_perm_id=None):
    """ Merged pub/sub pattern lists for a security definition as they would look
    after `extra_row` is added and `exclude_perm_id` is removed.
    """
    rows = []
    for perm_row in server.config_store.get_list('pubsub_permission'):
        if perm_row['security'] != security:
            continue
        if exclude_perm_id is not None and perm_row['id'] == exclude_perm_id:
            continue
        rows.append(perm_row)
    if extra_row is not None:
        rows.append(extra_row)

    pub_patterns = []
    sub_patterns = []
    for row in rows:
        for pub_item in row['pub_topics']:
            if pub_item and pub_item not in pub_patterns:
                pub_patterns.append(pub_item)
        for sub_item in row['sub_topics']:
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

        subscriptions = self.server.config_store.get_list('pubsub_subscription')

        for item in items:
            item['name'] = item['security']

            pub_topics = item['pub_topics']
            sub_topics = item['sub_topics']

            pattern_lines = []
            for pub_item in pub_topics:
                pattern_lines.append('pub={}'.format(pub_item))
            for sub_item in sub_topics:
                pattern_lines.append('sub={}'.format(sub_item))
            item['pattern'] = '\n'.join(pattern_lines)

            has_pub = len(pub_topics) > 0
            has_sub = len(sub_topics) > 0
            if has_pub and has_sub:
                item['access_type'] = 'publisher-subscriber'
            elif has_pub:
                item['access_type'] = 'publisher'
            elif has_sub:
                item['access_type'] = 'subscriber'
            else:
                item['access_type'] = ''

            security = item['security']
            count = 0
            for subscription in subscriptions:
                if subscription['security'] == security:
                    count += 1
            item['subscription_count'] = count

        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub permission.
    """
    input = 'sec_base_id', '-pub_topics', '-sub_topics', '-cluster_id'
    output = 'id', 'security'

    def handle(self):
        input = self.request.input

        sec_base_id = input.sec_base_id
        security = _get_security_by_id(self.server, sec_base_id)

        pub_topics = input.get('pub_topics') or []
        sub_topics = input.get('sub_topics') or []

        if isinstance(pub_topics, str):
            pub_topics = [item.strip() for item in pub_topics.split(',') if item.strip()]
        if isinstance(sub_topics, str):
            sub_topics = [item.strip() for item in sub_topics.split(',') if item.strip()]

        data = {
            'security': security,
            'sec_base_id': sec_base_id,
            'pub_topics': pub_topics,
            'sub_topics': sub_topics,
        }

        user_id = _get_user_id(self.server, security)

        with self.server.auth_update_lock(user_id):
            perm_id = next_id()
            data['id'] = perm_id

            new_pub, new_sub = _merged_acl_for_user(self.server, security, extra_row=data)
            _push_acl(self.server, user_id, new_pub, new_sub)

            self.server.config_store.set('pubsub_permission', perm_id, data)

        self.response.payload.id = perm_id
        self.response.payload.security = security

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an existing pub/sub permission.
    """
    input = 'id', 'sec_base_id', '-pub_topics', '-sub_topics', '-cluster_id'
    output = 'id', 'security'

    def handle(self):
        input = self.request.input

        perm_id = input.id
        sec_base_id = input.sec_base_id
        security = _get_security_by_id(self.server, sec_base_id)

        pub_topics = input.get('pub_topics') or []
        sub_topics = input.get('sub_topics') or []

        if isinstance(pub_topics, str):
            pub_topics = [item.strip() for item in pub_topics.split(',') if item.strip()]
        if isinstance(sub_topics, str):
            sub_topics = [item.strip() for item in sub_topics.split(',') if item.strip()]

        user_id = _get_user_id(self.server, security)

        with self.server.auth_update_lock(user_id):
            data = {
                'id': perm_id,
                'security': security,
                'sec_base_id': sec_base_id,
                'pub_topics': pub_topics,
                'sub_topics': sub_topics,
            }

            new_pub, new_sub = _merged_acl_for_user(
                self.server, security, extra_row=data, exclude_perm_id=perm_id,
            )
            _push_acl(self.server, user_id, new_pub, new_sub)

            self.server.config_store.delete('pubsub_permission', perm_id)
            self.server.config_store.set('pubsub_permission', perm_id, data)

        self.response.payload.id = perm_id
        self.response.payload.security = security

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

        security = existing['security']
        user_id = _get_user_id(self.server, security)

        with self.server.auth_update_lock(user_id):
            new_pub, new_sub = _merged_acl_for_user(
                self.server, security, exclude_perm_id=perm_id,
            )
            _push_acl(self.server, user_id, new_pub, new_sub)

            self.server.config_store.delete('pubsub_permission', perm_id)

# ################################################################################################################################
# ################################################################################################################################
