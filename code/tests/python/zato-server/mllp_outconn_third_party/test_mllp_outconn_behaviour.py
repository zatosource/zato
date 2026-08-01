# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import time

# Zato
from zato.common.hl7.mllp.circuit_breaker import CircuitBreaker, CircuitState
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.retry import RetryEngine

# Zato - the suite's own parts
from _outconn_api import create_outconn, send, send_one, wait_until_ready
from _outconn_messages import build_adt_a01, Control_Id_Marker, get_msh_field
from _outconn_receivers import build_receiver, next_delivery, wait_for_deliveries, Receiver_Hl7apy

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import OutconnEnvironment
    from zato.common.typing_ import any_, anylist

    any_ = any_
    anylist = anylist
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

# How long the retry test waits between attempts, and the most it will wait. Both are small so that
# a handful of attempts takes a second rather than the half-hour the defaults would come to.
_Retry_Backoff_Base = 0.2
_Retry_Backoff_Cap  = 1.0

# How many attempts the retry test allows past the first one - enough to outlast the listener being
# down and to leave room for one more after it comes back
_Retry_Max_Retries = 6

# What the retry test multiplies the wait by each time, which is what makes the backoff a backoff
_Retry_Backoff_Multiplier = 2.0

# The retry test takes the jitter out, because what it asserts is the delay the settings promise and
# jitter is by definition what makes a delay something other than what was promised. That the jitter
# stays inside its own percentage is asserted separately, where the delays are computed rather than
# waited through.
_Retry_No_Jitter = 0

# The jitter the computed-delay check holds the engine to, as a percentage of the delay
_Jitter_Percent = 10

# How many delays the computed-delay check looks at, one per attempt
_Jitter_Attempt_Count = 5

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

# How long the retry test waits before starting the listener again, in seconds. It is longer than
# the first two backoff delays together and shorter than all of them, so that the send fails a few
# times and then succeeds rather than either succeeding at once or running out of attempts.
_Restart_After = 0.7

# ################################################################################################################################
# ################################################################################################################################

