# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One run of the production traffic against the server of a suite - the traffic, its per-minute measurement
# and the cleanup process, started and stopped together.

# Zato
from pubsub_rest.monitor import Monitor
from pubsub_rest.runner import start_cleanup_process, stop_cleanup_process
from pubsub_rest.traffic import get_traffic_profile, Traffic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from pubsub_rest.definition import Definition
    from pubsub_rest.monitor import Limits
    from pubsub_rest.server import PubSubServer
    from pubsub_rest.traffic import TrafficProfile
    from zato.common.typing_ import anydict

    process = Popen[bytes]

# ################################################################################################################################
# ################################################################################################################################

def define_traffic(server:'PubSubServer', definition:'Definition', profile:'TrafficProfile | None'=None) -> 'Traffic':
    """ Adds the production traffic to the definition of the server of a suite, with the production profile
    unless another one is given.
    """
    if profile is None:
        profile = get_traffic_profile()

    out = Traffic(profile)
    out.define(server, definition)

    server.traffic = out
    return out

# ################################################################################################################################
# ################################################################################################################################

class TrafficRun:
    """ The traffic of the server of a suite, measured each minute, with the cleanup process running alongside.
    """

    def __init__(self, server:'PubSubServer', limits:'Limits') -> 'None':
        self.server = server
        self.traffic = server.get_traffic()
        self.monitor = Monitor(server, self.traffic, limits)
        self.cleanup:'process | None' = None

# ################################################################################################################################

    def start(self, starts_cleanup:'bool'=True) -> 'None':
        if starts_cleanup:
            self.cleanup = start_cleanup_process()

        self.traffic.start()
        self.monitor.start()

# ################################################################################################################################

    def drain(self, timeout_seconds:'float') -> 'float':
        """ Stops the API clients and waits until every publication was delivered, returning how long it took, in seconds.
        """
        self.traffic.stop_publishing()
        self.monitor.checks_rate = False

        out = self.traffic.wait_until_drained(timeout_seconds)
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        self.monitor.stop()
        self.traffic.stop()

        if self.cleanup:
            stop_cleanup_process(self.cleanup)

# ################################################################################################################################

    def get_figures(self, figures:'anydict') -> 'anydict':
        """ The figures of the run - those of the suite, the totals of the traffic and the measurements of each minute.
        """
        out = dict(figures)
        out['totals'] = self.traffic.get_totals()
        out['minutes'] = self.monitor.get_figures()

        return out

# ################################################################################################################################
# ################################################################################################################################
