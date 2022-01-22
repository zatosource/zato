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
from json import dumps
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

        class WSXServicesTestCase(TestCase, PubSubTestingClass):

            def _subscribe(_self, topic_name): # type: ignore
                service = 'zato.pubsub.pubapi.subscribe'
                response = self.invoke(service, {'topic_name': topic_name})
                return response['sub_key']

            def _unsubscribe(_self, topic_name): # type: ignore
                service = 'zato.pubsub.pubapi.unsubscribe'
                response = self.invoke(service, {'topic_name': topic_name})
                return response

            def _publish(_self, topic_name, data): # type: ignore
                service = 'zato.pubsub.pubapi.publish-message'
                response = self.invoke(service, {'topic_name': topic_name, 'data':data})
                return response

            def _receive(_self, topic_name): # type: ignore
                service = 'zato.pubsub.pubapi.get-messages'
                response = self.invoke(service, {'topic_name': topic_name})
                return response

            def test_wsx_services_full_path_subscribe_before_publication(_self):
                tester = FullPathTester(_self, True)
                tester.run()

            def test_wsx_services_full_path_subscribe_after_publication(_self):
                tester = FullPathTester(_self, False)
                tester.run()

        try:
            iters = 10
            for _ in range(iters):
                suite = defaultTestLoader.loadTestsFromTestCase(WSXServicesTestCase)
                result = TextTestRunner().run(suite)

                if result.errors or result.failures:
                    errors   = []
                    failures = []

                    response = {
                        'errors':   errors,
                        'failures': failures,
                    }

                    for error in result.errors:
                        test, reason = error
                        test = str(test)
                        _error = {
                            'error_test': test,
                            'error_reason': reason,
                        }
                        self.logger.warn('Test error -> %s', result.errors)
                        errors.append(_error)

                    for failure in result.failures:
                        test, reason = failure
                        test = str(test)
                        reason = '\n'.join(reason)
                        _failure = {
                            'failure_test': test,
                            'failure_reason': reason,
                        }
                        self.logger.warn('Test Failure -> %s', result.errors)
                        errors.append(_failure)

                    # Serialize all the warnings and errors ..
                    self.response.payload = dumps(response)

                    # .. and do resume the test.
                    break

            # If we ar here, it means that there was no error
            else:
                self.response.payload = 'OK'

        except Exception:
            msg = 'Exception in {} -> {}'.format(self.__class__.__name__, format_exc())
            self.logger.warn(msg)
            self.response.payload = msg

# ################################################################################################################################
# ################################################################################################################################
'''
