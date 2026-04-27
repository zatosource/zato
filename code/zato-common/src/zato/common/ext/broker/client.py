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
