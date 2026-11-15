# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module

# gevent
from gevent import sleep

# Zato
from zato.common import worker_slot as worker_slot_module
from zato.common.sdk import SubscribingConnector
from zato.server.generic.api.outconn_sdk import SDKConnectorWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anydict, anylist

    any_ = any_
    anydict = anydict
    anylist = anylist
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Channel_ID = 1

    # The slot of a worker other than the first one
    Other_Slot = 1

# ################################################################################################################################
# ################################################################################################################################

class _RecordingListener:
    """ Records the start of the listener of one channel, in place of ChannelListener.
    """
    started:'anylist' = []

    def __init__(self, server:'any_', config:'anydict') -> 'None':
        self.config = config

    def start(self) -> 'None':
        _RecordingListener.started.append(self.config['id'])

    def stop(self) -> 'None':
        pass

# ################################################################################################################################

class _RecordingConnector(SubscribingConnector):
    """ Records each subscription that the connection makes.
    """
    def __init__(self) -> 'None':
        self.subscribed:'anylist' = []

    def on_started(self, client:'any_') -> 'None':
        self.subscribed.append(client)

# ################################################################################################################################
# ################################################################################################################################

def _start_connection() -> 'tuple[SDKConnectorWrapper, _RecordingConnector, anylist]':
    """ Starts one SDK connection whose connector subscribes, recording the subscriptions and the monitors started.
    """
    connector = _RecordingConnector()
    client = object()
    monitored:'anylist' = []

    def monitor(connector:'any_', client:'any_') -> 'None':
        monitored.append(client)

    wrapper = SDKConnectorWrapper.__new__(SDKConnectorWrapper)
    wrapper._build_connector = lambda: connector # type: ignore[method-assign]
    wrapper._build_client = lambda connector: client # type: ignore[method-assign]
    wrapper._monitor_subscribing = monitor # type: ignore[method-assign]
    wrapper._init_impl()

    # The monitor runs in a greenlet of its own
    sleep(0)

    return wrapper, connector, monitored

# ################################################################################################################################
# ################################################################################################################################

def test_channel_listeners_run_in_the_worker_of_the_first_slot_only(monkeypatch:'MonkeyPatch') -> 'None':

    recv = import_module('zato.server.queue_bridge.recv')
    monkeypatch.setattr(recv, 'ChannelListener', _RecordingListener)
    monkeypatch.setattr(_RecordingListener, 'started', [])

    config = {'id': ModuleCtx.Channel_ID}

    # The worker of another slot starts no listener, neither directly nor through an update ..
    monkeypatch.setattr(worker_slot_module, '_worker_slot', ModuleCtx.Other_Slot)

    other_listeners = recv.ChannelListeners(object())
    other_listeners.start(config)
    other_listeners.update(config)
    other_listeners.sync([config])

    assert _RecordingListener.started == []

    # .. while the worker of the first slot starts it.
    monkeypatch.setattr(worker_slot_module, '_worker_slot', worker_slot_module.ModuleCtx.Singleton_Slot)

    first_listeners = recv.ChannelListeners(object())
    first_listeners.start(config)

    assert _RecordingListener.started == [ModuleCtx.Channel_ID]

# ################################################################################################################################

def test_a_subscribing_connection_subscribes_in_the_worker_of_the_first_slot_only(monkeypatch:'MonkeyPatch') -> 'None':

    # The worker of another slot builds the connection and its client and does not subscribe ..
    monkeypatch.setattr(worker_slot_module, '_worker_slot', ModuleCtx.Other_Slot)

    wrapper, connector, monitored = _start_connection()

    assert wrapper.connector is connector
    assert wrapper.is_connected
    assert connector.subscribed == []
    assert monitored == []

    # .. while the worker of the first slot subscribes and watches the subscription.
    monkeypatch.setattr(worker_slot_module, '_worker_slot', worker_slot_module.ModuleCtx.Singleton_Slot)

    wrapper, connector, monitored = _start_connection()

    assert len(connector.subscribed) == 1
    assert monitored == connector.subscribed

# ################################################################################################################################
# ################################################################################################################################
