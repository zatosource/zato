# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# sh
import sh
from sh import RunningCommand

# Zato
from base import BaseTest
from zato.common.test.config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

class CommandLineTestCase(BaseTest):

# ################################################################################################################################

    def _assert_command_line_result(self, out:'RunningCommand') -> 'None':
        self.assertEqual(out.exit_code, 0)
        self.assertEqual(out.stdout, b'(None)\n')

# ################################################################################################################################

    def test_command_line(self) -> 'None':
        command = sh.zato # type: ignore
        out = command('service', 'invoke', TestConfig.server_location, 'zato.sso.sso-test-service')
        self._assert_command_line_result(out)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
