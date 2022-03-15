# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.api import WEB_SOCKET

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test import CommandLineTestCase
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

ExtraProperties = WEB_SOCKET.ExtraProperties

# ################################################################################################################################
# ################################################################################################################################

class WSXChannelManager:

    test_case: 'CommandLineTestCase'
    username: 'str'
    password: 'str'
    channel_id: 'str'
    security_id: 'str'
    security_name: 'str'
    needs_credentials: 'bool'
    wsx_channel_address: 'str'

    def __init__(
        self,
        test_case:'CommandLineTestCase',
        username:'str' = '',
        password:'str' = '',
        needs_credentials:'bool' = False
    ) -> 'None':
        self.test_case = test_case
        self.username = username
        self.password = password
        self.needs_credentials = needs_credentials
        self.channel_id = ''
        self.security_id = ''
        self.security_name = ''
        self.wsx_channel_address = ''

# ################################################################################################################################

    def create_basic_auth(self):

        # Command to invoke ..
        cli_params = ['create', 'basic-auth', '--username', self.username, '--password', self.password]

        # .. always run in verbose mode ..
        cli_params.append('--verbose')

        # .. get the command's response as a dict ..
        out = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

        # .. and store the security definition's details for later use.
        self.security_id = out['id']
        self.security_name = out['name']

# ################################################################################################################################

    def __enter__(self) -> 'WSXChannelManager':

        # Command to invoke ..
        cli_params = ['wsx', 'create-channel']

        # .. credentials are optional ..
        if self.needs_credentials:

            # .. first, we need a Basic Auth definition for the WSX channel ..
            self.create_basic_auth()

            # .. now, we can make use of that definition ..
            cli_params.append('--security')
            cli_params.append(self.security_name)

        # .. we want for the channel to store the runtime context for later use ..
        extra_properties = dumps({
            ExtraProperties.StoreCtx: True
        })

        cli_params.append('--extra-properties')
        cli_params.append(extra_properties)

        # .. always run in verbose mode ..
        cli_params.append('--verbose')

        # .. get the command's response as a dict ..
        out = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

        # .. store for later use ..
        self.channel_id = out['id']
        self.wsx_channel_address = out['address']

        # .. and return control to the caller.
        return self

# ################################################################################################################################

    def delete_basic_auth(self):

        # Command to invoke ..
        cli_params = ['delete', 'basic-auth', '--id', self.security_id]

        # .. now, invoke the command, ignoring the result.
        _ = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

# ################################################################################################################################

    def __exit__(self, type_:'any_', value:'any_', traceback:'any_'):

        if self.needs_credentials:
            self.delete_basic_auth()

        # Command to invoke ..
        cli_params = ['wsx', 'delete-channel', '--id', self.channel_id, '--verbose']

        # .. get its response as a dict ..
        self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

# ################################################################################################################################
# ################################################################################################################################
