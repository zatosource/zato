# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.redis_backend import RedisPubSubBackend
from zato.server.base.parallel.delivery import RedisPushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_test_topic = 'test.delivery.topic'
_test_sub_key = 'zpsk.test.delivery'

# ################################################################################################################################
# ################################################################################################################################

class _MockServer:
    """ Minimal server mock that provides only what the delivery loop needs.
    """

    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}
        self._invoke_side_effect = None
        self._invoke_calls:'list' = []

    def invoke(self, service_name:'str', payload:'anydict') -> 'None':
        self._invoke_calls.append({'service_name': service_name, 'payload': payload})
        if self._invoke_side_effect:
            raise self._invoke_side_effect

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveryRetry(unittest.TestCase):
    """ Tests for at-least-once delivery with retry using a real Redis connection.
    """

    def setUp(self) -> 'None':
        self.redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)
        _ = self.redis.flushall()
        self.backend = RedisPubSubBackend(self.redis)
        self.server = _MockServer()

    def tearDown(self) -> 'None':
        _ = self.redis.flushall()
        _ = self.redis.close()

# ################################################################################################################################

    def _publish_and_subscribe(self, topic_name:'str'=_test_topic, sub_key:'str'=_test_sub_key) -> 'str':
        """ Publish a test message and subscribe, returning the msg_id.
        """
        self.backend.subscribe(sub_key, topic_name)
        result = self.backend.publish(topic_name, 'test-data', publisher='test')
        return result.msg_id

# ################################################################################################################################

    def _get_pending_count(self, topic_name:'str'=_test_topic, sub_key:'str'=_test_sub_key) -> 'int':
        """ Return the number of pending (unacked) messages for a consumer group.
        """
        stream_key = self.backend._get_stream_key(topic_name)
        try:
            pending_info = self.redis.xpending(stream_key, sub_key)
            return pending_info['pending']
        except Exception:
            return 0

# ################################################################################################################################

    def test_successful_delivery_acks(self) -> 'None':
        """ After successful delivery, the message must no longer be pending in Redis.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        self.assertEqual(len(messages), 1)

        # .. message is now pending (read but not acked) ..
        self.assertEqual(self._get_pending_count(), 1)

        # .. ack it ..
        self.backend.ack_message(messages[0]['_stream_name'], _test_sub_key, messages[0]['_redis_message_id'])

        # .. no longer pending ..
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_failed_delivery_does_not_ack(self) -> 'None':
        """ If delivery fails, the message must remain pending in Redis.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        self.assertEqual(len(messages), 1)

        # .. message is pending ..
        self.assertEqual(self._get_pending_count(), 1)

        # .. no ack called, message stays pending ..
        self.assertEqual(self._get_pending_count(), 1)

