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
        self.queue_patterns = config.queue_patterns or ''

        self.pub_topic_patterns = []
        self.pub_queue_patterns = []
        self.sub_topic_patterns = []
        self.sub_queue_patterns = []

        self.pub_topics = {}
        self.pub_queues = {}
        self.sub_topics = {}
        self.sub_queues = {}

        self.set_up_patterns()

# ################################################################################################################################

    def set_up_patterns(self):
        data = {
            'topic': self.topic_patterns,
            'queue': self.queue_patterns,
        }

        # is_pub, is_topic -> target set
        targets = {
            (True, True): self.pub_topic_patterns,
            (True, False): self.pub_queue_patterns,
            (False, True): self.sub_topic_patterns,
            (False, False): self.sub_queue_patterns,
        }

        for key, config in data.iteritems():
            is_topic = key == 'topic'

            for line in config.splitlines():
                line = line.strip()
                if line.startswith('pub=') or line.startswith('sub='):
                    is_pub = line.startswith('pub=')

                    pattern = line[line.find('='):]
                    pattern = globre_compile(pattern)

                    source = (is_pub, is_topic)
                    target = targets[source]
                    target.append(pattern)

                else:
                    logger.warn('Ignoring invalid {} pattern `{}` for `{}` ({})'.format(key, line, self.name, self.role))

# ################################################################################################################################

class PubSub(object):
    def __init__(self):
        self.endpoints = {}
        self._lock = RLock()

# ################################################################################################################################

    def set_endpoint(self, config):
        with self._lock:
            self.endpoints[config.id] = Endpoint(config)

# ################################################################################################################################

    def _is_allowed(self, endpoint_id, target, name):
        endpoint = self.endpoints[endpoint_id]

        for elem in getattr(endpoint, target):
            if elem.match(name):
                return True

# ################################################################################################################################

    def is_allowed_pub_topic(self, endpoint_id, name):
        return self._is_allowed(endpoint_id, 'pub_topic_patterns', name)

# ################################################################################################################################

    def is_allowed_pub_queue(self, endpoint_id, name):
        return self._is_allowed(endpoint_id, 'pub_queue_patterns', name)

# ################################################################################################################################

    def is_allowed_sub_queue(self, endpoint_id, name):
        return self._is_allowed(endpoint_id, 'sub_queue_patterns', name)

# ################################################################################################################################

    def is_allowed_sub_topic(self, endpoint_id, name):
        return self._is_allowed(endpoint_id, 'sub_topic_patterns', name)

# ################################################################################################################################