def _build_client(port:'int') -> 'HL7MLLPClient':
    """ Builds the client Zato's own outgoing connections send through, pointed at one of this
    suite's listeners. The tests below that drive the retry engine and the circuit breaker use it
    directly, because what they are about is what happens around a send rather than inside one.
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

class TestOutconnRetries:
    """ The retry engine an outgoing connection carries the settings for, driven against a listener
    that goes down and comes back on the address its senders know. What it wraps is the same client
    a connection sends through, so what is under test here is the real thing over a real socket.
    """

# ################################################################################################################################

    def test_a_send_succeeds_once_the_listener_is_back(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ The listener is stopped, a send is started against it, and the listener comes back
        while the engine is between attempts. The message goes through on the attempt after that,
        and the engine reports how many attempts it took.
        """
        receiver = build_receiver(Receiver_Hl7apy)
        receiver.start()

        # The port is the listener's own and it keeps it across a stop and a start, which is what
        # makes a sender that never learns of the outage possible at all
        port = receiver.port
        receiver.stop()

        client = _build_client(port)
        control_id = 'RETRY-0001'
        message = build_adt_a01(control_id).encode('utf8')

        dead_letters:'anylist' = []

        def _send(payload:'bytes') -> 'any_':
            return client.send(payload, control_id)

        def _to_dead_letter(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            dead_letters.append((error_text, retry_count))

        engine = RetryEngine(
            _send,
            _to_dead_letter,
            max_retries=_Retry_Max_Retries,
            backoff_base=_Retry_Backoff_Base,
            backoff_multiplier=_Retry_Backoff_Multiplier,
            backoff_cap=_Retry_Backoff_Cap,
            jitter_percent=_Retry_No_Jitter,
        )

        # The listener comes back while the engine is waiting between attempts, which is the outage
        # a retry engine is there for - short, and over before anybody was told about it
        restart_timer = _start_after(receiver.start, _Restart_After)

        try:
            result = engine.send_with_retry(message)
        finally:
            restart_timer.join()
            receiver.stop()

        assert result.is_sent
        assert not result.sent_to_dlq
        assert not dead_letters

        # It took more than one attempt, which is what says the engine did the waiting rather than
        # the listener having been there all along
        assert result.retry_count >= 1
        assert result.retry_count <= _Retry_Max_Retries

        # .. and the listener's own record shows the message that finally got through
        wait_for_deliveries(receiver, 1)
        assert get_msh_field(receiver.deliveries[0].text, 10) == control_id

# ################################################################################################################################

    def test_a_listener_that_never_comes_back_ends_in_the_dead_letter_queue(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ Every attempt the settings allow is made, each after the wait the settings promise, and
        then the message is handed to the dead-letter queue rather than tried forever.
        """
        receiver = build_receiver(Receiver_Hl7apy)
        receiver.start()

        port = receiver.port
        receiver.stop()

        client = _build_client(port)
        control_id = 'RETRY-0002'
        message = build_adt_a01(control_id).encode('utf8')

        dead_letters:'anylist' = []
        attempt_times:'anylist' = []

        def _send(payload:'bytes') -> 'any_':
            attempt_times.append(time.monotonic())
            return client.send(payload, control_id)

        def _to_dead_letter(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            dead_letters.append((error_text, retry_count))

        # Two retries is enough to see the waits growing without the test taking any longer over it
        max_retries = 2

        engine = RetryEngine(
            _send,
            _to_dead_letter,
            max_retries=max_retries,
            backoff_base=_Retry_Backoff_Base,
            backoff_multiplier=_Retry_Backoff_Multiplier,
            backoff_cap=_Retry_Backoff_Cap,
            jitter_percent=_Retry_No_Jitter,
        )

        result = engine.send_with_retry(message)

        assert not result.is_sent
        assert result.sent_to_dlq
        assert len(dead_letters) == 1

        # The first attempt plus every retry the settings allowed
        assert len(attempt_times) == max_retries + 1

        # .. and each wait was the one the settings promised, doubling as it went
        for index in range(1, len(attempt_times)):

            waited = attempt_times[index] - attempt_times[index - 1]
            promised = _Retry_Backoff_Base * (_Retry_Backoff_Multiplier ** (index - 1))

            assert waited >= promised

# ################################################################################################################################

    def test_the_backoff_stays_inside_its_jitter_and_under_its_cap(
        self,
        outconn_environment:'OutconnEnvironment',
    ) -> 'None':
        """ The delays the engine computes grow by the multiplier, stay inside the jitter they were
        given and never cross the cap. Asserting on the computed delays rather than on waits is what
        keeps a test of the cap from taking as long as the cap.
        """
        def _send(payload:'bytes') -> 'None':
            pass

        def _to_dead_letter(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            pass

        engine = RetryEngine(
            _send,
            _to_dead_letter,
            backoff_base=_Retry_Backoff_Base,
            backoff_multiplier=_Retry_Backoff_Multiplier,
            backoff_cap=_Retry_Backoff_Cap,
            jitter_percent=_Jitter_Percent,
        )

        jitter_fraction = _Jitter_Percent / 100.0

        for attempt in range(1, _Jitter_Attempt_Count + 1):

            delay = engine._compute_delay(attempt)

            uncapped = _Retry_Backoff_Base * (_Retry_Backoff_Multiplier ** (attempt - 1))
            expected = min(uncapped, _Retry_Backoff_Cap)

            assert delay >= expected * (1 - jitter_fraction)
            assert delay <= expected * (1 + jitter_fraction)

            # The cap holds however far along the attempts have got, jitter included
            assert delay <= _Retry_Backoff_Cap * (1 + jitter_fraction)

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

def _start_after(action:'any_', delay:'float') -> 'any_':
    """ Runs something once, after a wait, on a thread of its own. It is how a listener is brought
    back while a send is already under way against it.
    """
    def _run() -> 'None':
        time.sleep(delay)
        action()

    out = threading.Thread(target=_run, daemon=True)
    out.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
