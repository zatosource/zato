# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# PyKafka
try:
    from pykafka import KafkaClient, SslConfig # type: ignore
except ImportError:
    has_kafka = False
else:
    has_kafka = True

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pykafka.broker import Broker # type: ignore
    Broker = Broker

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class DefKafkaWrapper(Wrapper):
    """ Wraps a Kafka connection client.
    """
    _impl: 'KafkaClient'
    wrapper_type = 'Kafka definition'

# ################################################################################################################################

    def _init_client(self) -> 'None':

        with self.update_lock:

            if self.is_connected:
                return

            # TLS is optional
            if self.config.is_tls_enabled:
                tls_config = SslConfig(**{
                    'certfile': self.config.tls_cert_file,
                    'keyfile': self.config.tls_private_key_file,
                    'password': self.config.tls_pem_passphrase,
                    'cafile': self.config.tls_ca_certs_file,
                })
            else:
                tls_config = None

            # Our server list needs to be reformatted in accordance with what KafkaClient expects
            # and it may be turned into a Kafka or ZooKeeper server list.

            server_list = self.config.server_list.splitlines()
            server_list = ','.join(server_list)

            if self.config.should_use_zookeeper:
                hosts = None
                zookeeper_hosts = server_list
            else:
                hosts = server_list
                zookeeper_hosts = None

            client_config = {
                'hosts': hosts,
                'zookeeper_hosts': zookeeper_hosts,
                'socket_timeout_ms': self.config.socket_timeout * 1000,
                'offsets_channel_socket_timeout_ms': self.config.offset_timeout * 1000,
                'use_greenlets': True,
                'exclude_internal_topics': self.config.should_exclude_internal_topics,
                'source_address': self.config.source_address or '',
                'ssl_config': tls_config,
                'broker_version': self.config.broker_version,
            }

            # Create the actual connection object
            self._impl = KafkaClient(**client_config)

            # Confirm the connection was established
            self.ping()

            # We can assume we are connected now
            self.is_connected = True

# ################################################################################################################################

    def get(self) -> 'KafkaClient':
        return self._impl

# ################################################################################################################################

    def _init_impl(self) -> 'None':
        if not has_kafka:
            return
        try:
            self._init_client()
        except Exception:
            logger.warning('Could not build `%s` client to `%s`; e:`%s`', self.wrapper_type, self.config.name, format_exc())
            raise

# ################################################################################################################################

    def _delete(self) -> 'None':
        for elem in self._impl.brokers.values():
            elem = cast_('Broker', elem)
            try:
                elem._connection.disconnect()
            except Exception:
                logger.warning('Could not disconnect `%s` from `%r`, e:`%s`', elem, self.config, format_exc())

# ################################################################################################################################

    def _ping(self) -> 'None':
        self._impl.cluster.fetch_api_versions()

# ################################################################################################################################
# ################################################################################################################################
