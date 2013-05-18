# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from importlib import import_module
from string import punctuation

# PyParsing
from pyparsing import alphanums, oneOf, OneOrMore, Optional, White, Word

# redis
from redis import StrictRedis

# Zato
from zato.common import KVDB as _KVDB

# Redis PyParsing grammar

quot = Optional(oneOf(('"', "'")))
command = oneOf(('CONFIG', 'DBSIZE', 'DECR', 'DECRBY', 'DEL', 'DUMP', 'ECHO', 
    'EXISTS', 'EXPIRE', 'EXPIREAT', 'FLUSHDB', 'GET', 
    'HDEL', 'HEXISTS', 'HGET', 'HGETALL', 'HINCRBY', 'HKEYS', 'HLEN', 'HSETNX', 
    'HVALS', 'INCR', 'INCRBY', 'INFO', 'KEYS', 'LLEN', 'LPOP', 'LPUSH', 'LPUSHX', 
    'LRANGE', 'LREM', 'LSET', 'LTRIM', 'MGET', 'MSET', 'MSETNX', 'OBJECT', 'PERSIST',
    'PEXPIRE', 'PEXPIREAT', 'PING', 'PSETEX', 'PTTL', 'RANDOMKEY', 'RENAME', 'RENAMENX', 
    'RESTORE', 'RPOP', 'SADD', 'SET', 'SMEMBERS', 'SREM', 'TIME', 'TTL', 'TYPE', 
    'ZADD', 'ZRANGE', 'ZREM'), caseless=True).setResultsName('command')
parameters = (OneOrMore(quot + Word(alphanums + '-' + punctuation) + quot)).setResultsName('parameters')
redis_grammar = quot + command + Optional(White().suppress() + parameters)

class KVDB(object):
    """ A wrapper around the Zato's key-value database.
    """
    def __init__(self, conn=None, config=None, decrypt_func=None):
        self.conn = conn
        self.config = config
        self.decrypt_func = decrypt_func
        
    def init(self):
        config = {}
        
        if self.config.get('host'):
            config['host'] = self.config.host
        
        if self.config.get('port'):
            config['port'] = int(self.config.port)
            
        if self.config.get('db'):
            config['db'] = int(self.config.db)
            
        if self.config.get('password'):
            config['password'] = self.decrypt_func(self.config.password)
            
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
            
        if self.config.get('unix_socket_path'):
            config['unix_socket_path'] = self.config.unix_socket_path
            
        self.conn = StrictRedis(**config)
        
    def pubsub(self):
        return self.conn.pubsub()
    
    def publish(self, *args, **kwargs):
        return self.conn.publish(*args, **kwargs)
    
    def subscribe(self, *args, **kwargs):
        return self.conn.subscribe(*args, **kwargs)

    def translate(self, system1, key1, value1, system2, key2, default=''):
        return self.conn.hget(_KVDB.SEPARATOR.join((_KVDB.TRANSLATION, system1, key1, value1, system2, key2)), 'value2') or default
    
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