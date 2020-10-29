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
from zato.common.util.api import spawn_greenlet
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

class ConnectionWrapper(object):
    def __init__(self, client):
        # type: (LDAPClient) -> None
        self.client = client
        self.conn = None # type: Connection

    def __enter__(self):
        try:
            self.conn = self.client.connect()
        except Exception:
            logger.warn('Could not obtain a connection to `%s` (%s)', self.client.config.server_list, self.client.config.name)
            raise
        else:
            return self.conn

    def __exit__(self, type, value, traceback):
        if self.conn:
            self.conn.unbind()

# ################################################################################################################################
# ################################################################################################################################

class LDAPClient(object):
    """ A client through which outgoing LDAP messages can be sent.
    """
    def __init__(self, config):
        # type: (Bunch) -> None

        self.config = config

        # By default, we are not connected anywhere
        self.is_connected = False

        # Initialize in a separate greenlet so as not to block the main one
        # if the remote server is slow to respond.
        spawn_greenlet(self._init, timeout=2)

# ################################################################################################################################

    def _init(self):
        # Try to ping the remote end
        self.ping()

        # If we are here it means that ping succeeded so we can assume the connection's configuration is good
        self.is_connected = True

# ################################################################################################################################

    def get_conn_config(self):

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
            'pool_size': 1,
            'pool_lifetime': self.config.pool_lifetime,
            'return_empty_attributes': self.config.should_return_empty_attrs,
            'pool_keepalive': self.config.pool_keep_alive,
            'raise_exceptions': True,
        }

        if self.config.sasl_mechanism:
            conn_config['sasl_mechanism'] = self.config.sasl_mechanism
            conn_config['sasl_credentials'] = self.config.sasl_credentials

        return conn_config

    def connect(self, conn_config=None):

        # Obtain connection configuration ..
        conn_config = conn_config or self.get_conn_config()

        # .. create the connection objet
        conn = Connection(**conn_config)

        # .. bind only if we are to be active.
        if self.config.is_active:
            conn.bind()

        # Finally, return the connection object
        return conn

# ################################################################################################################################

    def zato_delete_impl(self):
        pass # Not implemented by LDAP connections

# ################################################################################################################################

    def get(self):
        return ConnectionWrapper(self)

# ################################################################################################################################

    def check_credentials(self, user_data, secret, raise_on_error=True):

        # Build a new connection definition dictionary with input credentials ..
        conn_config = self.get_conn_config()
        conn_config['user'] = user_data
        conn_config['password'] = secret

        # .. and try to connect to the remote end.
        conn = None
        try:
            conn = self.connect(conn_config)
            conn.abandon(0)
        except Exception:
            if raise_on_error:
                raise
            else:
                return False
        else:
            return True
        finally:
            if conn:
                conn.unbind()

# ################################################################################################################################

    def ping(self):
        logger.info('Pinging LDAP `%s`', self.config.server_list)
        with self.get() as conn:
            conn.abandon(0)

# ################################################################################################################################
# ################################################################################################################################

class OutconnLDAPWrapper(Wrapper):
    """ Wraps a queue of connections to LDAP.
    """
    def __init__(self, config, server):
        config.parent = self
        config.auth_url = config.server_list
        super(OutconnLDAPWrapper, self).__init__(config, 'outgoing LDAP', server)

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
