# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from json import dumps
from types import SimpleNamespace
from unittest.mock import MagicMock

# Zato
from zato.common.api import PubSub
from zato.common.ext.bunch import Bunch
from zato.server.base.config_manager import ConfigManager, _pubsub_amqp_bridge_service

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManagerStub:
    """ Runs the real topic backend registry code of ConfigManager
    with everything around it mocked out.
    """

    # The real methods under test, bound to this stub
    _sync_pubsub_topics = ConfigManager._sync_pubsub_topics
    _apply_amqp_channel_override = ConfigManager._apply_amqp_channel_override
    _remove_amqp_channel_override = ConfigManager._remove_amqp_channel_override
    get_pubsub_topic_backend = ConfigManager.get_pubsub_topic_backend
    on_config_event_PUBSUB_TOPIC_CREATE = ConfigManager.on_config_event_PUBSUB_TOPIC_CREATE
    on_config_event_PUBSUB_TOPIC_EDIT = ConfigManager.on_config_event_PUBSUB_TOPIC_EDIT
    on_config_event_PUBSUB_TOPIC_DELETE = ConfigManager.on_config_event_PUBSUB_TOPIC_DELETE

    def __init__(self) -> 'None':
        self.server = MagicMock()
        self.config_store = MagicMock()
        self.config_store.pubsub_subs = {}
        self._push_subs = {}
        self._topic_backends = {}

        # These touch Redis and push delivery so they are not under test here
        self._remove_topic_sub_configs = MagicMock()
        self._resync_topic_subscriptions = MagicMock()

        # Two AMQP channels, each with its own connector, as in the real amqp_api
        self.channel_config_1 = {'service_name': 'original.service.1'}
        self.channel_config_2 = {'service_name': 'original.service.2'}

        connector_1 = MagicMock()
        connector_1.channels = {'channel.1': self.channel_config_1}

        connector_2 = MagicMock()
        connector_2.channels = {'channel.2': self.channel_config_2}

        self.amqp_api = MagicMock()
        self.amqp_api.connectors = {
            'channel.1': connector_1,
            'channel.2': connector_2,
        }

# ################################################################################################################################
# ################################################################################################################################

def _make_topic_row(name:'str', opaque:'dict | None') -> 'SimpleNamespace':
    """ Builds an object that looks like a PubSubTopic ODB row.
    """
    opaque1 = dumps(opaque) if opaque is not None else None
    return SimpleNamespace(name=name, opaque1=opaque1)

# ################################################################################################################################

def _make_amqp_msg(topic_name:'str', channel_name:'str'='', exchange:'str'='my.exchange') -> 'Bunch':
    """ Builds a TOPIC_CREATE-like config event message for an AMQP topic.
    """
    msg = Bunch()
    msg.topic_name = topic_name
    msg.backend_type = PubSub.Backend_Type.AMQP
    msg.amqp_outconn_name = 'my.outconn'
    msg.amqp_exchange = exchange
    msg.amqp_routing_key = topic_name
    msg.amqp_channel_name = channel_name
    return msg

# ################################################################################################################################
# ################################################################################################################################

class TestSyncPubSubTopics(unittest.TestCase):
    """ Item 18 - _sync_pubsub_topics keeps only AMQP topics from opaque1.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

# ################################################################################################################################

    def _set_odb_rows(self, rows:'list') -> 'None':
        session = MagicMock()
        session.query.return_value.filter.return_value.all.return_value = rows
        self.stub.server.odb.session.return_value = session

# ################################################################################################################################

    def test_sync_keeps_only_amqp_topics(self) -> 'None':

        amqp_opaque = {
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': 'my.outconn',
            'amqp_exchange': 'my.exchange',
            'amqp_routing_key': 'topic.amqp',
            'amqp_channel_name': '',
        }

        builtin_opaque = {
            'backend_type': PubSub.Backend_Type.Builtin,
            'amqp_outconn_name': '',
            'amqp_exchange': '',
            'amqp_routing_key': '',
            'amqp_channel_name': '',
        }

        rows = [
            _make_topic_row('topic.amqp', amqp_opaque),
            _make_topic_row('topic.builtin', builtin_opaque),
            _make_topic_row('topic.no.opaque', None),
            _make_topic_row('topic.opaque.no.backend', {'some_other_attr': 'value'}),
        ]
        self._set_odb_rows(rows)

        self.stub._sync_pubsub_topics()

        # Only the AMQP topic has a registry entry ..
        self.assertEqual(list(self.stub._topic_backends), ['topic.amqp'])

        # .. and its config was carried over from opaque1.
        entry = self.stub._topic_backends['topic.amqp']

        self.assertEqual(entry['backend_type'], PubSub.Backend_Type.AMQP)
        self.assertEqual(entry['amqp_outconn_name'], 'my.outconn')
        self.assertEqual(entry['amqp_exchange'], 'my.exchange')
        self.assertEqual(entry['amqp_routing_key'], 'topic.amqp')
        self.assertEqual(entry['amqp_channel_name'], '')

# ################################################################################################################################

    def test_sync_applies_channel_override(self) -> 'None':

        amqp_opaque = {
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': 'my.outconn',
            'amqp_exchange': 'my.exchange',
            'amqp_routing_key': 'topic.amqp',
            'amqp_channel_name': 'channel.1',
        }

        self._set_odb_rows([_make_topic_row('topic.amqp', amqp_opaque)])

        self.stub._sync_pubsub_topics()

        # The channel now dispatches to the bridge and the original is remembered
        self.assertEqual(self.stub.channel_config_1['service_name'], _pubsub_amqp_bridge_service)

        entry = self.stub._topic_backends['topic.amqp']
        self.assertEqual(entry['original_service_name'], 'original.service.1')

# ################################################################################################################################
# ################################################################################################################################

class TestTopicCreateHandler(unittest.TestCase):
    """ Item 19 - TOPIC_CREATE adds a registry entry and applies the channel override.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

