# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Kombu
from kombu.connection import Connection as KombuConnection

# Zato
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.common import BrokerConfig

# ################################################################################################################################
# ################################################################################################################################

class BrokerConnection(KombuConnection):

    def ensure_connection(self, *args, **kwargs):
        kwargs['timeout'] = None
        _ = self._ensure_connection(*args, **kwargs)
        return self

# ################################################################################################################################
# ################################################################################################################################

class AMQP:

    def get_connection(self, broker_config:'BrokerConfig | None'=None, needs_ensure:'bool'=True) -> 'BrokerConnection':
        """ Returns a new AMQP connection object using broker configuration parameters.
        """
        # Get broker configuration
        broker_config = get_broker_config()

        # Split host and port from address
        host, port = broker_config.address.split(':')
        port = int(port)

        # Create and return a new connection
        conn = BrokerConnection(
            hostname=host,
            port=port,
            userid=broker_config.username,
            password=broker_config.password,
            virtual_host=broker_config.vhost,
            transport=broker_config.protocol,
        )

        # Make sure we are connected
        _ = conn.ensure_connection(timeout=1)

        return conn

# ################################################################################################################################
# ################################################################################################################################
