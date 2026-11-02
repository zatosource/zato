# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import subprocess
import tempfile
import time
import unittest

# PyYAML
import yaml

# Zato
from zato.common.api import PubSub
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient, PublishClient
from zato.common.test.config_pubsub_service_subscriber import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_service_subscriber')

# ################################################################################################################################
# ################################################################################################################################

_receiver_1 = 'test.pubsub.service-subscriber.receiver-1'
_receiver_2 = 'test.pubsub.service-subscriber.receiver-2'
_receiver_3 = 'test.pubsub.service-subscriber.receiver-3'
_receiver_4 = 'test.pubsub.service-subscriber.receiver-4'

_topic_orders   = 'service-subscriber.orders'
_topic_invoices = 'service-subscriber.invoices'

# How long a pushed message may take to reach its receiver, in seconds
_delivery_timeout = 20

# How often the receivers are polled, in seconds
_poll_interval = 0.5

# How long a receiver must stay without a new message before it is considered to have received everything, in seconds
_quiet_period = 3

# How long a probe waits for its delivery before another probe is published, in seconds
_probe_wait = 2

# How long a subscription imported into the running server may take to start receiving messages, in seconds
_propagation_timeout = 45

# How long one enmasse command may run, in seconds
_enmasse_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

class TestServiceSubscriber(unittest.TestCase):
    """ Subscriptions whose subscriber is a service, without a security definition - how they are stored,
    how messages are pushed to them, and how enmasse imports and exports them.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = AdminClient(TestConfig.base_url, TestConfig.password)
        class_.publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def setUp(self) -> 'None':
        _ = self.client.invoke('test.pubsub.service-subscriber.clear-received')

# ################################################################################################################################
# ################################################################################################################################

    def _get_service_subscriptions(self) -> 'anydict':
        """ Returns the subscriptions without a security definition, keyed by the name of the service they push to.
        """
        response = self.client.invoke('zato.pubsub.subscription.get-list')
        out:'anydict' = {}

        for item in response:
            if item['sec_base_id'] is None:
                out[item['push_service_name']] = item

        return out

# ################################################################################################################################

    def _get_topic_names(self, subscription:'anydict') -> 'strlist':
        """ Returns the sorted names of the topics of a subscription.
        """
        out:'strlist' = []

        for topic in subscription['topic_name_list']:
            out.append(topic['topic_name'])

        out.sort()
        return out

# ################################################################################################################################

    def _get_received(self, service_name:'str') -> 'anylist':
        """ Returns the data of each message pushed to the receiver of the given name, parsed from JSON.
        """
        response = self.client.invoke('test.pubsub.service-subscriber.get-received')

        if isinstance(response, str):
            response = json.loads(response)

        out:'anylist' = []

        if service_name in response:
            for item in response[service_name]:
                data = json.loads(item)
                out.append(data)

        return out

# ################################################################################################################################

    def _wait_for_count(self, service_name:'str', expected_count:'int') -> 'anylist':
        """ Waits until the receiver of the given name has at least the expected number of messages and returns them.
        """
        deadline = time.monotonic() + _delivery_timeout

        while time.monotonic() < deadline:
            received = self._get_received(service_name)
            if len(received) >= expected_count:
                return received
            time.sleep(_poll_interval)

        out = self._get_received(service_name)
        return out

# ################################################################################################################################

    def _wait_until_quiet(self, service_name:'str') -> 'anylist':
        """ Waits until the receiver of the given name has received nothing new for the quiet period and returns its messages.
        """
        received = self._get_received(service_name)
        quiet_since = time.monotonic()

        while time.monotonic() - quiet_since < _quiet_period:

            time.sleep(_poll_interval)
            current = self._get_received(service_name)

            if len(current) != len(received):
                received = current
                quiet_since = time.monotonic()

        out = received
        return out

# ################################################################################################################################

    def _publish_marked(self, topic_name:'str') -> 'str':
        """ Publishes one message carrying a unique marker to the topic and returns the marker.
        """
        marker = CryptoManager.generate_hex_string(16)
        _ = self.publisher.publish(topic_name, {'marker': marker})

        out = marker
        return out

# ################################################################################################################################

    def _get_markers(self, received:'anylist') -> 'strlist':
        """ Returns the marker of each message received.
        """
        out:'strlist' = []

        for data in received:
            out.append(data['marker'])

        return out

# ################################################################################################################################

    def _publish_until_delivered(self, topic_name:'str', service_name:'str') -> 'None':
        """ Publishes probes to the topic until the receiver of the given name receives one, which shows
        that a subscription imported into the running server is in effect, then clears what every receiver stored.
        """
        deadline = time.monotonic() + _propagation_timeout

        while time.monotonic() < deadline:

            _ = self._publish_marked(topic_name)
            probe_deadline = time.monotonic() + _probe_wait

            while time.monotonic() < probe_deadline:

                received = self._get_received(service_name)

                if received:

                    # Probes still in flight are let arrive before the receivers are cleared
                    _ = self._wait_until_quiet(service_name)
                    _ = self.client.invoke('test.pubsub.service-subscriber.clear-received')
                    return

                time.sleep(_poll_interval)

        raise Exception(f'No probe published to `{topic_name}` reached `{service_name}` within {_propagation_timeout}s')

# ################################################################################################################################

    def _run_enmasse(self, args:'strlist') -> 'None':
        """ Runs one enmasse command against the running server and expects it to succeed.
        """
        enmasse_environment = os.environ.copy()
        _ = enmasse_environment.pop('COVERAGE_PROCESS_START', None)

        command = [TestConfig.zato_bin, 'enmasse', TestConfig.server_directory, '--verbose']
        command.extend(args)

        result = subprocess.run(command, capture_output=True, text=True, timeout=_enmasse_timeout, env=enmasse_environment)

        self.assertEqual(result.returncode, 0, f'enmasse failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

    def _import_yaml(self, yaml_text:'str') -> 'None':
        """ Imports the YAML document into the running server through enmasse.
        """
        file_suffix = CryptoManager.generate_hex_string(8)
        input_path = os.path.join(tempfile.gettempdir(), f'zato-pubsub-service-subscriber-{os.getpid()}-{file_suffix}.yaml')

        with open(input_path, 'w') as input_file:
            _ = input_file.write(yaml_text)

        try:
            self._run_enmasse(['--import', '--input', input_path, '--missing-wait-time', '15'])
        finally:
            os.remove(input_path)

# ################################################################################################################################

    def _build_subscription_yaml(self, service_name:'str', topic_names:'strlist') -> 'str':
        """ Returns an enmasse document with one subscription of the service to the topics, without a security definition.
        """
        lines = [
            'pubsub_subscription:',
            '',
            '  - delivery_type: push',
            f'    push_service: {service_name}',
            '    topic_list:',
        ]

        for topic_name in topic_names:
            lines.append(f'      - {topic_name}')

        lines.append('')

        out = '\n'.join(lines)
        return out

# ################################################################################################################################
# ################################################################################################################################

    def test_01_subscriptions_have_no_security_definition(self) -> 'None':
        """ Each service subscription imported at startup is stored without a security definition,
        with push delivery to its service, under the service's name, and with a sub_key of its own.
        """
        subscriptions = self._get_service_subscriptions()

        self.assertIn(_receiver_1, subscriptions)
        self.assertIn(_receiver_2, subscriptions)

        for service_name in (_receiver_1, _receiver_2):

            subscription = subscriptions[service_name]
            logger.info('Service subscription -> %s', subscription)

            self.assertIsNone(subscription['sec_base_id'])
            self.assertIsNone(subscription['sec_name'])
            self.assertEqual(subscription['security'], service_name)
            self.assertEqual(subscription['delivery_type'], PubSub.Delivery_Type.Push)
            self.assertEqual(subscription['push_type'], PubSub.Push_Type.Service)
            self.assertTrue(subscription['sub_key'].startswith('sk'))

        receiver_1_topics = self._get_topic_names(subscriptions[_receiver_1])
        receiver_2_topics = self._get_topic_names(subscriptions[_receiver_2])

        self.assertEqual(receiver_1_topics, sorted([_topic_orders, _topic_invoices]))
        self.assertEqual(receiver_2_topics, [_topic_orders])

        self.assertNotEqual(subscriptions[_receiver_1]['sub_key'], subscriptions[_receiver_2]['sub_key'])

# ################################################################################################################################

    def test_02_message_is_pushed_to_every_subscribed_service(self) -> 'None':
        """ A message published to a topic is pushed once to each service subscribed to it.
        """
        marker = self._publish_marked(_topic_orders)

        _ = self._wait_for_count(_receiver_1, 1)
        _ = self._wait_for_count(_receiver_2, 1)

        receiver_1_markers = self._get_markers(self._wait_until_quiet(_receiver_1))
        receiver_2_markers = self._get_markers(self._wait_until_quiet(_receiver_2))

        self.assertEqual(receiver_1_markers, [marker])
        self.assertEqual(receiver_2_markers, [marker])

# ################################################################################################################################

    def test_03_message_reaches_only_subscribed_services(self) -> 'None':
        """ A message published to a topic is not pushed to a service that is not subscribed to that topic.
        """
        marker = self._publish_marked(_topic_invoices)

        receiver_1_received = self._wait_for_count(_receiver_1, 1)
        receiver_1_markers = self._get_markers(receiver_1_received)

        self.assertEqual(receiver_1_markers, [marker])

        receiver_2_received = self._wait_until_quiet(_receiver_2)
        self.assertEqual(receiver_2_received, [])

# ################################################################################################################################

    def test_04_enmasse_reimport_keeps_one_subscription_per_service(self) -> 'None':
        """ Importing the same service subscriptions again updates them in place - the sub_keys stay the same,
        no second subscription appears and each message is still pushed exactly once.
        """
        before = self._get_service_subscriptions()

        receiver_1_yaml = self._build_subscription_yaml(_receiver_1, [_topic_orders, _topic_invoices])
        receiver_2_yaml = self._build_subscription_yaml(_receiver_2, [_topic_orders])

        self._import_yaml(receiver_1_yaml)
        self._import_yaml(receiver_2_yaml)

        after = self._get_service_subscriptions()

        for service_name in (_receiver_1, _receiver_2):
            self.assertEqual(after[service_name]['sub_key'], before[service_name]['sub_key'])

        response = self.client.invoke('zato.pubsub.subscription.get-list')
        receiver_1_count = 0

        for item in response:
            if item['push_service_name'] == _receiver_1:
                receiver_1_count += 1

        self.assertEqual(receiver_1_count, 1)

        marker = self._publish_marked(_topic_orders)

        _ = self._wait_for_count(_receiver_1, 1)
        _ = self._wait_for_count(_receiver_2, 1)

        receiver_1_markers = self._get_markers(self._wait_until_quiet(_receiver_1))
        receiver_2_markers = self._get_markers(self._wait_until_quiet(_receiver_2))

        self.assertEqual(receiver_1_markers, [marker])
        self.assertEqual(receiver_2_markers, [marker])

# ################################################################################################################################

    def test_05_enmasse_creates_service_subscription_at_runtime(self) -> 'None':
        """ A service subscription imported into the running server is stored without a security definition
        and starts receiving the messages published to its topic.
        """
        subscription_yaml = self._build_subscription_yaml(_receiver_3, [_topic_orders])
        self._import_yaml(subscription_yaml)

        subscriptions = self._get_service_subscriptions()
        self.assertIn(_receiver_3, subscriptions)

        subscription = subscriptions[_receiver_3]
        self.assertIsNone(subscription['sec_base_id'])
        self.assertEqual(self._get_topic_names(subscription), [_topic_orders])

        self._publish_until_delivered(_topic_orders, _receiver_3)

        marker = self._publish_marked(_topic_orders)
        _ = self._wait_for_count(_receiver_3, 1)

        receiver_3_markers = self._get_markers(self._wait_until_quiet(_receiver_3))
        self.assertEqual(receiver_3_markers, [marker])

# ################################################################################################################################

    def test_06_enmasse_updates_topics_of_service_subscription(self) -> 'None':
        """ Importing a service subscription again with another topic list changes its topics under the same sub_key,
        and the service then receives the messages of the topic added.
        """
        first_yaml = self._build_subscription_yaml(_receiver_4, [_topic_orders])
        self._import_yaml(first_yaml)

        self._publish_until_delivered(_topic_orders, _receiver_4)

        sub_key_before = self._get_service_subscriptions()[_receiver_4]['sub_key']

        second_yaml = self._build_subscription_yaml(_receiver_4, [_topic_orders, _topic_invoices])
        self._import_yaml(second_yaml)

        subscription = self._get_service_subscriptions()[_receiver_4]

        self.assertEqual(subscription['sub_key'], sub_key_before)
        self.assertEqual(self._get_topic_names(subscription), sorted([_topic_orders, _topic_invoices]))

        self._publish_until_delivered(_topic_invoices, _receiver_4)

        marker = self._publish_marked(_topic_invoices)
        _ = self._wait_for_count(_receiver_4, 1)

        receiver_4_markers = self._get_markers(self._wait_until_quiet(_receiver_4))
        self.assertEqual(receiver_4_markers, [marker])

# ################################################################################################################################

    def test_07_enmasse_export_omits_security_definition(self) -> 'None':
        """ An export lists each service subscription by its service, with no security key.
        """
        file_suffix = CryptoManager.generate_hex_string(8)
        output_path = os.path.join(tempfile.gettempdir(), f'zato-pubsub-service-subscriber-export-{os.getpid()}-{file_suffix}.yaml')

        try:
            self._run_enmasse(['--export', '--output', output_path, '--include-type', 'pubsub_subscription'])

            with open(output_path) as output_file:
                exported = yaml.safe_load(output_file)

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

        exported_by_service:'anydict' = {}

        for item in exported['pubsub_subscription']:
            if 'push_service' in item:
                exported_by_service[item['push_service']] = item

        self.assertIn(_receiver_1, exported_by_service)
        self.assertIn(_receiver_2, exported_by_service)

        receiver_1_item = exported_by_service[_receiver_1]
        logger.info('Exported service subscription -> %s', receiver_1_item)

        self.assertNotIn('security', receiver_1_item)
        self.assertEqual(receiver_1_item['delivery_type'], PubSub.Delivery_Type.Push)
        self.assertEqual(sorted(receiver_1_item['topic_list']), sorted([_topic_orders, _topic_invoices]))

        receiver_2_item = exported_by_service[_receiver_2]

        self.assertNotIn('security', receiver_2_item)
        self.assertEqual(receiver_2_item['topic_list'], [_topic_orders])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
