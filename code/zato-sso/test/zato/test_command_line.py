# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from base import BaseTest
from zato.common.util.cli import CommandLineServiceInvoker

# ################################################################################################################################
# ################################################################################################################################

class CommandLineTestCase(BaseTest):

    def test_command_line(self) -> 'None':

        # stdlib
        import os

        if not os.environ.get('ZATO_TEST_SSO'):
            return

        service = 'zato.sso.sso-test-service'
        invoker = CommandLineServiceInvoker()
        invoker.invoke_and_test(service)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
