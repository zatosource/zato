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
from traceback import format_exc

# Zato
from zato.common import ZatoException
from zato.common.kvdb import redis_grammar
from zato.server.service.internal import AdminService, AdminSIO

class ExecuteCommand(AdminService):
    """ Executes a command against the key/value DB.
    """
    name = 'zato.kvdb.remote-command.execute'
    
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_remote_command_execute_request'
        response_elem = 'zato_kvdb_remote_command_execute_response'
        input_required = ('command',)
        output_required = ('result',)
        
    def handle(self):
        input_command = self.request.input.command or ''
        
        if not input_command:
            msg = 'No command sent'
            raise ZatoException(self.cid, msg)

        try:
            parse_result = redis_grammar.parseString(input_command)
            
            options = {}
            command = parse_result.command
            parameters = parse_result.parameters if parse_result.parameters else []
            
            if command == 'CONFIG':
                options['parse'] = parameters[0]
            elif command == 'OBJECT':
                options['infotype'] = parameters[0]
                
            response = self.server.kvdb.conn.execute_command(command, *parameters, **options) or ''
            
            if response and command in('KEYS', 'HKEYS', 'HVALS'):
                response = unicode(response).encode('utf-8')
            elif command in('HLEN', 'LLEN', 'LRANGE', 'SMEMBERS', 'HGETALL'):
                response = str(response)
                
            self.response.payload.result = response or '(None)'
            
        except Exception, e:
            msg = 'Command parsing error, command:[{}], e:[{}]'.format(input_command, format_exc(e))
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)


# The data browser will most likely be implemented in a future version
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
