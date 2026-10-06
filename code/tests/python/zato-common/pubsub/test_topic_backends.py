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

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManagerStub:
    """ Runs the real topic backend registry code of ConfigManager
    with everything around it mocked out.
    """

    # The real methods under test, bound to this stub
    _read_pubsub_topics = ConfigManager._read_pubsub_topics
    _load_pubsub_topic_backends = ConfigManager._load_pubsub_topic_backends
    _sync_pubsub_topics = ConfigManager._sync_pubsub_topics
    get_pubsub_topic_backend = ConfigManager.get_pubsub_topic_backend
    is_pubsub_amqp_channel = ConfigManager.is_pubsub_amqp_channel
    on_amqp_channel_message = ConfigManager.on_amqp_channel_message
    on_config_event_PUBSUB_TOPIC_CREATE = ConfigManager.on_config_event_PUBSUB_TOPIC_CREATE
    on_config_event_PUBSUB_TOPIC_EDIT = ConfigManager.on_config_event_PUBSUB_TOPIC_EDIT
    on_config_event_PUBSUB_TOPIC_DELETE = ConfigManager.on_config_event_PUBSUB_TOPIC_DELETE
    amqp_stop_all = ConfigManager.amqp_stop_all

    def __init__(self) -> 'None':
        self.server = MagicMock()
        self.config_store = MagicMock()
        self.config_store.pubsub_subs = {}
        self._push_subs = {}
        self._topic_backends = {}

        # These touch the pub/sub backend and push delivery so they are not under test here
        self._remove_topic_sub_configs = MagicMock()
        self._resync_topic_subscriptions = MagicMock()

        # What the dispatch hands the message to once it has decided on the service
        self.invoke = MagicMock()

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

    def assert_channels_untouched(self, test:'unittest.TestCase') -> 'None':
        """ The channels' own configuration is never written to, whatever the topics do.
        """
        test.assertEqual(self.channel_config_1['service_name'], 'original.service.1')
        test.assertEqual(self.channel_config_2['service_name'], 'original.service.2')

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
    msg.is_audit_log_active = True
    return msg

# ################################################################################################################################

def _make_channel_kwargs(channel_name:'str') -> 'dict':
    """ The keyword arguments an AMQP consumer passes along with each message.
    """
    out = {
        'channel': 'amqp',
        'data_format': None,
        'zato_ctx': {
            'zato.channel_item': {
                'id': 1,
                'name': channel_name,
                'is_internal': False,
            },
        },
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLoadPubSubTopicBackends(unittest.TestCase):
    """ _load_pubsub_topic_backends keeps only AMQP topics from opaque1.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

# ################################################################################################################################

    def _set_odb_rows(self, rows:'list') -> 'None':
        session = MagicMock()
        session.query.return_value.filter.return_value.all.return_value = rows
        self.stub.server.odb.session.return_value = session

# ################################################################################################################################

    def test_load_keeps_only_amqp_topics(self) -> 'None':

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

        self.stub._load_pubsub_topic_backends()

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

    def test_load_makes_the_topics_channel_a_pubsub_one(self) -> 'None':

        amqp_opaque = {
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': 'my.outconn',
            'amqp_exchange': 'my.exchange',
            'amqp_routing_key': 'topic.amqp',
            'amqp_channel_name': 'channel.1',
        }

        self._set_odb_rows([_make_topic_row('topic.amqp', amqp_opaque)])

        self.stub._load_pubsub_topic_backends()

        # The first channel is the one the topic reads from, the second is not, and neither config was written to
        self.assertTrue(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.assertFalse(self.stub.is_pubsub_amqp_channel('channel.2'))
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_sync_registers_the_audit_flags_only(self) -> 'None':

        off_opaque = {
            'is_audit_log_active': False,
        }

        payload_opaque = {
            'is_audit_export_payload_active': True,
        }

        rows = [
            _make_topic_row('topic.audit.off', off_opaque),
            _make_topic_row('topic.payload.on', payload_opaque),
            _make_topic_row('topic.plain', {}),
        ]
        self._set_odb_rows(rows)

        self.stub._sync_pubsub_topics()

        backend = self.stub.server.pubsub_backend
        backend.set_topic_audit_flag.assert_called_once_with('topic.audit.off', False)
        backend.set_topic_payload_flag.assert_called_once_with('topic.payload.on', True)

        # The registry is not what the sync is about
        self.assertEqual(self.stub._topic_backends, {})

# ################################################################################################################################
# ################################################################################################################################

class TestAMQPChannelDispatch(unittest.TestCase):
    """ on_amqp_channel_message hands a message to pub/sub if a topic reads from the channel, else to the channel's service.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        create_msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')
        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(create_msg)

# ################################################################################################################################

    def test_a_channel_a_topic_reads_from_dispatches_to_pubsub(self) -> 'None':

        kwargs = _make_channel_kwargs('channel.1')

        _ = self.stub.on_amqp_channel_message('original.service.1', 'body-1', **kwargs)

        self.stub.invoke.assert_called_once_with(_pubsub_amqp_bridge_service, 'body-1', **kwargs)
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_any_other_channel_dispatches_to_its_own_service(self) -> 'None':

        kwargs = _make_channel_kwargs('channel.2')

        _ = self.stub.on_amqp_channel_message('original.service.2', 'body-2', **kwargs)

        self.stub.invoke.assert_called_once_with('original.service.2', 'body-2', **kwargs)
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_the_decision_follows_the_registry_per_message(self) -> 'None':

        kwargs = _make_channel_kwargs('channel.1')

        # The topic is gone, so the next message goes to the channel's own service ..
        delete_msg = Bunch()
        delete_msg.topic_name = 'topic.amqp'
        self.stub.on_config_event_PUBSUB_TOPIC_DELETE(delete_msg)

        _ = self.stub.on_amqp_channel_message('original.service.1', 'body-after-delete', **kwargs)
        self.stub.invoke.assert_called_with('original.service.1', 'body-after-delete', **kwargs)

        # .. and once the topic is back, so is pub/sub.
        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(_make_amqp_msg('topic.amqp', channel_name='channel.1'))

        _ = self.stub.on_amqp_channel_message('original.service.1', 'body-after-create', **kwargs)
        self.stub.invoke.assert_called_with(_pubsub_amqp_bridge_service, 'body-after-create', **kwargs)

        self.stub.assert_channels_untouched(self)

