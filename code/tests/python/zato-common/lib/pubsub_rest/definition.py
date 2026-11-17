# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import secrets

# PyYAML
import yaml

# Zato
from pubsub_rest.transport import Credentials

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The delivery types of a subscription.
Delivery_Pull = 'pull'
Delivery_Push = 'push'

# How many random bytes the password of each API client has.
_password_bytes = 16

# The address that the push endpoints of a test listen on.
_push_host = 'http://127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################

def new_credentials(username:'str') -> 'Credentials':
    """ Returns the credentials of one API client, with a password of its own.
    """
    suffix = secrets.token_hex(_password_bytes)
    password = f'{username}.{suffix}'

    out = Credentials(username, password)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Definition:
    """ The enmasse definition of the topics, the API clients, their permissions and their subscriptions,
    and of the outgoing REST connections of the push subscriptions.
    """

    def __init__(self) -> 'None':
        self.security:'anylist' = []
        self.topics:'anylist' = []
        self.permissions:'anylist' = []
        self.subscriptions:'anylist' = []
        self.outgoing_rest:'anylist' = []

        self._topic_names:'set[str]' = set()

# ################################################################################################################################

    def add_topic(self, topic_name:'str') -> 'None':
        if topic_name not in self._topic_names:
            self._topic_names.add(topic_name)
            self.topics.append({'name': topic_name})

# ################################################################################################################################

    def _add_client(self, username:'str') -> 'Credentials':
        out = new_credentials(username)

        self.security.append({
            'name': out.username,
            'type': 'basic_auth',
            'username': out.username,
            'password': out.password,
        })

        return out

# ################################################################################################################################

    def add_publisher(self, username:'str', topic_names:'strlist') -> 'Credentials':
        """ Adds an API client that may publish to the given topics.
        """
        for topic_name in topic_names:
            self.add_topic(topic_name)

        out = self._add_client(username)

        self.permissions.append({
            'security': out.username,
            'pub': topic_names,
        })

        return out

# ################################################################################################################################

    def add_pull_subscriber(self, username:'str', topic_names:'strlist') -> 'Credentials':
        """ Adds an API client with one pull subscription to the given topics.
        """
        for topic_name in topic_names:
            self.add_topic(topic_name)

        out = self._add_client(username)

        self.permissions.append({
            'security': out.username,
            'sub': topic_names,
        })

        self.subscriptions.append({
            'security': out.username,
            'delivery_type': Delivery_Pull,
            'topic_list': topic_names,
        })

        return out

# ################################################################################################################################

    def add_pattern_client(self, username:'str', pub_patterns:'strlist', sub_patterns:'strlist') -> 'Credentials':
        """ Adds an API client whose permissions are the given patterns, with no subscription of its own.
        """
        out = self._add_client(username)

        permission:'anydict' = {'security': out.username}

        if pub_patterns:
            permission['pub'] = pub_patterns

        if sub_patterns:
            permission['sub'] = sub_patterns

        self.permissions.append(permission)

        return out

# ################################################################################################################################

    def add_pull_subscription(self, username:'str', topic_names:'strlist') -> 'None':
        """ Adds one pull subscription of an API client that already has permissions to the given topics.
        """
        for topic_name in topic_names:
            self.add_topic(topic_name)

        self.subscriptions.append({
            'security': username,
            'delivery_type': Delivery_Pull,
            'topic_list': topic_names,
        })

# ################################################################################################################################

    def add_push_subscriber(self, username:'str', topic_names:'strlist', port:'int', url_path:'str') -> 'Credentials':
        """ Adds a subscriber whose messages the server pushes to the given path of a local endpoint,
        through an outgoing REST connection of its own.
        """
        out = self.add_push_subscriber_at(username, topic_names, f'{_push_host}:{port}', url_path)
        return out

# ################################################################################################################################

    def add_push_subscriber_at(self, username:'str', topic_names:'strlist', host:'str', url_path:'str') -> 'Credentials':
        """ Adds a subscriber whose messages the server pushes to the given path of the given host,
        through an outgoing REST connection of its own.
        """
        for topic_name in topic_names:
            self.add_topic(topic_name)

        out = self._add_client(username)

        self.permissions.append({
            'security': out.username,
            'sub': topic_names,
        })

        self.outgoing_rest.append({
            'name': username,
            'host': host,
            'url_path': url_path,
            'data_format': 'json',
        })

        self.subscriptions.append({
            'security': out.username,
            'delivery_type': Delivery_Push,
            'push_rest_endpoint': username,
            'topic_list': topic_names,
        })

        return out

# ################################################################################################################################

    def to_yaml(self) -> 'str':
        definition:'anydict' = {
            'security': self.security,
        }

        # The connections precede the subscriptions that name them.
        if self.outgoing_rest:
            definition['outgoing_rest'] = self.outgoing_rest

        definition['pubsub_topic'] = self.topics
        definition['pubsub_permission'] = self.permissions
        definition['pubsub_subscription'] = self.subscriptions

        out = yaml.safe_dump(definition, sort_keys=False)
        return out

# ################################################################################################################################
# ################################################################################################################################