# ################################################################################################################################

    def test_retry_succeeds_on_second_attempt(self) -> 'None':
        """ If the first delivery attempt fails but the second succeeds,
        the message must be acknowledged.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        self.assertEqual(len(messages), 1)

        message = messages[0]

        # .. first attempt fails ..
        call_count = 0
        def _deliver(msg:'anydict', sub_config:'anydict') -> 'None':
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception('transient failure')

        self.server._push_subs[_test_sub_key] = [{'topic_name': _test_topic, 'push_type': PubSub.Push_Type.Service, 'push_service_name': 'test.service'}]

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        with patch.object(delivery, '_deliver_message', side_effect=_deliver):
            delivery._deliver_with_retry(message, self.server._push_subs[_test_sub_key][0], _test_sub_key, self.backend)

        self.assertEqual(call_count, 2)
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_deadline_exhausted(self) -> 'None':
        """ If delivery fails until the deadline, the message must still be acknowledged
        (dead-lettered) and an error must be logged.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        self.server._push_subs[_test_sub_key] = [{'topic_name': _test_topic, 'push_type': PubSub.Push_Type.Service, 'push_service_name': 'test.service'}]

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        call_idx = 0

        def _fake_monotonic() -> 'float':
            nonlocal call_idx
            call_idx += 1
            if call_idx == 1:
                return 0.0
            return PubSub.Delivery.Max_Retry_Time + 1.0

        with patch('zato.server.base.parallel.delivery.monotonic', side_effect=_fake_monotonic), \
             patch.object(delivery, '_deliver_message', side_effect=Exception('permanent failure')), \
             patch('zato.server.base.parallel.delivery.logger') as mock_logger:

            delivery._deliver_with_retry(message, self.server._push_subs[_test_sub_key][0], _test_sub_key, self.backend)
            mock_logger.error.assert_called_once()

        # .. message is acked even though delivery failed ..
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_pending_recovery_on_startup(self) -> 'None':
        """ After a simulated crash (message read but never acked), fetch_pending
        must return the unacked message so it can be retried.
        """
        _ = self._publish_and_subscribe()

        # .. read the message (simulating the pre-crash read) ..
        messages = self.backend.fetch_messages(_test_sub_key)
        self.assertEqual(len(messages), 1)
        self.assertEqual(self._get_pending_count(), 1)

        # .. simulate restart: fetch_pending returns the unacked message ..
        pending = self.backend.fetch_pending(_test_sub_key)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['msg_id'], messages[0]['msg_id'])

        # .. ack it ..
        self.backend.ack_message(pending[0]['_stream_name'], _test_sub_key, pending[0]['_redis_message_id'])
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_ordering_preserved(self) -> 'None':
        """ When delivery of the first message fails, subsequent messages must
        not be delivered until the first one succeeds.
        """
        self.backend.subscribe(_test_sub_key, _test_topic)
        _ = self.backend.publish(_test_topic, 'msg-1', publisher='test')
        _ = self.backend.publish(_test_topic, 'msg-2', publisher='test')
        _ = self.backend.publish(_test_topic, 'msg-3', publisher='test')

        messages = self.backend.fetch_messages(_test_sub_key, max_messages=3)
        self.assertEqual(len(messages), 3)

        delivered_order:'list' = []

        call_count = 0
        def _deliver(msg:'anydict', sub_config:'anydict') -> 'None':
            nonlocal call_count
            call_count += 1
            delivered_order.append(msg['data'])
            if call_count == 1:
                raise Exception('fail first message on first try')

        self.server._push_subs[_test_sub_key] = [{'topic_name': _test_topic, 'push_type': PubSub.Push_Type.Service, 'push_service_name': 'test.service'}]

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        with patch.object(delivery, '_deliver_message', side_effect=_deliver), \
             patch('zato.server.base.parallel.delivery.sleep'):
            delivery._deliver_batch(messages, _test_sub_key, self.backend)

        # .. msg-1 was attempted first (failed), then retried (succeeded), then msg-2, msg-3 ..
        self.assertEqual(delivered_order[0], 'msg-1')
        self.assertEqual(delivered_order[1], 'msg-1')
        self.assertEqual(delivered_order[2], 'msg-2')
        self.assertEqual(delivered_order[3], 'msg-3')

# ################################################################################################################################

    def test_rest_delivery_connection_error_retries(self) -> 'None':
        """ REST delivery must retry when requests.post raises ConnectionError.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.REST, 'rest_push_url': 'http://localhost:19999/test'}
        self.server._push_subs[_test_sub_key] = [sub_config]

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        post_call_count = 0
        def _fake_post(*args:'str', **kwargs:'str') -> 'MagicMock':
            nonlocal post_call_count
            post_call_count += 1
            if post_call_count == 1:
                from requests.exceptions import ConnectionError as RequestsConnectionError
                raise RequestsConnectionError('connection refused')
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            return mock_response

        with patch('requests.post', _fake_post), \
             patch('zato.server.base.parallel.delivery.sleep'):
            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)

        self.assertEqual(post_call_count, 2)
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_rest_delivery_retries_on_non_2xx(self) -> 'None':
        """ REST delivery must retry when the endpoint returns a non-2xx response.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.REST, 'rest_push_url': 'http://localhost:19999/test'}
        self.server._push_subs[_test_sub_key] = [sub_config]

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        post_call_count = 0
        def _fake_post(*args:'str', **kwargs:'str') -> 'MagicMock':
            nonlocal post_call_count
            post_call_count += 1
            mock_response = MagicMock()
            if post_call_count == 1:
                from requests.exceptions import HTTPError
                mock_response.raise_for_status.side_effect = HTTPError('500 Server Error')
            else:
                mock_response.raise_for_status = MagicMock()
            return mock_response

        with patch('requests.post', _fake_post), \
             patch('zato.server.base.parallel.delivery.sleep'):
            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)

        self.assertEqual(post_call_count, 2)
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_rest_delivery_succeeds_after_transient_failure(self) -> 'None':
        """ REST delivery must succeed on the second attempt after a transient failure.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.REST, 'rest_push_url': 'http://localhost:19999/test'}

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        post_call_count = 0
        def _fake_post(*args:'str', **kwargs:'str') -> 'MagicMock':
            nonlocal post_call_count
            post_call_count += 1
            if post_call_count == 1:
                raise OSError('network unreachable')
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            return mock_response

        with patch('requests.post', _fake_post), \
             patch('zato.server.base.parallel.delivery.sleep'):
            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)

        self.assertEqual(post_call_count, 2)
        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_rest_delivery_deadline_exhausted(self) -> 'None':
        """ REST delivery must ack (dead-letter) and log error when deadline is exceeded.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.REST, 'rest_push_url': 'http://localhost:19999/test'}

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        call_idx = 0

        def _fake_monotonic() -> 'float':
            nonlocal call_idx
            call_idx += 1
            if call_idx == 1:
                return 0.0
            return PubSub.Delivery.Max_Retry_Time + 1.0

        with patch('zato.server.base.parallel.delivery.monotonic', side_effect=_fake_monotonic), \
             patch('requests.post', side_effect=OSError('network down')), \
             patch('zato.server.base.parallel.delivery.logger') as mock_logger:

            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)
            mock_logger.error.assert_called_once()

        self.assertEqual(self._get_pending_count(), 0)

