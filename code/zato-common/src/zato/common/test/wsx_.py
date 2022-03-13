# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test import CommandLineTestCase
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class WSXChannelManager:

    test_case: 'CommandLineTestCase'
    channel_id: 'str'

    def __init__(self, test_case:'CommandLineTestCase') -> 'None':
        self.test_case = test_case
        self.channel_id = ''

    def __enter__(self):

        # Command to invoke ..
        cli_params = ['wsx', 'create-channel']

        # .. get its response as a dict ..
        out = self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

        # .. extract an address of a newly created WSX channel ..
        address = out['address']

        # .. store for later use ..
        self.channel_id = out['id']

        # .. and return it to our caller.
        return address

# ################################################################################################################################

    def __exit__(self, type_:'any_', value:'any_', traceback:'any_'):

        # Command to invoke ..
        cli_params = ['wsx', 'delete-channel', '--id', self.channel_id, '--verbose']

        # .. get its response as a dict ..
        self.test_case.run_zato_cli_json_command(cli_params) # type: anydict

# ################################################################################################################################
# ################################################################################################################################
