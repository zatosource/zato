# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.hl7.audit import get_wire_attrs
from zato.common.hl7.feed import generate_feed_items, run_feed, Control_Id_Prefix, FeedConfig, FeedItem
from zato.hl7v2 import parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

def test_feed_is_reproducible() -> 'None':
    """ The same seed produces the same feed, message for message.
    """
    config = FeedConfig()
    config.seed = 111

    first  = generate_feed_items(50, config)
    second = generate_feed_items(50, config)

    for item_first, item_second in zip(first, second):
        assert item_first.text == item_second.text
        assert item_first.msg_type == item_second.msg_type
        assert item_first.is_error == item_second.is_error

# ################################################################################################################################

def test_control_ids_are_unique_and_sequential() -> 'None':
    """ Every message carries its own sequential control id, stamped into MSH-10.
    """
    config = FeedConfig()
    items = generate_feed_items(10, config)

    for index, item in enumerate(items):

        expected = f'{Control_Id_Prefix}-{index + 1:08d}'
        assert item.control_id == expected

        # The control id is actually inside the message, not just on the item
        msh_fields = item.text.split('\r')[0].split('|')
        assert msh_fields[9] == expected

# ################################################################################################################################

def test_messages_are_parseable_with_expected_types() -> 'None':
    """ Every message the feed produces parses, and its wire attributes carry
    the type the mix says it is.
    """
    config = FeedConfig()
    config.seed = 222

    items = generate_feed_items(30, config)

    # Only the types from the mix may appear
    allowed_types = {msg_type for msg_type, _, _ in config.mix}

    for item in items:

        assert item.msg_type in allowed_types

        # The message parses like real traffic would
        parsed = parse_hl7(item.text, validate=False)
        assert parsed is not None

        # The wire attributes agree with the item's declared type
        msh_line = item.text.split('\r')[0]
        attrs = get_wire_attrs(msh_line)
        assert attrs['msg_type'] == item.msg_type

# ################################################################################################################################

def test_error_injection_marks_msh3() -> 'None':
    """ An injected failure is a routing marker in MSH-3, and the configured ratio
    is approximately honored over a run.
    """
    config = FeedConfig()
    config.seed = 333
    config.error_ratio = 0.2

    count = 500
    items = generate_feed_items(count, config)

    error_count = 0

    for item in items:

        msh_fields = item.text.split('\r')[0].split('|')

        # The marker and the flag always agree
        if item.is_error:
            error_count += 1
            assert msh_fields[2] == config.error_sending_app
        else:
            assert msh_fields[2] != config.error_sending_app

    # With 500 draws at a 0.2 ratio the count lands well inside this band
    assert 60 <= error_count <= 140, error_count

# ################################################################################################################################

def test_zero_error_ratio_injects_nothing() -> 'None':
    """ The default configuration injects no failures at all.
    """
    config = FeedConfig()
    items = generate_feed_items(100, config)

    for item in items:
        assert not item.is_error

# ################################################################################################################################

def test_run_feed_paces_and_counts() -> 'None':
    """ A feed run paces its sends to the configured rate and reports what it did -
    the pacing logic runs offline through an injected sleep function.
    """
    config = FeedConfig()
    config.seed = 444
    config.error_ratio = 0.3
    config.rate_per_minute = 6000

    sent_items:'anylist' = []
    sleep_calls:'anylist' = []

    def send(item:'FeedItem') -> 'None':
        sent_items.append(item)

    def fake_sleep(seconds:'float') -> 'None':
        sleep_calls.append(seconds)

    count = 20
    result = run_feed(send, count, config, sleep_func=fake_sleep)

    # Everything was sent, in order, and the counters agree with the items
    assert result.sent_count == count
    assert len(sent_items) == count
    assert len(result.durations_ms) == count

    expected_errors = len([item for item in sent_items if item.is_error])
    assert result.error_injected_count == expected_errors

    # At 6000 messages a minute the interval is 10ms - the sends are fast,
    # so nearly every message had to wait for its scheduled time.
    assert len(sleep_calls) >= count - 2, len(sleep_calls)

    # The injected sleep never advances the clock, so the drift-free schedule shows
    # through directly - each wait targets its message's slot off the run's start,
    # which means the waits grow and never pass the last slot.
    interval = 60.0 / config.rate_per_minute

    for previous_wait, next_wait in zip(sleep_calls, sleep_calls[1:]):
        assert next_wait > previous_wait

    assert sleep_calls[-1] <= (count - 1) * interval, sleep_calls[-1]

# ################################################################################################################################
# ################################################################################################################################
