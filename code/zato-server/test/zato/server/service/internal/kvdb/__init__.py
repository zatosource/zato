# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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
                
            self.response.payload.result = response
            
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
