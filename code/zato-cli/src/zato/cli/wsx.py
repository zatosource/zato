# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import DATA_FORMAT, GENERIC, WEB_SOCKET
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
    WSXOutconnType = GENERIC.CONNECTION.TYPE.OUTCONN_WSX

# ################################################################################################################################
# ################################################################################################################################

class CreateChannel(ServerAwareCommand):
    """ Creates a new WebSocket channel.
    """
    opts = [
        {'name':'--name', 'help':'Name of the channel to create', 'required':False,},
        {'name':'--address', 'help':'TCP address for the channel to use', 'required':False},
        {'name':'--is-active', 'help':'Should the channel be active upon creation', 'required':False},
        {'name':'--service', 'help':'Service reacting to requests sent to the channel', 'required':False,
            'default':Config.ServiceName},
        {'name':'--security', 'help':'Name of the security definition assigned to the channel', 'required':False},
        {'name':'--new-token-wait-time', 'help':'How many seconds to wait for new tokens from clients', 'required':False,
            'default':Config.NewTokenWaitTime},
        {'name':'--token-ttl', 'help':'For how many seconds a token is considered valid', 'required':False,
            'default':Config.TokenTTL},
        {'name':'--ping-interval', 'help':'Once in how many seconds to send and expect ping messages', 'required':False,
            'default':Config.PingInterval},
        {'name':'--ping-missed-threshold', 'help':'After how many missed ping messages to consider a WebSocket disconnected',
            'required':False, 'default':Config.PingMissedThreshold},
        {'name':'--extra-properties', 'help':'Extra properties as JSON', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

    def execute(self, args:'Namespace'):

        name = getattr(args, 'name', None)
        address = getattr(args, 'address', None)
        service_name = getattr(args, 'service', None)
        security = getattr(args, 'security', None)
        ping_interval = getattr(args, 'ping_interval', None) or Config.PingInterval
        ping_missed_threshold = getattr(args, 'ping_missed_threshold', None) or Config.PingMissedThreshold
        token_ttl = getattr(args, 'token_ttl', None) or Config.TokenTTL
        new_token_wait_time = getattr(args, 'new_token_wait_time', None) or Config.NewTokenWaitTime

        extra_properties = getattr(args, 'extra_properties', None)

        is_active = getattr(args, 'is_active', True)
        if is_active is None:
            is_active = True

        # Assign default values if required
        ping_interval = ping_interval or Config.PingInterval
        ping_missed_threshold = ping_missed_threshold or Config.PingMissedThreshold
        token_ttl = token_ttl or Config.TokenTTL
        new_token_wait_time = new_token_wait_time or Config.NewTokenWaitTime

        # Generate a name if one is not given
        name = name or 'auto.wsx.channel.' + fs_safe_now()

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
            'is_active': is_active,
            'is_internal': False,
            'data_format': DATA_FORMAT.JSON,
            'token_ttl': token_ttl,
            'new_token_wait_time': new_token_wait_time,
            'ping_interval': ping_interval,
            'ping_missed_threshold': ping_missed_threshold,
            'extra_properties': extra_properties
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class DeleteChannel(ServerAwareCommand):
    """ Deletes a WebSocket channel.
    """
    opts = [
        {'name':'--id', 'help':'ID of the channel to delete', 'required':False,},
        {'name':'--name', 'help':'Name of the channel to delete', 'required':False,},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

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
            'should_raise_if_missing': False
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class CreateOutconn(ServerAwareCommand):
    """ Creates a new outgoing WebSocket connection.
    """
    opts = [
        {'name':'--name', 'help':'Name of the connection to create', 'required':False,},
        {'name':'--address',   'help':'TCP address of a WebSocket server to connect to', 'required':False},
        {'name':'--sub-list',   'help':'A comma-separate list of topics the connection should subscribe to', 'required':False},
        {'name':'--on-connect-service',
            'help':'Service to invoke when the WebSocket connects to a remote server', 'required':False},
        {'name':'--on-message-service',
            'help':'Service to invoke when the WebSocket receives a message from the remote server', 'required':False},
        {'name':'--on-close-service',
            'help':'Service to invoke when the remote server closes its WebSocket connection', 'required':False},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

    def execute(self, args:'Namespace'):

        # This can be specified by users
        name = getattr(args, 'name', None)
        address = getattr(args, 'address', None)
        on_connect_service_name = getattr(args, 'on_connect_service', None)
        on_message_service_name = getattr(args, 'on_message_service', None)
        on_close_service_name = getattr(args, 'on_close_service', None)
        subscription_list = getattr(args, 'sub_list', '')

        # This is fixed
        is_zato = getattr(args, 'is_zato', True)
        is_active = getattr(args, 'is_active', True)
        has_auto_reconnect = getattr(args, 'has_auto_reconnect', True)

        # Generate a name if one is not given
        name = name or 'auto.wsx.outconn.' + fs_safe_now()

        # If we have no address to connect to, use the on employed for testing
        if not address:
            address = 'ws://127.0.0.1:47043/zato.wsx.apitests'

        # Convert the subscription list to the format that the service expects
        if subscription_list:
            subscription_list = subscription_list.split(',')
            subscription_list = [elem.strip() for elem in subscription_list]
            subscription_list = '\n'.join(subscription_list)

        # API service to invoke
        service = 'zato.generic.connection.create'

        # API request to send
        request = {
            'name': name,
            'address': address,
            'is_zato': is_zato,
            'is_active': is_active,
            'has_auto_reconnect': has_auto_reconnect,
            'on_connect_service_name': on_connect_service_name,
            'on_message_service_name': on_message_service_name,
            'on_close_service_name': on_close_service_name,
            'subscription_list': subscription_list,
            'pool_size': 1,
            'is_channel': False,
            'is_outconn': True,
            'is_internal': False,
            'sec_use_rbac': False,
            'type_': Config.WSXOutconnType,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class DeleteOutconn(ServerAwareCommand):
    """ Deletes a WebSocket outgoing connection.
    """
    opts = [
        {'name':'--id', 'help':'ID of the outgoing connection to delete', 'required':False,},
        {'name':'--name', 'help':'Name of the outgoing connection to delete', 'required':False,},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

    def execute(self, args:'Namespace'):

        id = getattr(args, 'id', None)
        name = getattr(args, 'name', None)

        # Make sure we have input data to delete the outgoing connection by
        if not (id or name):
            msg = 'Cannot continue. To delete a WebSocket outgoing connection, either --id or --name is required on input.'
            self.logger.warn(msg)
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # API service to invoke
        service = 'zato.generic.connection.delete'

        # API request to send
        request = {
            'id': id,
            'name': name,
            'should_raise_if_missing': False
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
    args.sub_list = 'zato.ping, zato.ping2'
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = CreateChannel(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
