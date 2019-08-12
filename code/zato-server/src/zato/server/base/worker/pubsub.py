# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class PubSub(WorkerImpl):
    """ Publish/subscribe-related functionality for worker objects.
    """

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_CREATE(self, msg):
        self.pubsub.create_topic_object(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(self, msg):
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.pubsub.edit_topic(del_name, msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(self, msg):
        self.pubsub.delete_topic(msg.id)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_CREATE(self, msg):
        self.pubsub.create_endpoint(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_EDIT(self, msg):
        self.pubsub.edit_endpoint(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_DELETE(self, msg):
        self.pubsub.delete_endpoint(msg.id)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(self, msg):
        self.pubsub.create_subscription_object(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(self, msg):
        msg.pop('action') # Not needed by pub/sub
        self.pubsub.edit_subscription(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(self, msg):
        self.pubsub.unsubscribe(msg.topic_sub_keys)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUB_KEY_SERVER_SET(self, msg):
        self.pubsub.set_sub_key_server(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_WSX_CLIENT_SUB_KEY_SERVER_REMOVE(self, msg):
        self.pubsub.remove_ws_sub_key_server(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_DELIVERY_SERVER_CHANGE(self, msg):
        if msg.old_delivery_server_id == self.server.id:
            old_server_pid = self.pubsub.get_delivery_server_by_sub_key(msg.sub_key).server_pid
            if old_server_pid == self.server.pid:
                self.pubsub.migrate_delivery_server(msg)

# ################################################################################################################################
