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

class WSXServicesInvokerTest(CommandLineServiceTestCase):

    def test_wsx_services_invoker(self) -> 'None':

        # This service invokes a test suite that invokes all the services
        # that pubapi clients use for publish/subscribe.
        service_name = 'helpers.pubsub.pubapi-invoker'

        # Run the test now
        _ = self.run_zato_service_test(service_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
