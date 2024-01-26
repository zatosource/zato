# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# ################################################################################################################################
# ################################################################################################################################

class CommandLineServiceInvokeTest(TestCase):

    def test_wsx_services(self) -> 'None':

        # Zato
        from zato.common.util.cli import CommandLineServiceInvoker

        service = 'zato.ping'
        expected_stdout = b"{'pong': 'zato'}\n"

        invoker = CommandLineServiceInvoker(expected_stdout)
        invoker.invoke_and_test(service)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
