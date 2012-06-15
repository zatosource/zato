# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from string import punctuation

# PyParsing
from pyparsing import alphanums, oneOf, OneOrMore, Optional, White, Word

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

if __name__ == '__main__':
    sample = 'LLEN list-10'
    result = redis_grammar.parseString(sample)
    print(result.command)
    print(result.parameters)
