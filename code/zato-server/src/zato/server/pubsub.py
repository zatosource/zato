# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# gevent
from gevent.lock import RLock

# globre
from globre import compile as globre_compile

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Endpoint(object):
    """ A publisher/subscriber in pub/sub workflows.
    """
    def __init__(self, config):
        self.id = config.id
        self.name = config.name
        self.role = config.role
        self.is_active = config.is_active
        self.is_internal = config.is_internal
        self.hook_service_id = config.hook_service_id

        self.topic_patterns = config.topic_patterns or ''

        self.pub_topic_patterns = []
        self.sub_topic_patterns = []

        self.pub_topics = {}
        self.sub_topics = {}

        self.set_up_patterns()

# ################################################################################################################################

    def set_up_patterns(self):
        data = {
            'topic': self.topic_patterns,
        }

        # is_pub, is_topic -> target set
        targets = {
            (True, True): self.pub_topic_patterns,
            (False, True): self.sub_topic_patterns,
        }

        for key, config in data.iteritems():
            is_topic = key == 'topic'

            for line in config.splitlines():
                line = line.strip()
                if line.startswith('pub=') or line.startswith('sub='):
                    is_pub = line.startswith('pub=')

                    pattern = line[line.find('=')+1:]
                    pattern = globre_compile(pattern)

                    source = (is_pub, is_topic)
                    target = targets[source]
                    target.append(pattern)

                else:
                    logger.warn('Ignoring invalid {} pattern `{}` for `{}` (role:{}) (reason: no pub=/sub= prefix found)'.format(
                        key, line, self.name, self.role))

# ################################################################################################################################

class PubSub(object):
    def __init__(self):
        self.endpoints = {}
        self._security_id_to_endpoint_id = {}
        self._ws_channel_id_to_endpoint_id = {}
        self._lock = RLock()

# ################################################################################################################################

    def set_endpoint(self, config):
        self.endpoints[config.id] = Endpoint(config)

        if config['security_id']:
            self._security_id_to_endpoint_id[config['security_id']] = config.id

        if config['ws_channel_id']:
            self._ws_channel_id_to_endpoint_id[config['ws_channel_id']] = config.id

# ################################################################################################################################

    def _is_allowed(self, target, name, security_id, ws_channel_id):

        if security_id:
            source, id = self._security_id_to_endpoint_id, security_id
        else:
            source, id = self._ws_channel_id_to_endpoint_id, ws_channel_id

        endpoint_id = source[id]
        endpoint = self.endpoints[endpoint_id]

        for elem in getattr(endpoint, target):
            if elem.match(name):
                return True

# ################################################################################################################################

    def is_allowed_pub_topic(self, name, security_id=None, ws_channel_id=None):
        return self._is_allowed('pub_topic_patterns', name, security_id, ws_channel_id)

# ################################################################################################################################

    def is_allowed_sub_topic(self, endpoint_id, name, security_id=None, ws_channel_id=None):
        return self._is_allowed('sub_topic_patterns', name, security_id, ws_channel_id)

# ################################################################################################################################
