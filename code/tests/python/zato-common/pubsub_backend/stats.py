# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers all the statistics assertions share.
_topic_1 = 'pubsub.backend.test.stats.1'
_topic_2 = 'pubsub.backend.test.stats.2'
_sub_key_1 = 'zpsk.test.stats.1'
_sub_key_2 = 'zpsk.test.stats.2'

# The publish timeline is bucketed by minute.
_milliseconds_per_minute = 60 * 1000

# ################################################################################################################################
# ################################################################################################################################

def _run_depths_and_counts_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Pending depths and per-state totals reflect publications and acknowledgements.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)
    backend.subscribe(_sub_key_2, _topic_1)
    backend.subscribe(_sub_key_2, _topic_2)

    results = []

    for index in range(3):
        result = backend.publish(_topic_1, f'topic-1-message-{index}')
        results.append(result)

    for index in range(2):
        _ = backend.publish(_topic_2, f'topic-2-message-{index}')

    # The depths sum up each subscriber's requested pairs ..
    pairs = [
        (_sub_key_1, _topic_1),
        (_sub_key_2, _topic_1),
        (_sub_key_2, _topic_2),
    ]
    depths = backend.get_pending_depths(pairs)

    assert depths == {_sub_key_1: 3, _sub_key_2: 5}

    # .. pairs outside the request do not count ..
    depths = backend.get_pending_depths([(_sub_key_2, _topic_2)])
    assert depths == {_sub_key_2: 2}

    # .. a subscriber with nothing pending is still present in the result ..
    depths = backend.get_pending_depths([('zpsk.test.stats.unknown', _topic_1)])
    assert depths == {'zpsk.test.stats.unknown': 0}

    # .. the totals start with everything pending and nothing delivered ..
    assert backend.get_total_count(_sub_key_1, _topic_1, 'all') == 3
    assert backend.get_total_count(_sub_key_1, _topic_1, 'pending') == 3
    assert backend.get_total_count(_sub_key_1, _topic_1, 'delivered') == 0

    # .. an acknowledgement moves one message from pending to delivered ..
    first_result = results[0]
    _ = backend.ack_message(_sub_key_1, first_result.msg_id)

    assert backend.get_total_count(_sub_key_1, _topic_1, 'all') == 3
    assert backend.get_total_count(_sub_key_1, _topic_1, 'pending') == 2
    assert backend.get_total_count(_sub_key_1, _topic_1, 'delivered') == 1

    # .. and an unrecognized state counts nothing.
    assert backend.get_total_count(_sub_key_1, _topic_1, 'no-such-state') == 0

# ################################################################################################################################

def _run_timeline_and_publishers_flow(backend:'SQLPubSubBackend') -> 'None':
    """ The publish timeline buckets by minute and publishers are counted distinctly.
    """
    delete_all_rows()

    for index in range(3):
        _ = backend.publish(_topic_1, f'alice-message-{index}', publisher='alice')

    _ = backend.publish(_topic_2, 'bob-message-1', publisher='bob')
    _ = backend.publish(_topic_2, 'bob-message-2', publisher='bob')

    # One message has no publisher and must not affect the distinct count.
    _ = backend.publish(_topic_2, 'anonymous-message')

    # The timeline covers all the requested topics ..
    timeline = backend.get_publish_timeline([_topic_1, _topic_2])

    total_count = 0

    for entry in timeline:

        # .. each bucket sits exactly on a minute boundary ..
        assert entry['timestamp'] % _milliseconds_per_minute == 0

        total_count += entry['count']

    assert total_count == 6

    # .. no topics means no timeline ..
    assert backend.get_publish_timeline([]) == []

    # .. and the publisher counts are distinct per requested topic set.
    assert backend.count_distinct_publishers([_topic_1, _topic_2]) == 2
    assert backend.count_distinct_publishers([_topic_1]) == 1
    assert backend.count_distinct_publishers([]) == 0

# ################################################################################################################################

def _run_browse_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Browsing pages through a topic by delivery state in both directions.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)

    results = []

    for index in range(5):
        result = backend.publish(_topic_1, f'browse-message-{index}')
        results.append(result)

    # Forward browsing returns the oldest messages first, two pages of two and one of one ..
    page_1, cursor_1 = backend.browse_messages(_topic_1, _sub_key_1, state='pending', page_size=2)

    assert len(page_1) == 2
    assert page_1[0]['msg_id'] == results[0].msg_id
    assert page_1[1]['msg_id'] == results[1].msg_id
    assert cursor_1

    page_2, cursor_2 = backend.browse_messages(_topic_1, _sub_key_1, state='pending', cursor=cursor_1, page_size=2)

    assert len(page_2) == 2
    assert page_2[0]['msg_id'] == results[2].msg_id
    assert cursor_2

    page_3, cursor_3 = backend.browse_messages(_topic_1, _sub_key_1, state='pending', cursor=cursor_2, page_size=2)

    assert len(page_3) == 1
    assert page_3[0]['msg_id'] == results[4].msg_id
    assert cursor_3 == ''

    # .. reverse browsing returns the newest first ..
    reverse_page, _ignored = backend.browse_messages(_topic_1, _sub_key_1, state='pending', page_size=2, reverse=True)

    assert reverse_page[0]['msg_id'] == results[4].msg_id
    assert reverse_page[1]['msg_id'] == results[3].msg_id

    # .. entries carry no payload unless it is asked for ..
    assert 'data' not in page_1[0]

    with_data, _ignored = backend.browse_messages(_topic_1, _sub_key_1, state='pending', page_size=2, needs_data=True)
    assert with_data[0]['data'] == 'browse-message-0'

    # .. acknowledging two messages splits the topic between the states ..
    _ = backend.ack_messages(_sub_key_1, [results[0].msg_id, results[1].msg_id])

    pending_page, _ignored = backend.browse_messages(_topic_1, _sub_key_1, state='pending')

    assert len(pending_page) == 3

    for entry in pending_page:
        assert entry['is_delivered'] is False

    delivered_page, _ignored = backend.browse_messages(_topic_1, _sub_key_1, state='delivered')

    assert len(delivered_page) == 2

    for entry in delivered_page:
        assert entry['is_delivered'] is True

    # .. and browsing everything stamps each entry with its own delivery state.
    all_page, _ignored = backend.browse_messages(_topic_1, _sub_key_1, state='all')

    assert len(all_page) == 5
    assert all_page[0]['is_delivered'] is True
    assert all_page[1]['is_delivered'] is True
    assert all_page[2]['is_delivered'] is False
    assert all_page[3]['is_delivered'] is False
    assert all_page[4]['is_delivered'] is False

# ################################################################################################################################

def run_stats_scenario() -> 'None':
    """ The statistics and browsing every backend must support - queue depths,
    per-state totals, the publish timeline, distinct publishers and browsing.
    """
    backend = SQLPubSubBackend()

    _run_depths_and_counts_flow(backend)
    _run_timeline_and_publishers_flow(backend)
    _run_browse_flow(backend)

# ################################################################################################################################
# ################################################################################################################################
