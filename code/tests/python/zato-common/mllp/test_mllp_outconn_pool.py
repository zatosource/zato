# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
import gevent
from gevent import sleep

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.hl7.mllp.ack import AckResult
from zato.common.typing_ import cast_
from zato.server.connection.facade import HL7MLLPInvoker, MLLPFacade
from zato.server.connection.queue import ConnectionQueue
from zato.server.generic.api.outconn_hl7_mllp import OutconnHL7MLLPWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

    any_ = any_
    strdict = strdict

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'outgoing.mllp.pool'

# How long one send holds its pooled connection
_send_duration = 0.3

# How long after the first send the next one arrives
_arrival_gap = 0.1

# ################################################################################################################################
# ################################################################################################################################

class _PooledConnection:
    """ Stands in for a pooled _HL7MLLPConnection - each send and each ping holds it for a while.
    """
    def __init__(self) -> 'None':
        self.sends_in_flight = 0
        self.most_sends_in_flight = 0

# ################################################################################################################################

    def _hold(self) -> 'None':
        self.sends_in_flight += 1
        self.most_sends_in_flight = max(self.most_sends_in_flight, self.sends_in_flight)
        sleep(_send_duration)
        self.sends_in_flight -= 1

# ################################################################################################################################

    def invoke(self, data:'str', cid:'str'='', needs_audit:'bool'=True, needs_retry:'bool'=True) -> 'AckResult':
        self._hold()

        out = AckResult()
        out.ack_code = 'AA'
        out.is_accepted = True
        out.ack_text = f'MSA|AA|{data}'

        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        self._hold()

# ################################################################################################################################
# ################################################################################################################################

def _build_pool(pooled:'_PooledConnection') -> 'ConnectionQueue':
    server = cast_('any_', None)
    out = ConnectionQueue(server, True, 1, 30, 1, _conn_name, 'HL7 MLLP', '127.0.0.1:2575', None, needs_spawn=False)
    _ = out.put_client(pooled)

    return out

# ################################################################################################################################

def _build_container(pool:'ConnectionQueue', is_active:'bool') -> 'strdict':
    wrapper = Bunch(client=pool, use_queue=False, config=Bunch(name=_conn_name, is_active=is_active))
    out = {_conn_name: Bunch(conn=wrapper, is_active=is_active)}

    return out

# ################################################################################################################################

def _build_facade(container:'strdict') -> 'MLLPFacade':
    config_manager = cast_('any_', Bunch(outconn_hl7_mllp=container))

    out = MLLPFacade()
    out.init('test-cid', config_manager)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingPool:

    def test_a_send_that_finds_every_pooled_connection_in_use_waits_for_one(self) -> 'None':

        pooled = _PooledConnection()
        container = _build_container(_build_pool(pooled), True)
        invoker = HL7MLLPInvoker(_conn_name, 'test-cid', container)

        def send(data:'str') -> 'AckResult':
            out = cast_('AckResult', invoker.send(data, needs_audit=False))
            return out

        first = gevent.spawn(send, 'MSH|first')
        sleep(_arrival_gap)
        second = gevent.spawn(send, 'MSH|second')

        _ = gevent.joinall([first, second], raise_error=True)

        first_ack = cast_('AckResult', first.value)
        second_ack = cast_('AckResult', second.value)

        assert first_ack.ack_text == 'MSA|AA|MSH|first'
        assert second_ack.ack_text == 'MSA|AA|MSH|second'

        # One pooled connection, so the sends went one after another
        assert pooled.most_sends_in_flight == 1

# ################################################################################################################################

    def test_a_ping_that_finds_every_pooled_connection_in_use_waits_for_one(self) -> 'None':

        pooled = _PooledConnection()
        container = _build_container(_build_pool(pooled), True)
        invoker = HL7MLLPInvoker(_conn_name, 'test-cid', container)

        def send(data:'str') -> 'AckResult':
            out = cast_('AckResult', invoker.send(data, needs_audit=False))
            return out

        first = gevent.spawn(send, 'MSH|first')
        sleep(_arrival_gap)
        second = gevent.spawn(invoker.ping)

        _ = gevent.joinall([first, second], raise_error=True)

        assert pooled.most_sends_in_flight == 1

# ################################################################################################################################

    def test_a_delivery_from_the_queue_that_finds_every_pooled_connection_in_use_waits_for_one(self) -> 'None':

        pooled = _PooledConnection()
        pool = _build_pool(pooled)

        wrapper = OutconnHL7MLLPWrapper.__new__(OutconnHL7MLLPWrapper)
        wrapper.client = pool

        container = _build_container(pool, True)
        invoker = HL7MLLPInvoker(_conn_name, 'test-cid', container)

        def send(data:'str') -> 'AckResult':
            out = cast_('AckResult', invoker.send(data, needs_audit=False))
            return out

        def deliver(data:'str') -> 'AckResult':
            out = wrapper.send_from_queue('test-cid', {'data': data})
            return out

        first = gevent.spawn(send, 'MSH|first')
        sleep(_arrival_gap)
        second = gevent.spawn(deliver, 'MSH|queued')

        _ = gevent.joinall([first, second], raise_error=True)

        queued_ack = cast_('AckResult', second.value)

        assert queued_ack.ack_text == 'MSA|AA|MSH|queued'
        assert pooled.most_sends_in_flight == 1

# ################################################################################################################################

    def test_an_active_connection_is_looked_up(self) -> 'None':

        container = _build_container(_build_pool(_PooledConnection()), True)
        facade = _build_facade(container)

        invoker = facade[_conn_name]
        assert invoker.to_dict() == {'conn_name': _conn_name}

# ################################################################################################################################

    def test_an_inactive_connection_cannot_be_looked_up(self) -> 'None':

        container = _build_container(_build_pool(_PooledConnection()), False)
        facade = _build_facade(container)

        with pytest.raises(Exception) as context:
            _ = facade[_conn_name]

        message = str(context.value)
        assert _conn_name in message
        assert 'inactive' in message

# ################################################################################################################################

    def test_a_connection_that_does_not_exist_cannot_be_looked_up(self) -> 'None':

        facade = _build_facade({})

        with pytest.raises(KeyError):
            _ = facade[_conn_name]

# ################################################################################################################################
# ################################################################################################################################
