# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.monitoring.health import derive_health, EndpointHealth, EndpointMetrics, HealthState, HealthThresholds

# ################################################################################################################################
# ################################################################################################################################

def _metrics(
    *,
    is_connected:'bool'=True,
    error_rate:'float'=0.0,
    silence_seconds:'float'=0.0,
    backlog:'int'=0,
    nack_streak:'int'=0,
    ) -> 'EndpointMetrics':
    """ Builds one round of metrics with everything healthy unless said otherwise.
    """
    out = EndpointMetrics()

    out.is_connected = is_connected
    out.error_rate = error_rate
    out.silence_seconds = silence_seconds
    out.backlog = backlog
    out.nack_streak = nack_streak

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDeriveHealth:

    def test_a_healthy_endpoint_is_green(self) -> 'None':
        assert derive_health(_metrics(), HealthThresholds()) == HealthState.Green

# ################################################################################################################################

    def test_a_disconnected_endpoint_is_red_whatever_else_says(self) -> 'None':
        assert derive_health(_metrics(is_connected=False), HealthThresholds()) == HealthState.Red

# ################################################################################################################################

    def test_heavy_erroring_is_red(self) -> 'None':
        thresholds = HealthThresholds()

        assert derive_health(_metrics(error_rate=0.5), thresholds) == HealthState.Red
        assert derive_health(_metrics(error_rate=0.9), thresholds) == HealthState.Red

# ################################################################################################################################

    def test_a_dead_feed_is_red(self) -> 'None':
        assert derive_health(_metrics(silence_seconds=900.0), HealthThresholds()) == HealthState.Red

# ################################################################################################################################

    def test_moderate_erroring_is_amber(self) -> 'None':

        # Connected but degraded - what a pure up and down check misses
        assert derive_health(_metrics(error_rate=0.2), HealthThresholds()) == HealthState.Amber

# ################################################################################################################################

    def test_a_feed_going_quiet_is_amber(self) -> 'None':
        assert derive_health(_metrics(silence_seconds=400.0), HealthThresholds()) == HealthState.Amber

# ################################################################################################################################

    def test_a_growing_backlog_is_amber_even_without_errors(self) -> 'None':
        assert derive_health(_metrics(backlog=150), HealthThresholds()) == HealthState.Amber

# ################################################################################################################################

    def test_a_nack_streak_is_amber(self) -> 'None':
        assert derive_health(_metrics(nack_streak=5), HealthThresholds()) == HealthState.Amber

# ################################################################################################################################

    def test_a_zero_threshold_disables_its_check(self) -> 'None':

        # Not every endpoint expects steady traffic - a silence threshold of zero
        # means silence never degrades it.
        thresholds = HealthThresholds()
        thresholds.silence_amber_seconds = 0.0
        thresholds.silence_red_seconds = 0.0

        assert derive_health(_metrics(silence_seconds=10_000.0), thresholds) == HealthState.Green

# ################################################################################################################################
# ################################################################################################################################

class TestHysteresis:

    def test_worsening_surfaces_immediately(self) -> 'None':
        health = EndpointHealth()

        assert health.update(_metrics()) == HealthState.Green
        assert health.update(_metrics(error_rate=0.2)) == HealthState.Amber
        assert health.update(_metrics(error_rate=0.6)) == HealthState.Red

# ################################################################################################################################

    def test_improvement_within_the_margin_does_not_flap(self) -> 'None':
        health = EndpointHealth()

        # The endpoint degrades at an error rate of 0.10 ..
        assert health.update(_metrics(error_rate=0.12)) == HealthState.Amber

        # .. dipping just below the threshold is not enough to recover -
        # the metric must clear the margin at 0.08 first, so the indicator
        # hovering around 0.10 never flaps.
        assert health.update(_metrics(error_rate=0.09)) == HealthState.Amber

        # .. while a real improvement clears the margin and the state follows.
        assert health.update(_metrics(error_rate=0.05)) == HealthState.Green

# ################################################################################################################################

    def test_a_disconnect_is_red_at_once_and_a_reconnect_recovers(self) -> 'None':
        health = EndpointHealth()

        assert health.update(_metrics()) == HealthState.Green
        assert health.update(_metrics(is_connected=False)) == HealthState.Red

        # A reconnected endpoint with clean metrics recovers right away -
        # the margin guards metric thresholds, not the connection flag.
        assert health.update(_metrics()) == HealthState.Green

# ################################################################################################################################

    def test_the_thresholds_are_per_endpoint_configuration(self) -> 'None':

        # A channel that expects one message a day tolerates long silence
        thresholds = HealthThresholds()
        thresholds.silence_amber_seconds = 100_000.0
        thresholds.silence_red_seconds = 200_000.0

        health = EndpointHealth(thresholds)

        assert health.update(_metrics(silence_seconds=50_000.0)) == HealthState.Green
        assert health.update(_metrics(silence_seconds=150_000.0)) == HealthState.Amber

# ################################################################################################################################
# ################################################################################################################################