# ################################################################################################################################
# ################################################################################################################################

class TestTopicCreateHandler(unittest.TestCase):
    """ TOPIC_CREATE adds a registry entry.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

# ################################################################################################################################

    def test_create_adds_entry(self) -> 'None':

        msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')

        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(msg)

        entry = self.stub._topic_backends['topic.amqp']

        self.assertEqual(entry['backend_type'], PubSub.Backend_Type.AMQP)
        self.assertEqual(entry['amqp_outconn_name'], 'my.outconn')
        self.assertEqual(entry['amqp_exchange'], 'my.exchange')
        self.assertEqual(entry['amqp_channel_name'], 'channel.1')

        self.assertTrue(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_create_without_channel_makes_no_channel_a_pubsub_one(self) -> 'None':

        msg = _make_amqp_msg('topic.amqp', channel_name='')

        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(msg)

        self.assertIn('topic.amqp', self.stub._topic_backends)
        self.assertFalse(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.assertFalse(self.stub.is_pubsub_amqp_channel('channel.2'))

# ################################################################################################################################
# ################################################################################################################################

class TestTopicEditHandler(unittest.TestCase):
    """ TOPIC_EDIT updates the entry and with it which channel is a pub/sub one.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        # Start from an AMQP topic that reads from channel.1
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

        self.assertTrue(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_edit_moves_the_topic_to_another_channel(self) -> 'None':

        msg = self._make_edit_msg(amqp_channel_name='channel.2')

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        # The first channel is a plain one again and the second one is the topic's now
        self.assertFalse(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.assertTrue(self.stub.is_pubsub_amqp_channel('channel.2'))

        entry = self.stub._topic_backends['topic.amqp']
        self.assertEqual(entry['amqp_channel_name'], 'channel.2')

        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_edit_to_builtin_removes_entry(self) -> 'None':

        msg = self._make_edit_msg(
            backend_type=PubSub.Backend_Type.Builtin,
            amqp_outconn_name='',
            amqp_exchange='',
            amqp_routing_key='',
            amqp_channel_name='',
        )

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        self.assertNotIn('topic.amqp', self.stub._topic_backends)
        self.assertFalse(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_edit_rename_moves_entry_to_new_name(self) -> 'None':

        msg = self._make_edit_msg()
        msg.new_topic_name = 'topic.amqp.renamed'

        self.stub.on_config_event_PUBSUB_TOPIC_EDIT(msg)

        self.assertNotIn('topic.amqp', self.stub._topic_backends)
        self.assertIn('topic.amqp.renamed', self.stub._topic_backends)

        # The channel is the topic's throughout
        self.assertTrue(self.stub.is_pubsub_amqp_channel('channel.1'))

# ################################################################################################################################
# ################################################################################################################################

class TestTopicDeleteHandler(unittest.TestCase):
    """ TOPIC_DELETE removes the entry.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()

        create_msg = _make_amqp_msg('topic.amqp', channel_name='channel.1')
        self.stub.on_config_event_PUBSUB_TOPIC_CREATE(create_msg)

# ################################################################################################################################

    def test_delete_removes_entry(self) -> 'None':

        msg = Bunch()
        msg.topic_name = 'topic.amqp'

        self.stub.on_config_event_PUBSUB_TOPIC_DELETE(msg)

        self.assertNotIn('topic.amqp', self.stub._topic_backends)
        self.assertFalse(self.stub.is_pubsub_amqp_channel('channel.1'))
        self.stub.assert_channels_untouched(self)

# ################################################################################################################################

    def test_delete_of_builtin_topic_is_a_noop_for_the_registry(self) -> 'None':

        msg = Bunch()
        msg.topic_name = 'topic.builtin'

        self.stub.on_config_event_PUBSUB_TOPIC_DELETE(msg)

        self.assertIn('topic.amqp', self.stub._topic_backends)
        self.assertTrue(self.stub.is_pubsub_amqp_channel('channel.1'))

# ################################################################################################################################
# ################################################################################################################################

class TestAMQPStopAll(unittest.TestCase):
    """ amqp_stop_all flags every connector before it waits for any of them and then removes them all.
    """

    def setUp(self) -> 'None':
        self.stub = _ConfigManagerStub()
        self.calls:'list[str]' = []

        for name, connector in self.stub.amqp_api.connectors.items():
            connector.name = name
            connector.request_stop.side_effect = self._record('request_stop', name)

        self.stub.amqp_api.delete.side_effect = self._record_delete

# ################################################################################################################################

    def _record(self, verb:'str', name:'str') -> 'callable_':
        def _inner() -> 'None':
            self.calls.append(f'{verb}:{name}')
        return _inner

# ################################################################################################################################

    def _record_delete(self, name:'str') -> 'None':
        self.calls.append(f'delete:{name}')

# ################################################################################################################################

    def test_every_connector_is_flagged_before_any_is_removed(self) -> 'None':

        self.stub.amqp_stop_all()

        expected = [
            'request_stop:channel.1',
            'request_stop:channel.2',
            'delete:channel.1',
            'delete:channel.2',
        ]

        self.assertEqual(self.calls, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
