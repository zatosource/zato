# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import CONNECTION
from zato.common.util.api import fs_safe_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

class Config:
    ServiceName = 'pub.zato.ping'
    MaxBytesRequests = 500   # 0.5k because requests are usually shorter
    MaxBytesResponses = 5000 # 5k because responses are usually longer

# ################################################################################################################################
# ################################################################################################################################

class SecurityAwareCommand(ServerAwareCommand):

    def _get_security_id(self, *, basic_auth:'str', api_key:'str') -> 'str':
        pass

# ################################################################################################################################
# ################################################################################################################################

class CreateChannel(SecurityAwareCommand):
    """ Creates a new REST channel.
    """
    opts = [
        {'name':'--name', 'help':'Name of the channel to create', 'required':False,},
        {'name':'--is-active', 'help':'Should the channel be active upon creation', 'required':False},
        {'name':'--url-path', 'help':'URL path to assign to the channel', 'required':False},
        {'name':'--service', 'help':'Service reacting to requests sent to the channel',
            'required':False, 'default':Config.ServiceName},
        {'name':'--basic-auth', 'help':'HTTP Basic Auth credentials for the channel', 'required':False},
        {'name':'--api-key', 'help':'API key-based credentials for the channel', 'required':False},
        {'name':'--store-requests', 'help':'How many requests to store in audit log',
            'required':False, 'default':0, 'type': int},
        {'name':'--store-responses', 'help':'How many responses to store in audit log',
            'required':False, 'default':0, 'type': int},
        {'name':'--max-bytes-requests', 'help':'How many bytes of each request to store',
            'required':False, 'default':500, 'type': int},
        {'name':'--max-bytes-responses', 'help':'How many bytes of each response to store',
            'required':False, 'default':500, 'type': int},
        {'name':'--path', 'help':'Path to a Zato server', 'required':True},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        name = getattr(args, 'name', None)
        is_active = getattr(args, 'is_active', None)
        url_path = getattr(args, 'url_path', None)
        channel_service = getattr(args, 'service', None) or Config.ServiceName
        basic_auth = getattr(args, 'basic_auth', '')
        api_key = getattr(args, 'api_key', '')
        store_requests = getattr(args, 'store_requests', 0)
        store_responses = getattr(args, 'store_responses', 0)
        max_bytes_requests = getattr(args, 'max_bytes_requests', None) or Config.MaxBytesRequests
        max_bytes_responses = getattr(args, 'max_bytes_requests', None) or Config.MaxBytesResponses

        # Assume that the channel should be active
        is_active = getattr(args, 'is_active', True)
        if is_active is None:
            is_active = True

        # Generate a name if one is not given
        name = name or 'auto.rest.channel.' + fs_safe_now()

        # If we have no URL path, base it on the auto-generate name
        if not url_path:
            url_path = '/'+ name

        # Enable the audit log if told to
        is_audit_log_received_active = bool(store_requests)
        is_audit_log_sent_active = bool(store_responses)

        # Obtain the security ID based on input data,
        # creating the definition if necessary.
        security_id = self._get_security_id(basic_auth=basic_auth, api_key=api_key)

        # API service to invoke
        service = 'zato.http-soap.create'

        # API request to send
        request = {
            'name': name,
            'url_path': url_path,
            'service': channel_service,
            'is_active': is_active,
            'connection': CONNECTION.CHANNEL,

            security_id: security_id,

            'is_audit_log_received_active': is_audit_log_received_active,
            'is_audit_log_sent_active': is_audit_log_sent_active,

            'max_len_messages_received': store_requests,
            'max_len_messages_sent': store_responses,

            'max_bytes_per_message_received': max_bytes_requests,
            'max_bytes_per_message_sent': max_bytes_responses,
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

class DeleteChannel(SecurityAwareCommand):
    """ Deletes a REST channel.
    """
    opts = [
        {'name':'--id', 'help':'ID of the channel to delete', 'required':False},
        {'name':'--name', 'help':'Name of the channel to delete', 'required':False},
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

class CreateOutconn(SecurityAwareCommand):
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
