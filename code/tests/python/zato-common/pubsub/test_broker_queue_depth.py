# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import PubSub
from zato.common.ext.bunch import Bunch
from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The config manager's mixins are loaded by path, so the broker read is patched where the method actually looks it up
_amqp_mixin_globals = ConfigManager.amqp_get_channel_queue_depth.__globals__

def _patch_queue_depth(**kwargs:'any_') -> 'any_':
    out = patch.dict(_amqp_mixin_globals, {'get_queue_depth': MagicMock(**kwargs)})
    return out

# ################################################################################################################################
# ################################################################################################################################

_topic_broker = 'zato.out.to.rest.orders'
_topic_builtin = 'zato.out.to.rest.invoices'
_topic_unreachable = 'zato.out.to.rest.reports'

_sub_key_broker = 'zpsk.out.rest.1'
_sub_key_builtin = 'zpsk.out.rest.2'
_sub_key_unreachable = 'zpsk.out.rest.3'

_channel_broker = 'channel.orders'
_channel_unreachable = 'channel.reports'

_encrypted_password = 'gAAAA-encrypted'
_decrypted_password = 'plain-password'

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManagerStub:
    """ Runs the real depth-reading code of ConfigManager with the broker and the configuration mocked out.
    """

    # The real methods under test, bound to this stub
    _get_broker_pending_counts = ConfigManager._get_broker_pending_counts
    amqp_get_channel_queue_depth = ConfigManager.amqp_get_channel_queue_depth
    get_pubsub_topic_backend = ConfigManager.get_pubsub_topic_backend

    def __init__(self) -> 'None':
        self.server = MagicMock()
        self.server.decrypt.return_value = _decrypted_password

        self._topic_backends = {
            _topic_broker: _make_backend(_channel_broker),
            _topic_unreachable: _make_backend(_channel_unreachable),
        }

        self.config_store = MagicMock()
        self.config_store.channel_amqp.get_config_list.return_value = [
            _make_channel(_channel_broker, 'orders.queue'),
            _make_channel(_channel_unreachable, 'reports.queue'),
        ]

# ################################################################################################################################
# ################################################################################################################################

def _make_backend(channel_name:'str') -> 'dict':
    out = {
        'backend_type': PubSub.Backend_Type.AMQP,
        'amqp_outconn_name': 'broker.outconn',
        'amqp_exchange': 'zato.out',
        'amqp_routing_key': channel_name,
        'amqp_channel_name': channel_name,
    }
    return out

# ################################################################################################################################

def _make_channel(name:'str', queue:'str') -> 'Bunch':
    out = Bunch()
    out.name = name
    out.address = 'amqp://127.0.0.1:5672//'
    out.username = 'guest'
    out.password = _encrypted_password
    out.queue = queue
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBrokerPendingCounts(unittest.TestCase):

    def setUp(self) -> 'None':
        self.config_manager = _ConfigManagerStub()

# ################################################################################################################################

    def test_a_broker_backed_queue_takes_its_depth_from_the_broker(self) -> 'None':
        """ The queue of a topic that lives in a broker is asked of the broker, through the channel that reads it back,
        with the channel's own address, credentials and queue, and a built-in topic is left to the database.
        """
        restored_topics = {
            _sub_key_broker: _topic_broker,
            _sub_key_builtin: _topic_builtin,
        }

        with _patch_queue_depth(return_value=4):
            out = self.config_manager._get_broker_pending_counts(restored_topics)
            get_queue_depth = _amqp_mixin_globals['get_queue_depth']

        self.assertEqual(out, {_sub_key_broker: 4})

        get_queue_depth.assert_called_once_with(
            _channel_broker, 'amqp://127.0.0.1:5672//', 'guest', _decrypted_password, 'orders.queue')

        # The password reaches the broker decrypted, the configuration keeps it as it was
        self.config_manager.server.decrypt.assert_called_once_with(_encrypted_password)

# ################################################################################################################################

    def test_a_broker_that_cannot_be_reached_stops_the_startup(self) -> 'None':
        """ A broker that does not answer leaves the depth of its queue unknown, and a queue whose depth is not known
        would let a direct send overtake the messages the broker holds, so the failure propagates out of the restore.
        """
        restored_topics = {
            _sub_key_unreachable: _topic_unreachable,
            _sub_key_broker: _topic_broker,
        }

        def read_depth(name:'str', *args:'str') -> 'int':
            if name == _channel_unreachable:
                raise ConnectionRefusedError('The broker is down')
            return 2

        with _patch_queue_depth(side_effect=read_depth):
            with self.assertRaises(ConnectionRefusedError):
                _ = self.config_manager._get_broker_pending_counts(restored_topics)

# ################################################################################################################################

    def test_a_channel_that_does_not_exist_is_an_error(self) -> 'None':
        """ A topic registry pointing at a channel the configuration has not got is a mistake worth a clear message.
        """
        with self.assertRaises(ValueError) as ctx:
            _ = self.config_manager.amqp_get_channel_queue_depth('channel.missing')

        self.assertIn('channel.missing', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
