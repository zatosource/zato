# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Zato
from common import measure_median_seconds, Max_Operation_Seconds
from seeding import count_rows, seed_backlog
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The full backlog - 1,000 queues with 1,000 pending messages each,
# one million enqueued messages in total
_full_topic_count = 1000
_full_messages_per_topic = 1000

# The small backlog the flatness comparison starts from
_small_topic_count = 10
_small_messages_per_topic = 1000

# The deep queue for clear-queue timing - one subscriber with a pending copy
# of the first that many topics, i.e. 100,000 deliveries
_deep_sub_key = 'zpsk.perf.deep'
_deep_topic_count = 100

# How many times each measured operation runs for its median
_iterations = 10

# The fetch median at the full backlog may be at most this many times the small-backlog one -
# generous enough for measurement noise, far below the hundredfold jump of a lost index
_flatness_factor = 10

# Measurement noise floor - medians below this are treated as this value in the flatness
# ratio so microsecond-level jitter cannot fail the comparison
_flatness_floor_seconds = 0.002

# How long the deep clear-queue may take in total - 20 bounded batches of 5,000
_deep_clear_max_seconds = 30

# How many (sub_key, topic) pairs one dashboard page asks depths for
_depth_pair_count = 50

# How many topics the timeline and publisher-count calls cover
_stats_topic_count = 10

# ################################################################################################################################
# ################################################################################################################################

def _measure_fetch_median(backend:'SQLPubSubBackend', topic_count:'int') -> 'float':
    """ Returns the median duration of a fetch across subscribers spread over the backlog.
    """
    state = {'topic_index': 0}

    def fetch_next() -> 'anylist':
        sub_key = f'zpsk.perf.{state["topic_index"] % topic_count:04d}'
        state['topic_index'] += 1

        out = backend.fetch_messages(sub_key)

        assert out, f'Expected a non-empty fetch for {sub_key}'
        return out

    out = measure_median_seconds(fetch_next, _iterations)
    return out

# ################################################################################################################################

def _assert_operations_within_bound(backend:'SQLPubSubBackend') -> 'None':
    """ Every user-visible operation must complete within the 50 ms bound
    at the full one-million-message backlog.
    """

    # Publishing into a subscribed topic - one outside the deep subscriber's range
    # so the deep queue's size stays exactly as seeded ..
    state = {'counter': 0}

    def publish_one() -> 'None':
        state['counter'] += 1
        _ = backend.publish('perf.topic.0500', f'backlog-publish-{state["counter"]}')

    # .. fetching and acknowledging a batch ..
    def fetch_and_ack() -> 'None':
        messages = backend.fetch_messages('zpsk.perf.0001')

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])

        _ = backend.ack_messages('zpsk.perf.0001', msg_ids)

    # .. the queue depths of one dashboard page ..
    depth_pairs:'anylist' = []

    for topic_index in range(_depth_pair_count):
        depth_pairs.append((f'zpsk.perf.{topic_index:04d}', f'perf.topic.{topic_index:04d}'))

    def depths_page() -> 'None':
        depths = backend.get_pending_depths(depth_pairs)
        assert len(depths) == _depth_pair_count

    # .. the per-state totals of one queue ..
    def total_counts() -> 'None':
        assert backend.get_total_count('zpsk.perf.0002', 'perf.topic.0002', 'pending') > 0
        assert backend.get_total_count('zpsk.perf.0002', 'perf.topic.0002', 'all') > 0
        _ = backend.get_total_count('zpsk.perf.0002', 'perf.topic.0002', 'delivered')

    # .. one browse page ..
    def browse_page() -> 'None':
        messages, _ignored = backend.browse_messages('perf.topic.0003', 'zpsk.perf.0003', state='pending')
        assert messages

    # .. one message detail lookup ..
    def message_details() -> 'None':
        details = backend.get_message_details('perf.topic.0004', 'zpsm.perf.0004.0')
        assert details is not None

    # .. and the dashboard statistics over a set of topics.
    stats_topics:'strlist' = []

    for topic_index in range(_stats_topic_count):
        stats_topics.append(f'perf.topic.{topic_index:04d}')

    def publish_timeline() -> 'None':
        timeline = backend.get_publish_timeline(stats_topics)
        assert timeline

    def distinct_publishers() -> 'None':
        assert backend.count_distinct_publishers(stats_topics) > 0

    operations = {
        'publish': publish_one,
        'fetch_and_ack': fetch_and_ack,
        'get_pending_depths': depths_page,
        'get_total_count': total_counts,
        'browse_messages': browse_page,
        'get_message_details': message_details,
        'get_publish_timeline': publish_timeline,
        'count_distinct_publishers': distinct_publishers,
    }

    for name, operation in operations.items():
        median = measure_median_seconds(operation, _iterations)

        assert median <= Max_Operation_Seconds, \
            f'{name} too slow at the full backlog: median {median * 1000:.1f} ms'

# ################################################################################################################################

def run_backlog_scenario() -> 'None':
    """ The one-million-message backlog - every user-visible operation stays under 50 ms,
    fetch latency stays flat between a 10k and a 1M backlog (the index regression detector)
    and clearing a 100,000-message queue completes within its batch bounds.
    """
    backend = SQLPubSubBackend()

    # First the small backlog - the baseline of the flatness comparison ..
    seed_seconds = seed_backlog(topic_count=_small_topic_count, messages_per_topic=_small_messages_per_topic)
    print(f'Seeded {_small_topic_count * _small_messages_per_topic} messages in {seed_seconds:.2f}s')

    small_fetch_median = _measure_fetch_median(backend, _small_topic_count)

    # .. then the full backlog, with the deep subscriber on top ..
    seed_seconds = seed_backlog(
        topic_count=_full_topic_count,
        messages_per_topic=_full_messages_per_topic,
        deep_sub_key=_deep_sub_key,
        deep_topic_count=_deep_topic_count,
    )
    print(f'Seeded {_full_topic_count * _full_messages_per_topic} messages in {seed_seconds:.2f}s')

    assert count_rows('pubsub_message') == _full_topic_count * _full_messages_per_topic

    # .. fetch latency must not grow with the backlog - a lost index shows up
    # .. as a hundredfold jump, far beyond this bound ..
    full_fetch_median = _measure_fetch_median(backend, _full_topic_count)

    if small_fetch_median < _flatness_floor_seconds:
        small_fetch_median = _flatness_floor_seconds

    assert full_fetch_median <= Max_Operation_Seconds, \
        f'Fetch too slow at the full backlog: median {full_fetch_median * 1000:.1f} ms'

    assert full_fetch_median <= small_fetch_median * _flatness_factor, \
        f'Fetch latency grew with the backlog: {small_fetch_median * 1000:.1f} ms -> {full_fetch_median * 1000:.1f} ms'

    # .. every user-visible operation stays within its bound at the full backlog ..
    _assert_operations_within_bound(backend)

    # .. and the deep queue clears completely, in bounded batches, within its time budget.
    start = monotonic()
    result = backend.clear_queue(_deep_sub_key)
    elapsed = monotonic() - start

    expected_deep_count = _deep_topic_count * _full_messages_per_topic

    assert result['cleared_count'] == expected_deep_count, \
        f'Expected {expected_deep_count} cleared, got {result["cleared_count"]}'

    assert elapsed <= _deep_clear_max_seconds, f'Deep clear-queue too slow: {elapsed:.1f}s'

    print(f'Cleared {expected_deep_count} deliveries in {elapsed:.2f}s')

# ################################################################################################################################
# ################################################################################################################################
