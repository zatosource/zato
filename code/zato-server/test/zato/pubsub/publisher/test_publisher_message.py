# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from unittest import TestCase

# Zato
from zato.common.test.pubsub.publisher import PublisherTestData
from zato.common.api import PUBSUB
from zato.common.typing_ import cast_
from zato.common.util.time_ import utcnow_as_ms
from zato.server.pubsub.publisher import Publisher, PubRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.server.pubsub.publisher import PubSubMessage
    ParallelServer = ParallelServer
    PubSubMessage = PubSubMessage

# ################################################################################################################################
# ################################################################################################################################

class PublisherMessageTestCase(TestCase):

    def get_default_request(
        self,
        *,
        cid,           # type: str
        data,          # type: str
        mime_type,     # type: str
        ext_client_id, # type: str
        ext_pub_time,  # type: str
    ) -> 'PubRequest':

        data = {
            'data': data,
            'mime_type': mime_type,
            'ext_client_id': ext_client_id,
            'ext_pub_time': ext_pub_time
        } # type: ignore

        # Correlation ID (cid) is provided via extra parameters so as to use the same mechanism that the publish service uses.
        out = PubRequest._zato_from_dict(data, extra={'cid':cid})
        return out

# ################################################################################################################################

    def get_test_publisher(self, test_data:'type[PublisherTestData]') -> 'Publisher':

        publisher = Publisher(
            pubsub = test_data.pubsub,
            server = cast_('ParallelServer', test_data.server),
            marshal_api = test_data.server.marshal_api,
            service_invoke_func = test_data.service_invoke_func,
            new_session_func = test_data.new_session_func,
        )

        return publisher

# ################################################################################################################################

    def test_get_data_prefixes(self) -> 'None':

        # Make a deep copy so as not to interfere with other tests.
        test_data = deepcopy(PublisherTestData)

        # Make them shorted for the purposes of our test
        test_data.pubsub.data_prefix_len = 7
        test_data.pubsub.data_prefix_short_len = 3

        publisher = self.get_test_publisher(test_data)

        data = '1234567890'
        data_prefix, data_prefix_short = publisher.get_data_prefixes(data)

        self.assertEqual(data_prefix, '1234567')
        self.assertEqual(data_prefix_short, '123')

# ################################################################################################################################

    def test_build_message_simple(self) -> 'None':

        # Make a deep copy so as not to interfere with other tests.
        test_data = deepcopy(PublisherTestData)

        # This is information about the message ..
        cid = 'cid.123'
        data = '{"Hello":"This is my data"}'
        mime_type = 'application/json'
        ext_client_id = 'my.ext.client.id.1'
        ext_pub_time = '2018-10-08T09:08:20.894193'

        # .. this is information about the publication ..
        now = 1.0
        endpoint_id = 8
        topic = test_data.topic
        has_no_sk_server = False
        pub_pattern_matched = '/*'
        subscriptions_by_topic = []

        # .. generate a default message based on the message's data ..
        request = self.get_default_request(
            cid = cid,
            data = data,
            mime_type = mime_type,
            ext_client_id = ext_client_id,
            ext_pub_time = ext_pub_time
        )

        # .. build a publisher object ..
        publisher = self.get_test_publisher(test_data)

        # .. build a timestamp before the test for later comparisons ..
        now_before_test = utcnow_as_ms()

        # .. transform the message data into an actual business object ..
        message = cast_('PubSubMessage', publisher.build_message(
            topic, request, now, pub_pattern_matched, endpoint_id, subscriptions_by_topic, has_no_sk_server))

        # .. build a timestamp after the test, also for later comparisons ..
        now_after_test = utcnow_as_ms()

        # .. and run the assertions now ..

        self.assertEqual(message.cluster_id, test_data.cluster_id)
        self.assertEqual(message.data, data)
        self.assertEqual(message.data_prefix, data)
        self.assertEqual(message.data_prefix_short, data)
        self.assertEqual(message.delivery_count, 0)
        self.assertEqual(message.delivery_status, str(PUBSUB.DELIVERY_STATUS.INITIALIZED))
        self.assertEqual(message.expiration, PUBSUB.DEFAULT.LimitMessageExpiry)
        self.assertEqual(message.expiration_time, 86401.0)
        self.assertEqual(message.expiration_time_iso, '')

        self.assertEqual(message.ext_pub_time_iso, '')
        self.assertIsNone(message.group_id)
        self.assertTrue(message.has_gd)
        self.assertIsNone(message.in_reply_to)
        self.assertFalse(message.is_in_sub_queue)
        self.assertEqual(message.mime_type, mime_type)
        self.assertEqual(message.position_in_group, 1)
        self.assertIsNone(message.pub_correl_id)
        self.assertTrue(message.pub_msg_id.startswith('zpsm'))
        self.assertTrue(len(message.pub_msg_id) >= 24)
        self.assertEqual(message.pub_pattern_matched, '/*')
        self.assertEqual(message.pub_time, '1.0000000')
        self.assertEqual(message.published_by_id, endpoint_id)
        self.assertLess(now_before_test, message.recv_time)
        self.assertGreater(now_after_test, message.recv_time)
        self.assertEqual(message.recv_time_iso, '')
        self.assertEqual(message.reply_to_sk, [])
        self.assertEqual(message.server_name, '')
        self.assertEqual(message.server_pid, 0)
        self.assertEqual(message.size, len(data))
        self.assertEqual(message.sub_key, '')
        self.assertEqual(message.sub_pattern_matched, {})
        self.assertEqual(message.topic_id, topic.id)
        self.assertEqual(message.topic_name, topic.name)
        self.assertIsNone(message.user_ctx)
        self.assertEqual(message.zato_ctx, '{\n\n}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    from unittest import main
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
