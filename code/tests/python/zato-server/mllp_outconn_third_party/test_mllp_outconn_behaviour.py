# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.hl7.mllp.circuit_breaker import CircuitBreaker, CircuitState
from zato.common.hl7.mllp.client import HL7MLLPClient

# Zato - the suite's own parts
from _outconn_api import create_outconn, send, send_one, wait_until_ready
from _outconn_messages import build_adt_a01, Control_Id_Marker, get_msh_field
from _outconn_receivers import build_receiver, next_delivery, wait_for_deliveries, Receiver_Hl7apy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import OutconnEnvironment
    from zato.common.typing_ import any_

    any_ = any_
    OutconnEnvironment = OutconnEnvironment

# ################################################################################################################################
# ################################################################################################################################

# The framing every listener in this suite reads and writes
_Start_Sequence = b'\x0b'
_End_Sequence   = b'\x1c\x0d'

# What the loopback address is called here
_Host = '127.0.0.1'

# How many messages the concurrency test sends at once, and the pool it sends them through - the
# two are the same number so that every message has a connection of its own to go out on
_Concurrent_Send_Count = 8

# How long a listener that is being waited on takes over each message, in seconds
_Slow_Receiver_Delay = 2.0

# The receive timeout a send is given against that listener when it is meant to give up, and when
# it is meant to wait, both in milliseconds
_Timeout_Below_The_Delay = 500
_Timeout_Above_The_Delay = 10000

# What the circuit breaker is held to - a failure rate over half of a window, a window long enough
# that a run of failures inside one test lands in the same one, and a reset short enough that a
# test can wait it out
_Breaker_Threshold_Percent = 50
_Breaker_Window_Seconds    = 60.0
_Breaker_Reset_Seconds     = 1.0

# How many sends the breaker is put through before it is expected to have opened
_Breaker_Failure_Count = 4

# How long a send against a listener that is there waits for its answer, in seconds
_Receive_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

def _build_client(port:'int') -> 'HL7MLLPClient':
    """ Builds the client Zato's own outgoing connections send through, pointed at one of this
    suite's listeners. The test below that drives the circuit breaker uses it directly, because
    what it is about is what happens around a send rather than inside one.
    """
    out = HL7MLLPClient(_Host, port, _Start_Sequence, _End_Sequence, receive_timeout=_Receive_Timeout)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnRejection:
    """ A listener that answers but refuses. The two codes it refuses with mean different things -
    one says the message will never be taken and the other says not now - and a sender has to be
    able to tell them apart, because one of them is worth trying again and the other never is.
    """