# ################################################################################################################################

    def test_create_adds_entry_and_overrides_channel(self) -> 'None':

        msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')

        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(msg)

        # The registry entry is in place ..
        entry = self.stub._topic_backends['topic.amqp']

        self.assertEqual(entry['backend_type'], PubSub.Backend_Type.AMQP)
        self.assertEqual(entry['amqp_outconn_name'], 'my.outconn')
        self.assertEqual(entry['amqp_exchange'], 'my.exchange')
        self.assertEqual(entry['amqp_channel_name'], 'channel.1')

        # .. the channel dispatches to the bridge ..
        self.assertEqual(self.stub.channel_config_1['service_name'], _pubsub_amqp_bridge_service)

        # .. and the original service name is remembered.
        self.assertEqual(entry['original_service_name'], 'original.service.1')

# ################################################################################################################################

    def test_create_without_channel_does_not_touch_channels(self) -> 'None':

        msg = _make_amqp_msg('topic.amqp', channel_name='')

        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(msg)

        self.assertIn('topic.amqp', self.stub._topic_backends)
        self.assertEqual(self.stub.channel_config_1['service_name'], 'original.service.1')
        self.assertEqual(self.stub.channel_config_2['service_name'], 'original.service.2')

# ################################################################################################################################
# ################################################################################################################################

class TestTopicEditHandler(unittest.TestCase):
    """ Item 20 - TOPIC_EDIT updates the entry and moves the channel override.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        # Start from an AMQP topic that overrides channel.1
        create_msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')
        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(create_msg)

# ################################################################################################################################

    def _make_edit_msg(self, **kwargs:'str') -> 'Bunch':
        msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')
        msg.old_topic_name = 'topic.amqp'
        msg.new_topic_name = 'topic.amqp'
        msg.old_backend_type = PubSub.Backend_Type.AMQP
        msg.old_amqp_channel_name = 'channel.1'

        for key, value in kwargs.items():
            msg[key] = value

        return msg

# ################################################################################################################################

    def test_edit_updates_entry_in_place(self) -> 'None':

        msg = self._make_edit_msg(amqp_exchange='new.exchange', amqp_routing_key='new.key')

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        entry = self.stub._topic_backends['topic.amqp']

        self.assertEqual(entry['amqp_exchange'], 'new.exchange')
        self.assertEqual(entry['amqp_routing_key'], 'new.key')

        # The channel is still overridden and the original is still remembered
        self.assertEqual(self.stub.channel_config_1['service_name'], _pubsub_amqp_bridge_service)
        self.assertEqual(entry['original_service_name'], 'original.service.1')

# ################################################################################################################################

    def test_edit_moves_override_to_another_channel(self) -> 'None':

        msg = self._make_edit_msg(amqp_channel_name='channel.2')

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        # The first channel got its original service back ..
        self.assertEqual(self.stub.channel_config_1['service_name'], 'original.service.1')

        # .. and the second one is now overridden.
        self.assertEqual(self.stub.channel_config_2['service_name'], _pubsub_amqp_bridge_service)

        entry = self.stub._topic_backends['topic.amqp']
        self.assertEqual(entry['amqp_channel_name'], 'channel.2')
        self.assertEqual(entry['original_service_name'], 'original.service.2')

# ################################################################################################################################

    def test_edit_to_builtin_removes_entry_and_restores_channel(self) -> 'None':

        msg = self._make_edit_msg(
            backend_type=PubSub.Backend_Type.Builtin,
            amqp_outconn_name='',
            amqp_exchange='',
            amqp_routing_key='',
            amqp_channel_name='',
        )

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        # The registry no longer knows the topic ..
        self.assertNotIn('topic.amqp', self.stub._topic_backends)

        # .. and the channel got its original service back.
        self.assertEqual(self.stub.channel_config_1['service_name'], 'original.service.1')

# ################################################################################################################################

    def test_edit_rename_moves_entry_to_new_name(self) -> 'None':

        msg = self._make_edit_msg()
        msg.new_topic_name = 'topic.amqp.renamed'

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        self.assertNotIn('topic.amqp', self.stub._topic_backends)
        self.assertIn('topic.amqp.renamed', self.stub._topic_backends)

        # The channel stays overridden throughout
        self.assertEqual(self.stub.channel_config_1['service_name'], _pubsub_amqp_bridge_service)

# ################################################################################################################################
# ################################################################################################################################

class TestTopicDeleteHandler(unittest.TestCase):
    """ Item 21 - TOPIC_DELETE removes the entry and restores the channel.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        create_msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')
        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(create_msg)

# ################################################################################################################################

    def test_delete_removes_entry_and_restores_channel(self) -> 'None':

        msg = Bunch()
        msg.topic_name = 'topic.amqp'

        self.stub.on_config_event_PUBSUB_TOPIC_DELETE(msg)

        self.assertNotIn('topic.amqp', self.stub._topic_backends)
        self.assertEqual(self.stub.channel_config_1['service_name'], 'original.service.1')

# ################################################################################################################################

    def test_delete_of_builtin_topic_is_a_noop_for_the_registry(self) -> 'None':

        msg = Bunch()
        msg.topic_name = 'topic.builtin'

        self.stub.on_config_event_PUBSUB_TOPIC_DELETE(msg)

        # The AMQP topic's entry and override are untouched
        self.assertIn('topic.amqp', self.stub._topic_backends)
        self.assertEqual(self.stub.channel_config_1['service_name'], _pubsub_amqp_bridge_service)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
