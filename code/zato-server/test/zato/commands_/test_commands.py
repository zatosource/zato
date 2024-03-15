# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main

# Zato
from zato.common.test import CommandLineServiceTestCase

# ################################################################################################################################
# ################################################################################################################################

class ServiceCommandsTestCase(CommandLineServiceTestCase):

    def test_service_commands(self) -> 'None':

        # Test service to execute
        service_name = 'helpers.commands-service'

        # Run the test now
        self.run_zato_service_test(service_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
