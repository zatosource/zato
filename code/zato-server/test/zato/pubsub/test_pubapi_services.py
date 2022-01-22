# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import CommandLineServiceInvoker

# ################################################################################################################################
# ################################################################################################################################

class WSXServicesInvokerTest(TestCase):

    maxDiff = 1234567890

    def test_wsx_services_invoker(self) -> 'None':

        # This service invokes a test suite that invokes all the services
        # that pubapi clients use for publish/subscribe.
        service = 'helpers.pubsub.pubapi-invoker'

        # Prepare the invoker
        invoker = CommandLineServiceInvoker(check_stdout=False)

        # .. invoke the service and obtain its response ..
        out = invoker.invoke_and_test(service) # type: str
        out = out.strip()

        # .. make sure that the response indicates a success.
        self.assertEqual(out, 'OK')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
