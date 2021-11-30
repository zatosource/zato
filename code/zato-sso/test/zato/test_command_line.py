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
from base import BaseTest, Config

# ################################################################################################################################
# ################################################################################################################################

class CommandLineTestCase(BaseTest):

# ################################################################################################################################

    def _assert_command_line_result(self, out:RunningCommand):
        self.assertEqual(out.exit_code, 0)
        self.assertEqual(out.stdout, b'(None)\n')

# ################################################################################################################################

    def test_command_line(self):
        out = sh.zato('service', 'invoke', Config.server_location, 'zato.sso.sso-test-service')
        self._assert_command_line_result(out)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