# ################################################################################################################################

    def test_an_application_error_is_not_reported_as_a_successful_send(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ AE comes back as a message that was sent and refused, with retrying ruled out.
        """
        client = outconn_environment.client

        receiver = build_receiver(Receiver_Hl7apy, ack_code='AE')
        receiver.start()

        try:
            name = create_outconn(outconn_environment, 'reject-ae', receiver.address)

            wait_until_ready(client, name)
            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01('REJECT-AE'))

            # The message reached the listener and was answered, so the send itself worked ..
            assert result['is_sent']

            # .. and what came back was a refusal rather than an acceptance
            assert result['ack_code'] == 'AE'
            assert not result['is_accepted']
            assert not result['should_retry']
            assert 'Application error (AE)' in result['error_text']

            arrived = next_delivery(receiver, delivered_before)
            assert get_msh_field(arrived, 10) == 'REJECT-AE'

        finally:
            receiver.stop()

# ################################################################################################################################

    def test_an_application_reject_asks_to_be_tried_again(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ AR comes back as a refusal too, except one that says the message is worth sending again,
        which is the difference the retry engine reads its decision out of.
        """
        client = outconn_environment.client

        receiver = build_receiver(Receiver_Hl7apy, ack_code='AR')
        receiver.start()

        try:
            name = create_outconn(outconn_environment, 'reject-ar', receiver.address)

            wait_until_ready(client, name)

            result = send_one(client, name, build_adt_a01('REJECT-AR'))

            assert result['is_sent']
            assert result['ack_code'] == 'AR'
            assert not result['is_accepted']
            assert result['should_retry']
            assert 'Application reject (AR)' in result['error_text']

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnConcurrency:
    """ What a pool does when everything in it is in use at once. Each message has to come back with
    the answer to itself rather than with the answer to whichever of the others finished first.
    """

# ################################################################################################################################

    def test_every_concurrent_send_gets_its_own_answer(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ Eight messages go out at once through a pool of eight, and every acknowledgment names
        the message it answers. A crossed reply would be a message reporting somebody else's id.
        """
        client = outconn_environment.client

        control_ids = []

        for index in range(_Concurrent_Send_Count):
            control_ids.append(f'CONC-{index:04}')

        name = create_outconn(outconn_environment, 'concurrent', receiver.address, pool_size=_Concurrent_Send_Count)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        # The message carries a marker where its control id goes, and the send service puts one
        # of the ids above in its place for each of the messages it sends
        template = build_adt_a01(Control_Id_Marker)
        results = send(client, name, template, _Concurrent_Send_Count, control_ids)

        assert len(results) == _Concurrent_Send_Count

        for index, result in enumerate(results):

            control_id = control_ids[index]

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']

            # The acknowledgment names this message rather than one of the seven beside it.
            # The client checks the same thing, an acknowledgment naming another message never
            # being counted as an acceptance, so this holds twice over.
            assert f'MSA|AA|{control_id}' in result['ack_text']

        # .. and the listener took delivery of all eight
        wait_for_deliveries(receiver, delivered_before + _Concurrent_Send_Count)

        arrived_ids = set()

        for delivery in receiver.deliveries[delivered_before:]:
            arrived_ids.add(get_msh_field(delivery.text, 10))

        assert arrived_ids == set(control_ids)

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnSlowReceiver:
    """ A listener that takes its time. The receive timeout is what says how long a sender waits for
    an answer, and a listener slower than that is what the field calls an outage.
    """

# ################################################################################################################################

    def test_a_send_gives_up_on_a_listener_slower_than_its_timeout(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ The listener answers, only later than the sender was told to wait, so the send fails
        even though nothing about the listener is wrong.
        """
        client = outconn_environment.client

        receiver = build_receiver(Receiver_Hl7apy, delay=_Slow_Receiver_Delay)
        receiver.start()

        try:
            config = {'recv_timeout': _Timeout_Below_The_Delay}

            name = create_outconn(outconn_environment, 'slow-strict', receiver.address, **config)

            delivered_before = len(receiver.deliveries)

            start = time.monotonic()
            result = send_one(client, name, build_adt_a01('SLOW-0001'))
            elapsed = time.monotonic() - start

            assert not result['is_sent']
            assert 'Timed out waiting for ACK' in result['error_text']

            # The send gave up when it was told to rather than waiting the listener out
            assert elapsed < _Slow_Receiver_Delay

            # .. and the message did arrive all the same, which is what makes this a timeout
            # rather than a failure to deliver - the listener has it, the sender does not know
            wait_for_deliveries(receiver, delivered_before + 1)

        finally:
            receiver.stop()

# ################################################################################################################################

    def test_a_send_waits_out_a_listener_inside_its_timeout(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ The same listener, with the sender told to wait longer than it takes, and the send goes
        through - a slow listener is only a problem against a timeout that is shorter than it.
        """
        client = outconn_environment.client

        receiver = build_receiver(Receiver_Hl7apy, delay=_Slow_Receiver_Delay)
        receiver.start()

        try:
            config = {'recv_timeout': _Timeout_Above_The_Delay}

            name = create_outconn(outconn_environment, 'slow-patient', receiver.address, **config)

            result = send_one(client, name, build_adt_a01('SLOW-0002'))

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']
            assert 'MSA|AA|SLOW-0002' in result['ack_text']

            # The send did wait, rather than the listener having answered early
            assert result['elapsed_ms'] >= _Slow_Receiver_Delay * 1000

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnCircuitBreaker:
    """ The circuit breaker an outgoing connection carries the settings for. A listener that is down
    is worth a few attempts and then worth leaving alone, because the attempts cost the sender more
    than they cost whatever is not answering them.
    """

# ################################################################################################################################

    def test_the_circuit_opens_on_a_listener_that_is_down_and_closes_when_it_is_back(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ Enough failures inside the window cross the threshold and sending stops. Once the reset
        has passed one trial message is allowed through, and its success closes the circuit again.
        """
        receiver = build_receiver(Receiver_Hl7apy)
        receiver.start()

        port = receiver.port
        receiver.stop()

        client = _build_client(port)

        breaker = CircuitBreaker(
            failure_threshold_percent=_Breaker_Threshold_Percent,
            window_seconds=_Breaker_Window_Seconds,
            reset_seconds=_Breaker_Reset_Seconds,
        )

        attempted_count = 0

        # Every send fails, because there is nothing at the far end to answer one
        for index in range(_Breaker_Failure_Count):

            if not breaker.can_execute():
                break

            attempted_count += 1

            try:
                _ = client.send(build_adt_a01(f'BREAK-{index:04}').encode('utf8'), f'BREAK-{index:04}')
                breaker.record_success()
            except Exception:
                breaker.record_failure()

        # The circuit opened before every send had been tried, which is the whole point of it
        assert breaker.state == CircuitState.Open
        assert attempted_count < _Breaker_Failure_Count

        # .. and while it is open nothing is sent at all
        assert not breaker.can_execute()

        # The listener comes back and the reset passes ..
        receiver.start()

        try:
            time.sleep(_Breaker_Reset_Seconds)

            # .. after which one trial message is allowed through ..
            assert breaker.can_execute()
            assert breaker.state == CircuitState.Half_Open

            control_id = 'BREAK-TRIAL'
            result = client.send(build_adt_a01(control_id).encode('utf8'), control_id)

            assert result.is_accepted
            breaker.record_success()

            # .. and its success is what closes the circuit and lets everything through again
            assert breaker.state == CircuitState.Closed
            assert breaker.can_execute()

            wait_for_deliveries(receiver, 1)
            assert get_msh_field(receiver.deliveries[0].text, 10) == control_id

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################
