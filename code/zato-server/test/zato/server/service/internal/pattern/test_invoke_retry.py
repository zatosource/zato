# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps
from logging import getLogger

# Arrow
import arrow

# Bunch
from bunch import Bunch

# gevent
import gevent

# Mock
from mock import MagicMock

# Zato
from zato.common import BROKER, CHANNEL, DATA_FORMAT
from zato.common.broker_message import SERVICE
from zato.common.util import new_cid
from zato.common.test import enrich_with_static_config, ServiceTestCase, rand_int, rand_string
from zato.server.service import Service
from zato.server.service.internal.pattern.invoke_retry import InvokeRetry
from zato.server.service.store import set_up_class_attributes

enrich_with_static_config(InvokeRetry)

logger = getLogger(__name__)

# ################################################################################################################################

class InvokeRetryTestCase(ServiceTestCase):

# ################################################################################################################################

    def setUp(self):
        self.broker_client_publish = True
        self.given_response = None

# ################################################################################################################################

    def test_handle_simple_ok_exception(self):

        test_instance = self

        for is_ok in True, False:

            expected_response = 'expected_response_{}'.format(rand_string()) if is_ok else None

            class Ping(Service):
                name = 'zato.ping'

                def __init__(self):
                    self.response = Bunch(payload=expected_response)
                    test_instance.given_response = expected_response

                def accept(self):
                    return True

                def update(self, *ignored_args, **ignored_kwargs):
                    if not is_ok:
                        raise Exception()

                def set_response_data(self, *ignored_args, **ignored_kwargs):
                    return expected_response

                post_handle = validate_output = handle = validate_input = call_hooks = pre_handle = update

            set_up_class_attributes(Ping)
            Ping.server = MagicMock()
            Ping.kvdb = MagicMock()

            callback = rand_string()
            target = 'zato.ping'

            orig_cid, call_cid = new_cid(), new_cid()
            source, req_ts_utc = rand_string(), rand_string()

            ping_impl = 'zato.service.internal.Ping'
            service_store_name_to_impl_name = {'zato.ping':ping_impl, callback:ping_impl}
            service_store_impl_name_to_service = {ping_impl:Ping}

            payload = {
                'source': source,
                'req_ts_utc': req_ts_utc,
                'orig_cid': orig_cid,
                'call_cid': call_cid,
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
            self.assertEquals(len(async_msg), 11)

            self.assertEquals(async_msg.action, SERVICE.PUBLISH.value)
            self.assertEquals(async_msg.channel, CHANNEL.INVOKE_ASYNC)
            self.assertEquals(async_msg.data_format, DATA_FORMAT.DICT)
            self.assertEquals(async_msg.transport, None)

            resp_ts_utc = async_msg.payload.pop('resp_ts_utc')

            # Is it a date? If not, an exception will be raised while parsing.
            arrow.get(resp_ts_utc)

            expected_response_msg = {
                'ok': is_ok,
                'source': source,
                'target': target,
                'req_ts_utc': req_ts_utc,
                'orig_cid': orig_cid,
                'call_cid': call_cid,
                'retry_seconds': payload['retry_seconds'],
                'context': payload['callback_context'],
                'retry_repeats': payload['retry_repeats'],
                'response': expected_response,
                }

            self.assertDictEqual(expected_response_msg, async_msg.payload)

            self.assertTrue(len(instance.broker_client.invoke_async_kwargs) == 1)
            self.assertEquals(instance.broker_client.invoke_async_kwargs[0], {'expiration':BROKER.DEFAULT_EXPIRATION})

# ################################################################################################################################
