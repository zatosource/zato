# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import DEBUG, getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# Redis
from redis.sentinel import MasterNotFoundError

# Zato
from zato.common import ZatoException
from zato.common.kvdb import redis_grammar
from zato.common.util import has_redis_sentinels
from zato.server.service.internal import AdminService, AdminSIO

kvdb_logger = getLogger('zato_kvdb')

class ExecuteCommand(AdminService):
    """ Executes a command against the key/value DB.
    """
    name = 'zato.kvdb.remote-command.execute'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_remote_command_execute_request'
        response_elem = 'zato_kvdb_remote_command_execute_response'
        input_required = ('command',)
        output_required = ('result',)

    def _fixup_parameters(self, parameters):
        """ Fix up quotes so stuff like [SISMEMBER key member] and [SISMEMBER key "member"] is treated the same
        (brackets used here for clarity only to separate commands).
        """
        if parameters:
            has_one = len(parameters) == 1
            first_elem_idx = 0 if has_one else 1

            if parameters[first_elem_idx][0] == '"' and parameters[-1][-1] == '"':
                parameters[first_elem_idx] = parameters[first_elem_idx][1:]
                parameters[-1] = parameters[-1][:-1]

        return parameters

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

            parameters = self._fixup_parameters(parameters)

            if command == 'CONFIG':
                options['parse'] = parameters[0]
            elif command == 'OBJECT':
                options['infotype'] = parameters[0]

            response = self.server.kvdb.conn.execute_command(command, *parameters, **options) or ''

            if response and command in('KEYS', 'HKEYS', 'HVALS'):
                response = unicode(response).encode('utf-8')

            elif command in('HLEN', 'LLEN', 'LRANGE', 'SMEMBERS', 'HGETALL'):
                response = str(response)

            elif command == 'DUMP':
                response = repr(response)

            self.response.payload.result = response or '(None)'

        except Exception, e:
            msg = 'Command parsing error, command:[{}], e:[{}]'.format(input_command, format_exc(e))
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)

class LogConnectionInfo(AdminService):
    """ Writes outs to logs information regarding current connections to KVDB.
    """
    def handle(self):
        config = self.server.fs_server_config.kvdb
        sleep_time = float(config.log_connection_info_sleep_time)
        has_sentinels = has_redis_sentinels(config)

        if kvdb_logger.isEnabledFor(DEBUG):
            while True:
                if has_sentinels:
                    try:
                        master_address = self.kvdb.conn.connection_pool.connection_kwargs['connection_pool'].get_master_address()
                        kvdb_logger.debug(
                            'Uses sentinels: `%s %r`, master: `%r`', has_sentinels, config.redis_sentinels, master_address)
                    except MasterNotFoundError, e:
                        self.logger.warn(format_exc(e))
                        kvdb_logger.warn(format_exc(e))
                else:
                    kvdb_logger.debug(
                        'Uses sentinels: `%s`, conn:`%r`', has_sentinels, self.kvdb.conn)
                sleep(sleep_time)

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
