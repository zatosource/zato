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

# Zato
from zato.common import ZatoException
from zato.server.service.internal import AdminService

COMMANDS_AVAILABLE = (
    'CONFIG GET', 'CONFIG SET', 'CONFIG RESETSTAT', 'DBSIZE', 'DEBUG OBJECT', 'DECR', 
    'DECRBY', 'DEL', 'DUMP', 'ECHO', 'EXISTS', 'EXPIRE', 'EXPIREAT', 'FLUSHDB', 'GET', 'HDEL', 
    'HEXISTS', 'HGET', 'HGETALL', 'HINCRBY', 'HKEYS', 'HLEN', 'HSETNX', 'HVALS', 'INCR', 
    'INCRBY', 'INFO', 'KEYS', 'LLEN', 'LPOP', 'LPUSH', 'LPUSHX', 'LRANGE', 'LREM', 'LSET', 'LTRIM', 
    'MGET', 'MSET', 'MSETNX', 'OBJECT', 'PERSIST', 'PEXPIRE', 'PEXPIREAT', 'PING', 'PSETEX', 
    'PTTL', 'RANDOMKEY', 'RENAME', 'RENAMENX', 'RESTORE', 'RPOP', 'SADD', 'SET', 'SMEMBERS', 
    'SREM', 'TIME', 'TTL', 'TYPE', 'ZADD', 'ZRANGE', 'ZREM')

class ExecuteCommand(AdminService):
    """ Executes a command against the key/value DB.
    """
    class SimpleIO:
        input_required = ('command',)
        output_required = ('result',)
        
    def handle(self):
        command = self.request.input.command or ''
        
        if not command:
            msg = 'No command sent'
            raise ZatoException(self.cid, msg)
        
        # Can we handle it at all? This won't catch everything but it's OK for
        # filtering out most of the noise.
        if not any(command.startswith(elem) for elem in COMMANDS_AVAILABLE):
            msg = 'Invalid command:[{}], not one of [{}]'.format(command, COMMANDS_AVAILABLE)
            raise ZatoException(self.cid, msg)
                   
        self.response.payload.result = 'aaa'
        print(333, self.server.kvdb.conn)

'''
class GetList(AdminService):
    """ Returns a list of keys, optionally including their values.
    """
    # KEYS, then
    # HGETALL
    # GET
    # LRANGE
    # SMEMBERS
'''