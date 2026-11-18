# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from pubsub_rest.monitor import Limits
from pubsub_rest.runner import run_for
from pubsub_rest.suite import TrafficRun
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer
    from pubsub_rest.traffic import Traffic
    from zato.common.typing_ import any_, anydict, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics that the administration works on, as the setup of the suite names them.
_cleared_topic = 'stability.admin.0000'
_deleted_topic = 'stability.admin.0001'
_renamed_topic = 'stability.admin.0002'
_new_topic_name = 'stability.admin.renamed'
_unsubscribed_topic = 'stability.admin.0003'

# The live queues of the traffic that are cleared - those of a pull partner and of a push subscriber of the broadcast topic.
_live_partner_index = 1
_live_push_index = 0

# How long a live queue is left to fill before it is cleared, and how long a delivery in progress
# is given to complete once its queue was paused, in seconds.
_fill_seconds = 1
_settle_seconds = 1

# How long the administration and, afterwards, the backlog of the traffic may take, in seconds.
_drain_seconds = 600

# By how much the publication rate of this suite is lower than that of the production profile,
# and how many publications the traffic makes in total.
_rate_divisor = 20
_publish_limit = 50

# ################################################################################################################################
# ################################################################################################################################

class _Administration:
    """ Runs the administrative operations one after another during the traffic and records how long each took.
    """
    def __init__(self, server:'PubSubServer', traffic:'Traffic') -> 'None':
        self.server = server
        self.traffic = traffic
        self.admin_topics:'anydict' = server.properties['admin_topics']

        self.durations:'anydict' = {}
        self.results:'anydict' = {}
        self.is_done = False

    def _timed(self, name:'str', function:'callable_', *args:'any_') -> 'any_':
        started = monotonic()
        out = function(*args)
        self.durations[name] = monotonic() - started
        return out

    def _clear_queue(self, sub_key:'str') -> 'int':
        response = self.server.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        out = response['cleared_count']
        return out

    def _delete_topic(self, topic_name:'str') -> 'None':
        topic_id = self.server.get_topic_id(topic_name)
        _ = self.server.invoke('zato.pubsub.topic.delete', {'id': topic_id})

    def _rename_topic(self, topic_name:'str', new_name:'str') -> 'None':
        topic_id = self.server.get_topic_id(topic_name)
        _ = self.server.invoke('zato.pubsub.topic.edit', {'id': topic_id, 'name': new_name, 'is_active': True})

    def _unsubscribe(self, sec_name:'str', topic_name:'str') -> 'None':
        _ = self.server.invoke('zato.pubsub.subscription.unsubscribe', {'sec_name': sec_name, 'topic_name_list': [topic_name]})

    def run(self) -> 'None':

        # Operations on the seeded queues and topics ..
        cleared_sub_key = self.admin_topics[_cleared_topic]
        self.results['clear_queue'] = self._timed('clear_queue', self._clear_queue, cleared_sub_key)

        _ = self._timed('delete_topic', self._delete_topic, _deleted_topic)
        _ = self._timed('rename_topic', self._rename_topic, _renamed_topic, _new_topic_name)
        _ = self._timed('unsubscribe', self._unsubscribe, _unsubscribed_topic, _unsubscribed_topic)

        # .. a pull partner's queue that filled up while it was away ..
        live_partner_sub_key = self.traffic.partner_sub_keys[_live_partner_index]

        self.traffic.paused_sub_keys.add(live_partner_sub_key)
        sleep(_fill_seconds)

        cleared_count = self._timed('clear_live_pull_queue', self._clear_queue, live_partner_sub_key)
        self.traffic.extra_deliveries -= cleared_count
        self.results['clear_live_pull_queue'] = cleared_count

        self.traffic.paused_sub_keys.discard(live_partner_sub_key)

        # .. and a push subscriber's queue, paused for the time of the operation.
        live_push_sub_key = self.traffic.broadcast_sub_keys[_live_push_index]

        self.server.set_delivery_active(live_push_sub_key, False)
        sleep(_settle_seconds)

        cleared_count = self._timed('clear_live_push_queue', self._clear_queue, live_push_sub_key)
        self.traffic.extra_deliveries -= cleared_count
        self.results['clear_live_push_queue'] = cleared_count

        self.server.set_delivery_active(live_push_sub_key, True)

        self.is_done = True

# ################################################################################################################################
# ################################################################################################################################

def test_admin_load(server:'PubSubServer') -> 'None':
    """ Clearing queues, deleting and renaming topics, and unsubscribing, during the traffic, which stays within its limits,
    while each operation has its full effect and the counts equal the rows.
    """
    messages_per_topic = server.properties['messages_per_topic']

    measurement = start_measurement(server.get_client(), server.get_database())
    run = TrafficRun(server, Limits())

    traffic = run.traffic
    traffic.set_rate(traffic.rate / _rate_divisor)
    traffic.publish_limit = _publish_limit

    # The publications end at their limit, after which there is no rate to keep.
    run.monitor.checks_rate = False

    administration = _Administration(server, traffic)

    # The partner whose queue is cleared waits on purpose, so its latency is not measured.
    traffic.unmeasured_sub_keys.add(traffic.partner_sub_keys[_live_partner_index])

    try:
        run.start()

        greenlet = spawn(administration.run)
        run_for(run.monitor, _drain_seconds, is_done=greenlet.ready)
        _ = greenlet.get()

        drained_seconds = run.drain(_drain_seconds)

    finally:
        run.stop()

    failures:'strlist' = []

    # Each operation had its full effect ..
    if administration.results['clear_queue'] != messages_per_topic:
        failures.append(f'Cleared {administration.results["clear_queue"]} of {messages_per_topic}')

    deleted_rows = server.get_topic_rows(_deleted_topic)
    for name in ('messages', 'deliveries', 'subscriptions'):
        if deleted_rows[name]:
            failures.append(f'{deleted_rows[name]} {name} left of {_deleted_topic}')

    renamed_rows = server.get_topic_rows(_renamed_topic)
    for name in ('messages', 'deliveries'):
        if renamed_rows[name]:
            failures.append(f'{renamed_rows[name]} {name} left of {_renamed_topic}')

    new_name_rows = server.get_topic_rows(_new_topic_name)
    if new_name_rows['deliveries'] != messages_per_topic:
        failures.append(f'{new_name_rows["deliveries"]} deliveries of {_new_topic_name}, expected {messages_per_topic}')

    unsubscribed_rows = server.get_topic_rows(_unsubscribed_topic)
    if unsubscribed_rows['deliveries']:
        failures.append(f'{unsubscribed_rows["deliveries"]} deliveries left of {_unsubscribed_topic}')

    figures = run.get_figures({
        'messages_per_topic': messages_per_topic,
        'seed_seconds': server.properties['seed_seconds'],
        'durations': administration.durations,
        'results': administration.results,
        'drain_seconds': drained_seconds,
    })
    _ = report_result(measurement, 'pubsub-admin-load', figures)

    monitor = run.monitor

    # .. and the traffic was not disturbed.
    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert administration.is_done
    assert not failures, failures
    assert not monitor.get_failures(), monitor.get_failures()
    assert not server.get_count_mismatches(), server.get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
