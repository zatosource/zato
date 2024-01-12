# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from uuid import uuid4

# Zato
from zato.cli import ServerAwareCommand
from zato.common.api import CONNECTION, ZATO_NONE
from zato.common.util.api import fs_safe_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    from zato.common.typing_ import anytuple, stranydict
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

    def _extract_credentials(self, name:'str', credentials:'str', needs_header:'bool') -> 'anytuple':

        credentials_lower = credentials.lower()

        if credentials_lower == 'true':
            username = name
            value_type = 'key' if needs_header else 'password'
            password = 'api.{}.'.format(value_type) + uuid4().hex

            # If the username is represented through an HTTP header,
            # turn the value into one.
            if needs_header:

                # 'T' is included below because it was part of the timestamp,
                # e.g. auto.rest.channel.2022_03_26T19_47_12_191630.
                username = username.replace('.', '-').replace('_', '-').replace('T', '-')
                username = username.split('-')
                username = [elem.capitalize() for elem in username]
                username = 'X-' + '-'.join(username)

        elif credentials_lower == 'false':
            username, password = None, None

        else:
            _credentials = credentials.split(',')
            _credentials = [elem.strip() for elem in _credentials]
            username, password = _credentials

        return username, password

# ################################################################################################################################

    def _get_security_id(self, *, name:'str', basic_auth:'str', api_key:'str') -> 'stranydict':

        # Zato
        from zato.common.util.cli import APIKeyManager, BasicAuthManager

        out = {}

        if basic_auth:

            username, password = self._extract_credentials(name, basic_auth, False)
            manager = BasicAuthManager(self, name, True, username, 'API', password)
            response = manager.create()

            out['username'] = username
            out['password'] = password
            out['security_id'] = response['id']

        elif api_key:

            header, key = self._extract_credentials(name, api_key, True)
            manager = APIKeyManager(self, name, True, header, key)
            response = manager.create()

            out['header'] = header
            out['key'] = key
            out['security_id'] = response['id']

        else:
            # Use empty credentials to explicitly indicate that none are required
            out['username'] = None
            out['password'] = None

            out['security_id'] = ZATO_NONE

        # No matter what we had on input, we can return our output now.
        return out

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

        # For later use
        now = fs_safe_now()

        # Assume that the channel should be active
        is_active = getattr(args, 'is_active', True)
        if is_active is None:
            is_active = True

        # Generate a name if one is not given
        name = name or 'auto.rest.channel.' + now

        # If we have no URL path, base it on the auto-generate name
        if not url_path:
            url_path = '/'+ name

        # Enable the audit log if told to
        is_audit_log_received_active = bool(store_requests)
        is_audit_log_sent_active = bool(store_responses)

        # Obtain the security ID based on input data, creating the definition if necessary.
        sec_name = 'auto.sec.' + now
        security_info = self._get_security_id(name=sec_name, basic_auth=basic_auth, api_key=api_key)
        security_id = security_info.pop('security_id')

        # API service to invoke
        service = 'zato.http-soap.create'

        # API request to send
        request = {
            'name': name,
            'url_path': url_path,
            'service': channel_service,
            'is_active': is_active,
            'connection': CONNECTION.CHANNEL,
            'security_id': security_id,
            'is_audit_log_received_active': is_audit_log_received_active,
            'is_audit_log_sent_active': is_audit_log_sent_active,

            'max_len_messages_received': store_requests,
            'max_len_messages_sent': store_responses,

            'max_bytes_per_message_received': max_bytes_requests,
            'max_bytes_per_message_sent': max_bytes_responses,
        }

        # Invoke the base service that creates a channel ..
        response = self._invoke_service(service, request)

        # .. update the response with the channel security definition's details ..
        response.update(security_info)

        # .. finally, log the response for the caller.
        self._log_response(response, needs_stdout=True)

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
            self.logger.warn('Cannot continue. To delete a REST channel, either --id or --name is required on input.')
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # API service to invoke
        service = 'zato.http-soap.delete'

        # API request to send
        request = {
            'id': id,
            'name': name,
            'connection': CONNECTION.CHANNEL,
            'should_raise_if_missing': False
        }

        self._invoke_service_and_log_response(service, request)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace
    from os import environ

    now = fs_safe_now()

    username = 'cli.username.' + now
    password = 'cli.password.' + now

    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.service = Config.ServiceName
    # args.basic_auth = f'{username}, {password}'
    args.api_key = 'true'
    args.path = environ['ZATO_SERVER_BASE_DIR']

    command = CreateChannel(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
