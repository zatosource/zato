# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Three-state health over a monitored endpoint - an MLLP channel, an outgoing connection,
# a trigger source such as a mailbox poll - anything with a connection, an error rate
# and an expectation of activity. Green means healthy, amber means degraded (connected
# but erroring, backlogged or going quiet), red means down or dead. Transitions
# toward the worse are immediate, transitions back require clearing the threshold
# by a margin, so an indicator hovering around a threshold never flaps.

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

class HealthState:
    Green = 'green'
    Amber = 'amber'
    Red   = 'red'

# ################################################################################################################################

# How the states compare - a bigger number is a worse condition
_severity = {
    HealthState.Green: 0,
    HealthState.Amber: 1,
    HealthState.Red:   2,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HealthThresholds:
    """ When a monitored endpoint counts as degraded or down. All the values
    are per-endpoint configuration - these defaults are a starting point, not policy.
    """

    # The error-rate share that makes the endpoint degraded, then down
    error_rate_amber: float = 0.10
    error_rate_red: float = 0.50

    # How long a silent feed counts as going quiet, then dead.
    # Zero disables silence checking - not every endpoint expects steady traffic.
    silence_amber_seconds: float = 300.0
    silence_red_seconds: float = 900.0

    # A growing backlog is degradation even when nothing errors.
    # Zero disables backlog checking.
    backlog_amber: int = 100

    # That many consecutive negative acknowledgments mean a degraded feed.
    # Zero disables streak checking.
    nack_streak_amber: int = 5

    # How far below a threshold a metric must fall before the state improves -
    # the hysteresis lag that keeps the indicator from flapping.
    clear_margin: float = 0.2

# ################################################################################################################################

@dataclass
class EndpointMetrics:
    """ What one endpoint reports about itself - the shape health derivation runs over.
    """
    is_connected: bool = True
    error_rate: float = 0.0
    silence_seconds: float = 0.0
    backlog: int = 0
    nack_streak: int = 0

# ################################################################################################################################
# ################################################################################################################################

def derive_health(metrics:'EndpointMetrics', thresholds:'HealthThresholds', scale:'float'=1.0) -> 'str':
    """ Derives the raw health state of one endpoint from its metrics. The scale tightens
    the thresholds during hysteresis checks - a state may only improve once its metrics
    clear the scaled-down thresholds, not merely dip below the plain ones.
    """

    # A disconnected endpoint is down, whatever its other metrics say
    if not metrics.is_connected:
        return HealthState.Red

    # The red conditions - erroring heavily or silent for far too long
    if metrics.error_rate >= thresholds.error_rate_red * scale:
        return HealthState.Red

    if thresholds.silence_red_seconds:
        if metrics.silence_seconds >= thresholds.silence_red_seconds * scale:
            return HealthState.Red

    # The amber conditions - connected but degraded, which pure up/down misses
    if metrics.error_rate >= thresholds.error_rate_amber * scale:
        return HealthState.Amber

    if thresholds.silence_amber_seconds:
        if metrics.silence_seconds >= thresholds.silence_amber_seconds * scale:
            return HealthState.Amber

    if thresholds.backlog_amber:
        if metrics.backlog >= thresholds.backlog_amber * scale:
            return HealthState.Amber

    if thresholds.nack_streak_amber:
        if metrics.nack_streak >= thresholds.nack_streak_amber * scale:
            return HealthState.Amber

    return HealthState.Green

# ################################################################################################################################
# ################################################################################################################################

class EndpointHealth:
    """ The health indicator of one monitored endpoint - it remembers its current state
    and applies hysteresis on the way back to a better one.
    """

    def __init__(self, thresholds:'HealthThresholds | None'=None) -> 'None':

        if thresholds is None:
            thresholds = HealthThresholds()

        self.thresholds = thresholds
        self.state = HealthState.Green

# ################################################################################################################################

    def update(self, metrics:'EndpointMetrics') -> 'str':
        """ Feeds one round of metrics in and returns the resulting state.
        """
        raw_state = derive_health(metrics, self.thresholds)

        raw_severity = _severity[raw_state]
        current_severity = _severity[self.state]

        # A worsening condition surfaces immediately ..
        if raw_severity >= current_severity:
            self.state = raw_state

        # .. while an improvement must clear the tightened thresholds first,
        # so a metric hovering right at a threshold never makes the indicator flap.
        else:
            clear_scale = 1.0 - self.thresholds.clear_margin
            self.state = derive_health(metrics, self.thresholds, scale=clear_scale)

        return self.state

# ################################################################################################################################
# ################################################################################################################################
