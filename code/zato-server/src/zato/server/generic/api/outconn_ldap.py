# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import ssl
from codecs import encode
from logging import getLogger
from traceback import format_exc

# ldap3
from ldap3 import Connection, Server, ServerPool, SYNC, Tls

# Zato
from zato.common.util import spawn_greenlet
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

# Type hints
import typing

if typing.TYPE_CHECKING:
    from bunch import Bunch

    # For pyflakes
    Bunch = Bunch

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class LDAPClient(object):
    """ A client through which outgoing LDAP messages can be sent.
    """
    def __init__(self, config):
        # type: (Bunch) -> None

        self.config = config
        self.is_connected = False
        self.impl = None # type: Connection
        spawn_greenlet(self._init, timeout=2)

# ################################################################################################################################

    def _init(self):

        # All servers in our pool, even if there is only one
        servers = []

        # TLS is optional
        if self.config.is_tls_enabled:

            tls_validate = getattr(ssl, self.config.tls_validate)
            tls_version = getattr(ssl, 'PROTOCOL_{}'.format(self.config.tls_version))

            tls_config = {
                'local_private_key_file': self.config.tls_private_key_file or None,
                'local_certificate_file': self.config.tls_cert_file or None,
                'validate': tls_validate or None,
                'version': tls_version,
                'ca_certs_file': self.config.tls_ca_certs_file or None,
                'ciphers': self.config.tls_ciphers,
            }

            logger.warn('QQQ %s', tls_config)

            tls = Tls(**tls_config)
        else:
            tls = None

        for server_info in self.config.server_list: # type: str

            # Configuration for each server
            server_config = {
                'host': server_info,
                'use_ssl': self.config.is_tls_enabled,
                'get_info': self.config.get_info,
                'connect_timeout': self.config.connect_timeout,
                'mode': self.config.ip_mode,
                'tls': tls
            }

            # Create a server object and append it to the list given to the pool later on
            servers.append(Server(**server_config))

        # Configuration for the server pool
        pool_config = {
            'servers': servers,
            'pool_strategy': self.config.pool_ha_strategy,
            'active': self.config.pool_max_cycles,
            'exhaust': self.config.pool_exhaust_timeout
        }

        # Create our server pool
        pool = ServerPool(**pool_config)

        # Connection configuration
        conn_config = {
            'server': pool,
            'user': self.config.username,
            'password': self.config.secret,
            'auto_bind': self.config.auto_bind,
            'auto_range': self.config.use_auto_range,
            'client_strategy': SYNC,
            'check_names': self.config.should_check_names,
            'collect_usage': self.config.is_stats_enabled,
            'read_only': self.config.is_read_only,
            'pool_name': self.config.pool_name or encode(self.config.name),
            'pool_size': self.config.pool_size,
            'pool_lifetime': self.config.pool_lifetime,
            'return_empty_attributes': self.config.should_return_empty_attrs,
            'pool_keepalive': self.config.pool_keep_alive,
        }

        if self.config.sasl_mechanism:
            conn_config['sasl_mechanism'] = self.config.sasl_mechanism
            conn_config['sasl_credentials'] = self.config.sasl_credentials

        # Finally, create the connection objet
        self.impl = Connection(**conn_config)

        # If we are active, bind and run a ping query immediately to check if any server is actually available
        if self.config.is_active:
            self.impl.bind()
            self.ping()

# ################################################################################################################################

    def zato_delete_impl(self):
        self.impl.unbind()

# ################################################################################################################################

    def ping(self):
        logger.info('Pinging LDAP `%s`', self.config.server_list)
        self.impl.abandon(0)

# ################################################################################################################################

# Public API

    def add(self, *args, **kwargs):
        return self.impl.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.impl.delete(*args, **kwargs)

    def modify(self, *args, **kwargs):
        return self.impl.modify(*args, **kwargs)

    def modify_dn(self, *args, **kwargs):
        return self.impl.modify_dn(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.impl.search(*args, **kwargs)

    def compare(self, *args, **kwargs):
        return self.impl.compare(*args, **kwargs)

    def abandon(self, *args, **kwargs):
        return self.impl.abandon(*args, **kwargs)

    def extended(self, *args, **kwargs):
        return self.impl.extended(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class OutconnLDAPWrapper(Wrapper):
    """ Wraps a queue of connections to LDAP.
    """
    def __init__(self, config, server):
        config.parent = self
        super(OutconnLDAPWrapper, self).__init__(config, 'outgoing LDAP', server)

# ################################################################################################################################

    def change_password(self, msg):
        logger.warn('QQQ %s', msg)

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client.ping()

# ################################################################################################################################

    def add_client(self):
        try:
            conn = LDAPClient(self.config)
        except Exception:
            logger.warn('LDAP client could not be built `%s`', format_exc())
        else:
            self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
