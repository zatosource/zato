# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps

# Bunch
from bunch import Bunch

# gevent
import gevent

# Zato
from zato.common import BROKER, CHANNEL, DATA_FORMAT
from zato.common.broker_message import SERVICE
from zato.common.util import new_cid
from zato.common.test import ServiceTestCase, rand_int, rand_string
from zato.server.service.internal.pattern.invoke_retry import InvokeRetry

# ################################################################################################################################

class InvokeRetryTestCase(ServiceTestCase):

# ################################################################################################################################

    def setUp(self):
        self.broker_client_publish = True

# ################################################################################################################################

    def test_handle_simple_ok_exception(self):

        for is_ok in True, False:

            expected_response = 'expected_response_{}'.format(rand_string())

            class Ping(object):
                name = 'zato.ping'
                passthrough_to = False

                def __init__(self):
                    self.response = Bunch(payload=expected_response)

                def update(self, *ignored_args, **ignored_kwargs):
                    if not is_ok:
                        raise Exception()

                post_handle = validate_output = handle = validate_input = call_hooks = pre_handle = update

            service_store_name_to_impl_name = {'zato.ping':'zato.service.internal.ping'}
            service_store_impl_name_to_service = {'zato.service.internal.ping':Ping}

            callback = rand_string()
            target = 'zato.ping'
            cid = new_cid()

            payload = {
                'orig_cid': cid,
                'callback': callback,
                'callback_context': {rand_string():rand_string()},
                'target': target,
                'retry_repeats': 4,
                'retry_seconds': 0.1,
                'args': [1,2,3],
                'kwargs': {rand_string():rand_string(), rand_int():rand_int()},
                }

            instance = self.invoke(
                InvokeRetry, dumps(payload), None, service_store_name_to_impl_name=service_store_name_to_impl_name,
                service_store_impl_name_to_service=service_store_impl_name_to_service)

            gevent.sleep(0.5)

            self.assertEquals(len(instance.broker_client.invoke_async_args), 1)
            self.assertEquals(len(instance.broker_client.invoke_async_args[0]), 1)

            async_msg = Bunch(instance.broker_client.invoke_async_args[0][0])
            self.assertEquals(len(async_msg), 9)

            self.assertEquals(async_msg.action, SERVICE.PUBLISH.value)
            self.assertEquals(async_msg.channel, CHANNEL.INVOKE_ASYNC)
            self.assertEquals(async_msg.data_format, DATA_FORMAT.DICT)
            self.assertEquals(async_msg.transport, None)

            self.assertEquals(async_msg.payload, dumps({
                'ok': is_ok,
                'target': target,
                'retry_seconds': payload['retry_seconds'],
                'context': payload['callback_context'],
                'orig_cid': payload['orig_cid'],
                'retry_repeats': payload['retry_repeats'],
                }))

            self.assertTrue(len(instance.broker_client.invoke_async_kwargs) == 1)
            self.assertEquals(instance.broker_client.invoke_async_kwargs[0], {'expiration':BROKER.DEFAULT_EXPIRATION})

# ################################################################################################################################
