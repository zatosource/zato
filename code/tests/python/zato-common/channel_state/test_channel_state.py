# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import time

# Zato
from zato.common.hl7.mllp.state import ChannelState

# ################################################################################################################################
# ################################################################################################################################

# The channel all the tests run over
_channel_name = 'hl7.test.channel'

# How far past the rolling window the expiry checks look, in seconds
_past_the_window = 400.0

# ################################################################################################################################
# ################################################################################################################################

class TestCounters:

    def test_a_new_channel_starts_at_zero(self) -> 'None':
        state = ChannelState(_channel_name)

        assert state.name == _channel_name
        assert state.received == 0
        assert state.acked == 0
        assert state.nacked == 0
        assert state.errored == 0
        assert state.nack_streak == 0
        assert state.is_listening is False

# ################################################################################################################################

    def test_the_hooks_count_what_happened(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_message_received()
        state.on_message_received()
        state.on_ack_sent()
        state.on_nack_sent()
        state.on_error()

        assert state.received == 2
        assert state.acked == 1
        assert state.nacked == 1
        assert state.errored == 1

# ################################################################################################################################

    def test_a_positive_ack_ends_a_nack_streak(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_nack_sent()
        state.on_nack_sent()
        state.on_nack_sent()

        assert state.nack_streak == 3

        state.on_ack_sent()

        assert state.nack_streak == 0

        # The lifetime counters keep the history the streak forgot
        assert state.nacked == 3
        assert state.acked == 1

# ################################################################################################################################
# ################################################################################################################################

class TestListener:

    def test_the_listener_condition_is_tracked(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_listener_up()

        assert state.is_listening is True
        assert state.listening_since_iso != ''

        state.on_listener_down()

        assert state.is_listening is False

# ################################################################################################################################
# ################################################################################################################################

class TestErrorRate:

    def test_an_empty_window_is_a_zero_rate(self) -> 'None':
        state = ChannelState(_channel_name)

        assert state.get_error_rate() == 0.0

# ################################################################################################################################

    def test_the_rate_is_the_share_of_failures(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_ack_sent()
        state.on_ack_sent()
        state.on_ack_sent()
        state.on_nack_sent()

        assert state.get_error_rate() == 0.25

# ################################################################################################################################

    def test_a_frame_error_counts_toward_the_rate(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_ack_sent()
        state.on_error()

        assert state.get_error_rate() == 0.5

# ################################################################################################################################

    def test_old_outcomes_fall_out_of_the_window(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_nack_sent()
        state.on_nack_sent()

        # Looking at the window from far enough in the future, everything expired
        future = time() + _past_the_window

        assert state.get_error_rate(now=future) == 0.0

# ################################################################################################################################
# ################################################################################################################################

class TestSilence:

    def test_a_channel_that_never_received_is_not_silent(self) -> 'None':

        # A feed that never started is a configuration matter, not a dead feed
        state = ChannelState(_channel_name)

        assert state.get_silence_seconds() == 0.0

# ################################################################################################################################

    def test_silence_is_measured_from_the_last_message(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_message_received()

        later = state.last_message_time + 42.0

        assert state.get_silence_seconds(now=later) == 42.0

# ################################################################################################################################
# ################################################################################################################################

class TestMetrics:

    def test_the_metrics_carry_the_state_in_the_generic_shape(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_listener_up()
        state.on_message_received()
        state.on_ack_sent()
        state.on_nack_sent()
        state.on_nack_sent()

        later = state.last_message_time + 10.0
        metrics = state.get_metrics(now=later)

        assert metrics.is_connected is True
        assert metrics.error_rate == 2 / 3
        assert metrics.silence_seconds == 10.0
        assert metrics.nack_streak == 2

# ################################################################################################################################
# ################################################################################################################################

class TestStateContract:

    def test_the_state_contract_has_everything_the_dashboard_renders(self) -> 'None':
        state = ChannelState(_channel_name)

        state.on_listener_up()
        state.on_message_received()
        state.on_ack_sent()

        contract = state.get_state()

        assert contract['name'] == _channel_name
        assert contract['is_listening'] is True
        assert contract['listening_since_iso'] != ''
        assert contract['received'] == 1
        assert contract['acked'] == 1
        assert contract['nacked'] == 0
        assert contract['errored'] == 0
        assert contract['nack_streak'] == 0
        assert contract['last_message_time_iso'] != ''
        assert contract['error_rate'] == 0.0
        assert contract['silence_seconds'] >= 0.0

# ################################################################################################################################
# ################################################################################################################################
