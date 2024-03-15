# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

# stdlib
from importlib import import_module
from logging import getLogger

# Cryptography
from cryptography.fernet import InvalidToken

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring

# Zato
from zato.common.api import KVDB as _KVDB
from zato.common.const import SECRETS
from zato.common.util import spawn_greenlet
from zato.common.util.kvdb import has_redis_sentinels

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class KVDB:
    """ A wrapper around the Zato's key-value database.
    """
    server: 'ParallelServer'

    def __init__(self, config=None, decrypt_func=None):

        self.conn = None
        self.config = config
        self.decrypt_func = decrypt_func
        self.conn_class = None # Introduced so it's easier to test the class
        self.has_sentinel = False

# ################################################################################################################################

    def _get_connection_class(self):
        """ Returns a concrete class to create Redis connections off basing on whether we use Redis sentinels or not.
        Abstracted out to a separate method so it's easier to test the whole class in separation.
        """
        if self.has_sentinel:
            from redis.sentinel import Sentinel
            return Sentinel
        else:
            from redis import StrictRedis
            return StrictRedis

# ################################################################################################################################

    def _parse_sentinels(self, item):
        if item:
            if isinstance(item, basestring):
                item = [item]
            out = []
            for elem in item:
                elem = elem.split(':')

                # This will always exist ..
                host = elem[0]

                # .. which is why we can always use it ..
                to_append = [host]

                # .. but port can be optional ..
                if len(elem) > 1:
                    port = elem[1]
                    port = int(port)
                    to_append.append(port)

                out.append(tuple(to_append))
            return out

# ################################################################################################################################

    def init(self):

        config = {}
        self.has_sentinel = has_redis_sentinels(self.config)

        if self.has_sentinel:
            sentinels = self._parse_sentinels(self.config.get('redis_sentinels'))

            if not sentinels:
                raise ValueError('kvdb.redis_sentinels must be provided')

            sentinel_master = self.config.get('redis_sentinels_master', None)
            if not sentinel_master:
                raise ValueError('kvdb.redis_sentinels_master must be provided')

            config['sentinels'] = sentinels
            config['sentinel_master'] = sentinel_master

        else:

            if self.config.get('host'):
                config['host'] = self.config.host

            if self.config.get('port'):
                config['port'] = int(self.config.port)

            if self.config.get('unix_socket_path'):
                config['unix_socket_path'] = self.config.unix_socket_path

            if self.config.get('db'):
                config['db'] = int(self.config.db)

        if self.config.get('password'):
            # Heuristics - gAAA is a prefix of encrypted secrets so there is a chance
            # we need to decrypt it. If the decryption fails, this is fine, we need
            # assume in such a case that it was an actual password starting with this prefix.
            if self.config.password.startswith(SECRETS.Encrypted_Indicator):
                try:
                    config['password'] = self.decrypt_func(self.config.password)
                except InvalidToken:
                    config['password'] = self.config.password
            else:
                config['password'] = self.config.password

        if self.config.get('socket_timeout'):
            config['socket_timeout'] = float(self.config.socket_timeout)

        if self.config.get('connection_pool'):

            split = self.config.connection_pool.split('.')
            module, class_name = split[:-1], split[-1]
            mod = import_module(module)
            config['connection_pool'] = getattr(mod, class_name)

        if self.config.get('charset'):
            config['charset'] = self.config.charset

        if self.config.get('errors'):
            config['errors'] = self.config.errors

        self.conn_class = self._get_connection_class()

        if self.has_sentinel:
            instance = self.conn_class(config['sentinels'], min_other_sentinels=0, password=config.get('password'),
                socket_timeout=config.get('socket_timeout'), decode_responses=True)
            self.conn = instance.master_for(config['sentinel_master'])
        else:
            self.conn = self.conn_class(charset='utf-8', decode_responses=True, **config)

        # Confirm whether we can connect
        self.ping()

# ################################################################################################################################

    def pubsub(self):
        return self.conn.pubsub()

# ################################################################################################################################

    def publish(self, *args, **kwargs):
        return self.conn.publish(*args, **kwargs)

# ################################################################################################################################

    def subscribe(self, *args, **kwargs):
        return self.conn.subscribe(*args, **kwargs)

# ################################################################################################################################

    def translate(self, system1:'str', key1:'str', value1:'str', system2:'str', key2:'str', default:'str'='') -> 'str':
        return self.conn.hget(
            _KVDB.SEPARATOR.join(
                (_KVDB.TRANSLATION, system1, key1, value1, system2, key2)), 'value2') or default

# ################################################################################################################################

    def reconfigure(self, config):
        # type: (dict) -> None
        self.config = config
        self.init()

# ################################################################################################################################

    def set_password(self, password):
        # type: (dict) -> None
        self.config['password'] = password
        self.init()

# ################################################################################################################################

    def copy(self):
        """ Returns an KVDB with the configuration copied over from self. Note that
        the object returned isn't initialized, in particular, the connection to the
        database won't have been initialized.
        """
        kvdb = KVDB()
        kvdb.config = self.config
        kvdb.decrypt_func = self.decrypt_func

        return kvdb

# ################################################################################################################################

    def close(self):
        self.conn.connection_pool.disconnect()

# ################################################################################################################################

    def ping(self):
        try:
            spawn_greenlet(self.conn.ping)
        except Exception as e:
            logger.warning('Could not ping %s due to `%s`', self.conn, e.args[0])
        else:
            logger.info('Redis ping OK -> %s', self.conn)

# ################################################################################################################################

    @staticmethod
    def is_config_enabled(config):
        """ Returns True if the configuration indicates that Redis is enabled.
        """
        # type: (dict) -> bool
        return config.get('host') and config.get('port')

# ################################################################################################################################
# ################################################################################################################################
