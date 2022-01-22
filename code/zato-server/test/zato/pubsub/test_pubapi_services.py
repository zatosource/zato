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

    def test_wsx_services_invoker(self) -> 'None':

        # This service invokes a test suite that invokes all the services
        # that pubapi clients use for publish/subscribe.
        service = 'pubsub1.my-service'

        # Prepare the invoker
        invoker = CommandLineServiceInvoker(check_stdout=False)

        # .. invoke the service and obtain its response ..
        out = invoker.invoke_and_test(service) # type: str
        out = out.strip()

        # .. make sure that the response points to a success.
        self.assertEqual(out, 'OK')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):
    """ Tests services that WebSocket clients use.
    """
    def handle(self):

        # stdlib
        from unittest import defaultTestLoader, TestCase, TextTestRunner

        # Zato
        from zato.common.test.config import TestConfig
        from zato.common.test.pubsub import FullPathTester, PubSubTestingClass

        topic_name = TestConfig.pubsub_topic_shared

        class WSXServicesTestCase(TestCase, PubSubTestingClass):

            def _subscribe(_self, *args, **kwargs): # type: ignore
                service = 'zato.pubsub.pubapi.subscribe'
                response = self.invoke(service, {'topic_name': topic_name})
                return response['sub_key']

            def _unsubscribe(_self, *args, **kwargs): # type: ignore
                service = 'zato.pubsub.pubapi.unsubscribe'
                response = self.invoke(service, {'topic_name': topic_name})
                return response

            def _publish(_self, data, **kwargs): # type: ignore
                service = 'zato.pubsub.pubapi.publish-message'
                response = self.invoke(service, {'topic_name': topic_name, 'data':data})
                return response

            def _receive(_self, *args, **kwargs): # type: ignore
                service = 'zato.pubsub.pubapi.get-messages'
                response = self.invoke(service, {'topic_name': topic_name})
                return response

            def test_wsx_services_full_path_subscribe_before_publication(_self):
                tester = FullPathTester(_self, True)
                tester.run()

            def test_wsx_services_full_path_subscribe_after_publication(_self):
                pass

        try:
            iters = 5
            for _ in range(iters):
                suite = defaultTestLoader.loadTestsFromTestCase(WSXServicesTestCase)
                TextTestRunner().run(suite)
            self.response.payload = 'OK'
        except Exception:
            msg = 'Exception in {} -> {}'.format(self.__class__.__name__, format_exc())
            self.logger.warn(msg)
            self.response.payload = msg

# ################################################################################################################################
# ################################################################################################################################
'''
