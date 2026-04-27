# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato_broker_core import Broker as _BrokerImpl

class PubSubBroker:

    def __init__(self, config):
        from gevent import get_hub
        self._hub = get_hub()
        self._broker = _BrokerImpl(config)

    def reconfigure_partman(self, config):
        self._hub.threadpool.apply(self._broker.reconfigure_partman, (config,))

    def stop(self):
        self._hub.threadpool.apply(self._broker.stop)

    def publish(self, config):
        return self._hub.threadpool.apply(self._broker.publish, (config,))

    def get_messages(self, topic_id, sub_id, batch_size, window_minutes):
        return self._hub.threadpool.apply(self._broker.get_messages, (topic_id, sub_id, batch_size, window_minutes))

    def ack(self, sub_id, pub_msg_ids, cursor, window_minutes):
        return self._hub.threadpool.apply(self._broker.ack, (sub_id, pub_msg_ids, cursor, window_minutes))

    def create_topic(self, name):
        return self._hub.threadpool.apply(self._broker.create_topic, (name,))

    def get_topic_by_name(self, name):
        return self._hub.threadpool.apply(self._broker.get_topic_by_name, (name,))

    def delete_topic(self, name):
        return self._hub.threadpool.apply(self._broker.delete_topic, (name,))

    def create_subscription(self, sub_key, topic_id, ack_mode):
        return self._hub.threadpool.apply(self._broker.create_subscription, (sub_key, topic_id, ack_mode))

    def get_subscription_id(self, sub_key, topic_id):
        return self._hub.threadpool.apply(self._broker.get_subscription_id, (sub_key, topic_id))

    def delete_subscription(self, sub_key, topic_id):
        return self._hub.threadpool.apply(self._broker.delete_subscription, (sub_key, topic_id))

    def get_cursor(self, sub_id):
        return self._hub.threadpool.apply(self._broker.get_cursor, (sub_id,))

    def list_active_subscriptions(self):
        return self._hub.threadpool.apply(self._broker.list_active_subscriptions)
