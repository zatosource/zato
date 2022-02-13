# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import DATA_FORMAT, WEB_SOCKET
from zato.common.test import get_free_tcp_port
from zato.common.util.api import fs_safe_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

class Config:
    ServiceName = 'helpers.web-sockets-gateway'
    NewTokenWaitTime = WEB_SOCKET.DEFAULT.NEW_TOKEN_TIMEOUT
    TokenTTL = WEB_SOCKET.DEFAULT.TOKEN_TTL
    PingInterval = WEB_SOCKET.DEFAULT.PING_INTERVAL
    PingMissedThreshold = WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD

# ################################################################################################################################
# ################################################################################################################################

class CreateChannel(ServerAwareCommand):
    """ Creates a new WebSocket channel.
    """
    opts = [
        {'name':'--name', 'help':'Name of the channel to create', 'required':False,},
        {'name':'--address',   'help':'TCP address for the channel to use', 'required':False},
        {'name':'--service', 'help':'Service reacting to requests sent to the channel', 'required':False,
            'default':Config.ServiceName},
        {'name':'--security', 'help':'Service reacting to requests sent to the channel', 'required':False},
        {'name':'--new-token-wait-time', 'help':'How many seconds to wait for new tokens from clients', 'required':False,
            'default':Config.NewTokenWaitTime},
        {'name':'--token-ttl', 'help':'For how many seconds a token is considered valid', 'required':False,
            'default':Config.TokenTTL},
        {'name':'--ping-interval', 'help':'Once in how many seconds to send and expect ping messages', 'required':False,
            'default':Config.PingInterval},
        {'name':'--ping-missed-threshold', 'help':'After how many missed ping messages to consider a WebSocket disconnected',
            'required':False, 'default':Config.PingMissedThreshold},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        name = getattr(args, 'name', None)
        address = getattr(args, 'address', None)
        service_name = getattr(args, 'service', None)
        security = getattr(args, 'security', None)
        ping_interval = getattr(args, 'ping_interval', None) or Config.PingInterval
        ping_missed_threshold = getattr(args, 'ping_missed_threshold', None) or Config.PingMissedThreshold
        token_ttl = getattr(args, 'token_ttl', None) or Config.TokenTTL
        new_token_wait_time = getattr(args, 'new_token_wait_time', None) or Config.NewTokenWaitTime

        # Assign default values if required
        ping_interval = ping_interval or Config.PingInterval
        ping_missed_threshold = ping_missed_threshold or Config.PingMissedThreshold
        token_ttl = token_ttl or Config.TokenTTL
        new_token_wait_time = new_token_wait_time or Config.NewTokenWaitTime

        # Generate a name if one is not given
        name = name or 'auto.wsx.' + fs_safe_now()

        # If we have no address to listen on, generate one here
        if not address:
            tcp_port = get_free_tcp_port()
            address = f'ws://127.0.0.1:{tcp_port}/{name}'

        # API service to invoke
        service = 'zato.channel.web-socket.create'

        # API request to send
        request = {
            'name': name,
            'address': address,
            'service_name': service_name,
            'security': security,
            'is_active': True,
            'is_internal': False,
            'data_format': DATA_FORMAT.JSON,
            'token_ttl': token_ttl,
            'new_token_wait_time': new_token_wait_time,
            'ping_interval': ping_interval,
            'ping_missed_threshold': ping_missed_threshold,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class DeleteChannel(ServerAwareCommand):
    """ Deletes a WebSocket channel.
    """
    opts = [
        {'name':'--id', 'help':'ID of the channel to create', 'required':False,},
        {'name':'--name', 'help':'Name of the channel to create', 'required':False,},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        id = getattr(args, 'id', None)
        name = getattr(args, 'name', None)

        # Make sure we have input data to delete the channel by
        if not (id or name):
            self.logger.warn('Cannot continue. To delete a WebSocket channel, either --id or --name is required on input.')
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # API service to invoke
        service = 'zato.channel.web-socket.delete'

        # API request to send
        request = {
            'id': id,
            'name': name,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace
    from os import environ

    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.service = Config.ServiceName
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = CreateChannel(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
