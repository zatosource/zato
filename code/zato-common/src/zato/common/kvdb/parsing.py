# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

# stdlib
from logging import getLogger
from string import punctuation

# PyParsing
from pyparsing import alphanums, oneOf, OneOrMore, Optional, White, Word

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Redis PyParsing grammar

quot = Optional(oneOf(('"', "'")))
command = oneOf((
    'CONFIG', 'DBSIZE', 'DECR', 'DECRBY', 'DEL', 'DUMP', 'ECHO',
    'EXISTS', 'EXPIRE', 'EXPIREAT', 'FLUSHDB', 'GET',
    'HDEL', 'HEXISTS', 'HGET', 'HGETALL', 'HINCRBY', 'HKEYS', 'HLEN', 'HSET', 'HSETNX',
    'HVALS', 'INCR', 'INCRBY', 'INFO', 'KEYS', 'LLEN', 'LPOP', 'LPUSH', 'LPUSHX',
    'LRANGE', 'LREM', 'LSET', 'LTRIM', 'MGET', 'MSET', 'MSETNX', 'OBJECT', 'PERSIST',
    'PEXPIRE', 'PEXPIREAT', 'PING', 'PSETEX', 'PTTL', 'RANDOMKEY', 'RENAME', 'RENAMENX',
    'RESTORE', 'RPOP', 'SADD', 'SET', 'SISMEMBER', 'SMEMBERS', 'SREM', 'TIME', 'TTL', 'TYPE',
    'ZADD', 'ZRANGE', 'ZREM'), caseless=True).setResultsName('command')
parameters = (OneOrMore(Word(alphanums + '-' + punctuation))).setResultsName('parameters')
redis_grammar = command + Optional(White().suppress() + parameters)

# ################################################################################################################################
# ################################################################################################################################
