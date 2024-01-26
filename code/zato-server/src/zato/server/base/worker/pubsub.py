# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.pubsub import MSG_PREFIX as PUBSUB_MSG_PREFIX
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore
    from zato.server.pubsub import PubSub as ServerPubSub
    ServerPubSub = ServerPubSub

# ################################################################################################################################
# ################################################################################################################################

class PubSub(WorkerImpl):
    """ Publish/subscribe-related functionality for worker objects.
    """
    pubsub: 'ServerPubSub'

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.create_topic_object(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.pubsub.edit_topic(del_name, msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.delete_topic(msg.id)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.create_endpoint(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.edit_endpoint(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_ENDPOINT_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.delete_endpoint(msg.id)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.create_subscription_object(msg)
        if msg.sub_key.startswith(PUBSUB_MSG_PREFIX.SERVICE_SK):
            self.pubsub.set_config_for_service_subscription(msg.sub_key)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        msg.pop('action') # Not needed by pub/sub
        self.pubsub.edit_subscription(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.unsubscribe(msg.topic_sub_keys)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUB_KEY_SERVER_SET(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.set_sub_key_server(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_QUEUE_CLEAR(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.clear_task(msg.sub_key)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_WSX_CLIENT_SUB_KEY_SERVER_REMOVE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.pubsub.remove_ws_sub_key_server(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_DELIVERY_SERVER_CHANGE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if msg.old_delivery_server_id == self.server.id:
            old_server = self.pubsub.get_delivery_server_by_sub_key(msg.sub_key)
            if old_server:
                if old_server.server_pid == self.server.pid:
                    self.pubsub.migrate_delivery_server(msg)

# ################################################################################################################################
