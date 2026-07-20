# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep

# humanize
from humanize import intcomma

# Zato
from perf import Progress_Interval_Seconds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_amqp.harness import PubSubAMQPHarness
    from zato.common.typing_ import anydict, callable_

# ################################################################################################################################
# ################################################################################################################################

# What the currently running scenario looks like - the reporter reads the publish
# counter the publishers increment and counts deliveries through the harness.
progress_context:'anydict' = {
    'scenario': 'starting',
    'publish_counters': {'count': 0},
    'harness': None,
}

# How long a wait for an asynchronous condition may take before a scenario fails, in seconds.
Wait_Deadline_Seconds = 300

# How often a wait checks its condition, in seconds.
_wait_poll_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

def set_progress_context(scenario:'str', publish_counters:'anydict', harness:'PubSubAMQPHarness') -> 'None':
    """ Called by every scenario as it starts so the progress line can name it
    and read its publish and delivery counters.
    """
    progress_context['scenario'] = scenario
    progress_context['publish_counters'] = publish_counters
    progress_context['harness'] = harness

# ################################################################################################################################

def _get_delivered_count() -> 'int':
    """ How many push deliveries the current scenario's harness recorded so far.
    """
    harness = progress_context['harness']

    if harness is None:
        return 0

    out = len(harness.server.service_invocations)
    return out

# ################################################################################################################################

def report_progress_forever() -> 'None':
    """ Prints one console line per interval - which scenario runs, what moved
    since the last line and at what rate.
    """
    start = monotonic()

    previous_published = 0
    previous_delivered = 0

    while True:
        sleep(Progress_Interval_Seconds)

        elapsed = monotonic() - start

        published = progress_context['publish_counters']['count']
        delivered = _get_delivered_count()

        # The rates cover the last interval only.
        publish_rate = (published - previous_published) // Progress_Interval_Seconds
        delivery_rate = (delivered - previous_delivered) // Progress_Interval_Seconds

        previous_published = published
        previous_delivered = delivered

        scenario = progress_context['scenario']

        message = f'Progress {elapsed:.0f}s [{scenario}]'
        message += f' published={intcomma(published)} ({intcomma(publish_rate)}/s)'
        message += f' delivered={intcomma(delivered)} ({intcomma(delivery_rate)}/s)'
        print(message, flush=True)

# ################################################################################################################################

def wait_until(condition:'callable_', description:'str') -> 'None':
    """ Waits until an asynchronous condition holds, failing the scenario after the deadline.
    """
    deadline = monotonic() + Wait_Deadline_Seconds

    while not condition():
        if monotonic() > deadline:
            raise Exception(f'Condition not met within {Wait_Deadline_Seconds}s -> {description}')
        sleep(_wait_poll_seconds)

# ################################################################################################################################
# ################################################################################################################################
