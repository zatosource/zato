# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep, spawn

# SQLAlchemy
from sqlalchemy import text

# Zato
from monitor import Limits, Monitor
from runner import get_count_mismatches, get_duration, get_report_path, run_for, start_cleanup_process, \
    stop_cleanup_process
from seeding import seed_backlog
from traffic import get_traffic_profile, Traffic
from zato.common.pubsub.sql.config import get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How many messages each of the topics that the administration works on holds,
# unless Zato_Test_Admin_Messages says otherwise.
_messages_per_topic = 250_000

# The topics and subscribers that the administration works on, named as the seeding names them.
_admin_topic_prefix = 'stability.admin'
_admin_sub_key_prefix = 'zpsk.stability.admin'
_admin_topic_count = 4

_cleared_sub_key = 'zpsk.stability.admin.0000'
_deleted_topic = 'stability.admin.0001'
_renamed_topic = 'stability.admin.0002'
_new_topic_name = 'stability.admin.renamed'
_unsubscribed_sub_key = 'zpsk.stability.admin.0003'
_unsubscribed_topic = 'stability.admin.0003'

# The live queues of the traffic that are cleared - a pull partner and a push subscriber of the broadcast topic.
_live_partner_sub_key = 'zpsk.stability.partner.0001'
_live_push_sub_key = 'zpsk.stability.broadcast.0000'

# How long the traffic runs before the administration starts and after it is over, in seconds.
_warm_up_seconds = 3 * 60
_cool_down_seconds = 3 * 60

# How long a live queue is left to fill before it is cleared, and how long a delivery in progress
# is given to complete once its queue was paused, in seconds.
_fill_seconds = 60
_settle_seconds = 5

# How long the backlog of the traffic may take to drain after the API clients stop, in seconds.
_drain_seconds = 600

# How often the cleanup process sweeps, in seconds.
_cleanup_interval_seconds = 60

_message_count_query = text('select count(*) from pubsub_message where topic_name = :topic_name')
_delivery_count_query = text('select count(*) from pubsub_delivery where topic_name = :topic_name')
_sub_count_query = text('select count(*) from pubsub_topic_sub where topic_name = :topic_name')

# ################################################################################################################################
# ################################################################################################################################

def _count(query:'any_', topic_name:'str') -> 'int':
    with get_pubsub_engine().connect() as connection:
        out = connection.execute(query, {'topic_name': topic_name}).scalar_one()
    return out

# ################################################################################################################################
# ################################################################################################################################

class _Administration:
    """ Runs the administrative operations one after another during the traffic and records how long each took.
    """
    def __init__(self, traffic:'Traffic') -> 'None':
        self.traffic = traffic
        self.backend = traffic.backend
        self.durations:'anydict' = {}
        self.results:'anydict' = {}
        self.is_done = False

    def _timed(self, name:'str', function:'callable_', *args:'any_') -> 'any_':
        started = monotonic()
        out = function(*args)
        self.durations[name] = monotonic() - started
        return out

    def run(self) -> 'None':

        # Operations on the queues and topics at production volumes ..
        result = self._timed('clear_queue', self.backend.clear_queue, _cleared_sub_key)
        self.results['clear_queue'] = result['cleared_count']

        _ = self._timed('delete_topic', self.backend.delete_topic, _deleted_topic)
        _ = self._timed('rename_topic', self.backend.rename_topic, _renamed_topic, _new_topic_name)
        _ = self._timed('unsubscribe', self.backend.unsubscribe, _unsubscribed_sub_key, _unsubscribed_topic)

        # .. a pull partner's queue that filled up while it was away ..
        self.traffic.paused_sub_keys.add(_live_partner_sub_key)
        sleep(_fill_seconds)

        result = self._timed('clear_live_pull_queue', self.backend.clear_queue, _live_partner_sub_key)
        self.traffic.extra_deliveries -= result['cleared_count']
        self.results['clear_live_pull_queue'] = result['cleared_count']

        self.traffic.paused_sub_keys.discard(_live_partner_sub_key)

        # .. and a push subscriber's queue, paused for the time of the operation.
        push_delivery = self.traffic.push_delivery

        push_delivery.pause_sub_key(_live_push_sub_key)
        sleep(_settle_seconds)

        result = self._timed('clear_live_push_queue', self.backend.clear_queue, _live_push_sub_key)
        self.traffic.extra_deliveries -= result['cleared_count']
        self.results['clear_live_push_queue'] = result['cleared_count']

        push_delivery.resume_sub_key(_live_push_sub_key)

        self.is_done = True

# ################################################################################################################################
# ################################################################################################################################

def test_admin_load(stability_env:'strstrdict') -> 'None':
    """ Clearing queues, deleting and renaming topics, and unsubscribing, at production volumes during the traffic,
    which stays within its limits, while each operation has its full effect and the counts equal the rows.
    """
    messages_per_topic = get_duration('Zato_Test_Admin_Messages', _messages_per_topic)

    seed_seconds = seed_backlog(
        topic_count=_admin_topic_count,
        messages_per_topic=messages_per_topic,
        topic_prefix=_admin_topic_prefix,
        sub_key_prefix=_admin_sub_key_prefix,
    )
    print(f'Seeded {_admin_topic_count * messages_per_topic} messages in {seed_seconds:.0f}s', flush=True)

    traffic = Traffic(get_traffic_profile())
    traffic.backend.take_over()
    traffic.subscribe_all()

    # The partner whose queue is cleared waits on purpose, so its latency is not measured.
    traffic.unmeasured_sub_keys.add(_live_partner_sub_key)

    cleanup = start_cleanup_process(_cleanup_interval_seconds)
    monitor = Monitor(traffic, Limits(), get_report_path('admin-load'), 'admin-load')
    administration = _Administration(traffic)

    try:
        traffic.start()
        monitor.start()

        run_for(monitor, _warm_up_seconds)

        greenlet = spawn(administration.run)
        run_for(monitor, _drain_seconds, is_done=greenlet.ready)
        _ = greenlet.get()

        run_for(monitor, _cool_down_seconds)

        traffic.stop_publishing()
        monitor.checks_rate = False
        _ = traffic.wait_until_drained(_drain_seconds)

    finally:
        monitor.stop()
        traffic.stop()
        stop_cleanup_process(cleanup)

    print(f'Administration durations: {administration.durations}', flush=True)
    print(f'Administration results: {administration.results}', flush=True)

    failures:'strlist' = []

    # Each operation had its full effect ..
    if administration.results['clear_queue'] != messages_per_topic:
        failures.append(f'Cleared {administration.results["clear_queue"]} of {messages_per_topic}')

    for query, topic_name in ((_message_count_query, _deleted_topic), (_delivery_count_query, _deleted_topic),
            (_sub_count_query, _deleted_topic), (_message_count_query, _renamed_topic),
            (_delivery_count_query, _renamed_topic), (_delivery_count_query, _unsubscribed_topic)):
        count = _count(query, topic_name)
        if count:
            failures.append(f'{count} rows left of {topic_name}')

    renamed_count = _count(_delivery_count_query, _new_topic_name)
    if renamed_count != messages_per_topic:
        failures.append(f'{renamed_count} deliveries of {_new_topic_name}, expected {messages_per_topic}')

    # .. and the traffic was not disturbed.
    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert administration.is_done
    assert not failures, failures
    assert not monitor.get_failures(), monitor.get_failures()
    assert not get_count_mismatches(), get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
