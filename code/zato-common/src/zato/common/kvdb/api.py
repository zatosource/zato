# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

# stdlib
from calendar import timegm
from importlib import import_module
from logging import getLogger
from time import gmtime

# Cryptography
from cryptography.fernet import InvalidToken

# Python 2/3 compatibility
from past.builtins import basestring

# Zato
from zato.common.api import KVDB as _KVDB, NONCE_STORE
from zato.common.util.kvdb import has_redis_sentinels

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class LuaContainer(object):
    """ A class which knows how to add and execute Lua scripts against Redis.
    """
    def __init__(self, kvdb=None, initial_programs=None):
        self.kvdb = kvdb
        self.lua_programs = {}
        self.add_initial_lua_programs(initial_programs or {})

    def add_initial_lua_programs(self, programs):
        for name, program in programs:
            self.add_lua_program(name, program)

    def add_lua_program(self, name, program):
        self.lua_programs[name] = self.kvdb.register_script(program)

    def run_lua(self, name, keys=None, args=None):
        logger.debug('run_lua: name/keys/args:`%s %s %s`, lua_programs:`%s', name, keys, args, self.lua_programs)
        return self.lua_programs[name](keys or [], args or [])

# ################################################################################################################################

class KVDB(object):
    """ A wrapper around the Zato's key-value database.
    """
    def __init__(self, conn=None, config=None, decrypt_func=None):
        self.conn = conn
        self.config = config
        self.decrypt_func = decrypt_func
        self.conn_class = None # Introduced so it's easier to test the class
        self.lua_container = LuaContainer()
        self.run_lua = self.lua_container.run_lua # So it's more natural to use it
        self.has_sentinel = False

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

    def _parse_sentinels(self, item):
        if item:
            if isinstance(item, basestring):
                item = [item]
            out = []
            for elem in item:
                elem = elem.split(':')
                out.append((elem[0], int(elem[1])))
            return out

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
            # Heuristics - gA is a prefix of encrypted secrets so there is a chance
            # we need to decrypt it. If the decryption fails, this is fine, we need
            # assume in such a case that it was an actual password starting with this prefix.
            if self.config.password.startswith('gA'):
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

        self.lua_container.kvdb = self.conn

    def pubsub(self):
        return self.conn.pubsub()

    def publish(self, *args, **kwargs):
        return self.conn.publish(*args, **kwargs)

    def subscribe(self, *args, **kwargs):
        return self.conn.subscribe(*args, **kwargs)

    def translate(self, system1, key1, value1, system2, key2, default=''):
        return self.conn.hget(
            _KVDB.SEPARATOR.join(
                (_KVDB.TRANSLATION, system1, key1, value1, system2, key2)), 'value2') or default

    def copy(self):
        """ Returns an KVDB with the configuration copied over from self. Note that
        the object returned isn't initialized, in particular, the connection to the
        database won't have been initialized.
        """
        kvdb = KVDB()
        kvdb.config = self.config
        kvdb.decrypt_func = self.decrypt_func

        return kvdb

    def close(self):
        self.conn.connection_pool.disconnect()

# ################################################################################################################################

    # OAuth

    def add_oauth_nonce(self, username, nonce, max_nonce_log):
        """ Adds an OAuth to the set containing last N used ones for a given username.
        """
        key = NONCE_STORE.KEY_PATTERN.format('oauth', username)

        # This lets us trim the set to top (last) N nonces
        score = timegm(gmtime())

        self.conn.zadd(key, score, nonce)
        self.conn.zremrangebyrank(key, 0, -max_nonce_log)

    def has_oauth_nonce(self, username, nonce):
        """ Returns a boolean flag indicating if there's an OAuth nonce for a given
        username stored in KVDB.
        """
        return self.conn.zscore(NONCE_STORE.KEY_PATTERN.format('oauth', username), nonce)

# ################################################################################################################################