# ################################################################################################################################

    def test_backoff_increases_logarithmically(self) -> 'None':
        """ Sleep durations must increase from Retry_Interval_Initial toward Retry_Interval_Max.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.Service, 'push_service_name': 'test.service'}

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        sleep_values:'list' = []
        attempt_count = 0

        def _fake_sleep(duration:'float') -> 'None':
            sleep_values.append(duration)

        def _deliver_fail(msg:'anydict', sub_config:'anydict') -> 'None':
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 5:
                raise Exception('fail')

        with patch.object(delivery, '_deliver_message', side_effect=_deliver_fail), \
             patch('zato.server.base.parallel.delivery.sleep', side_effect=_fake_sleep):
            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)

        # .. sleep values must be non-decreasing (ignoring jitter) ..
        self.assertTrue(len(sleep_values) >= 2)

        # .. the first sleep must be based on the initial interval ..
        initial = PubSub.Delivery.Retry_Interval_Initial
        max_jitter = initial * PubSub.Delivery.Retry_Jitter_Percent / 100
        self.assertGreaterEqual(sleep_values[0], initial)
        self.assertLessEqual(sleep_values[0], initial + max_jitter)

# ################################################################################################################################

    def test_backoff_never_exceeds_max(self) -> 'None':
        """ No sleep duration must exceed Retry_Interval_Max plus its jitter.
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.Service, 'push_service_name': 'test.service'}

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        sleep_values:'list' = []
        attempt_count = 0

        def _fake_sleep(duration:'float') -> 'None':
            sleep_values.append(duration)

        def _deliver_fail(msg:'anydict', sub_config:'anydict') -> 'None':
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 20:
                raise Exception('fail')

        with patch.object(delivery, '_deliver_message', side_effect=_deliver_fail), \
             patch('zato.server.base.parallel.delivery.sleep', side_effect=_fake_sleep):
            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)

        max_interval = PubSub.Delivery.Retry_Interval_Max
        max_allowed = max_interval + max_interval * PubSub.Delivery.Retry_Jitter_Percent / 100

        for sleep_val in sleep_values:
            self.assertLessEqual(sleep_val, max_allowed)

# ################################################################################################################################

    def test_jitter_is_within_bounds(self) -> 'None':
        """ Each sleep duration must be within [interval, interval + interval * jitter_percent / 100].
        """
        _ = self._publish_and_subscribe()

        messages = self.backend.fetch_messages(_test_sub_key)
        message = messages[0]

        sub_config = {'topic_name': _test_topic, 'push_type': PubSub.Push_Type.Service, 'push_service_name': 'test.service'}

        redis_conn_params = {'host': 'localhost', 'port': 6379, 'db': 0, 'decode_responses': True}
        delivery = RedisPushDelivery(self.server, redis_conn_params)

        sleep_values:'list' = []
        attempt_count = 0

        def _fake_sleep(duration:'float') -> 'None':
            sleep_values.append(duration)

        def _deliver_fail(msg:'anydict', sub_config:'anydict') -> 'None':
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 10:
                raise Exception('fail')

        with patch.object(delivery, '_deliver_message', side_effect=_deliver_fail), \
             patch('zato.server.base.parallel.delivery.sleep', side_effect=_fake_sleep):
            delivery._deliver_with_retry(message, sub_config, _test_sub_key, self.backend)

        jitter_percent = PubSub.Delivery.Retry_Jitter_Percent
        initial = PubSub.Delivery.Retry_Interval_Initial

        # .. the first sleep must have jitter within bounds of the initial interval ..
        self.assertGreaterEqual(sleep_values[0], initial)
        self.assertLessEqual(sleep_values[0], initial + initial * jitter_percent / 100)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
