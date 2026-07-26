# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.hl7.mllp.dedup import MessageDeduplicator, extract_control_id
from zato.common.hl7.mllp.settings import TTL_Multipliers

# ################################################################################################################################
# ################################################################################################################################

class TestExtractControlID:
    """ Tests for extract_control_id.
    """

    def test_extract_control_id(self) -> 'None':
        """ Standard MSH line returns the correct MSH-10 value.
        """
        msh_line = 'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|MY_CTRL_001|P|2.5'
        result = extract_control_id(msh_line)
        assert result == 'MY_CTRL_001'

    def test_extract_control_id_short_msh(self) -> 'None':
        """ Truncated MSH line with fewer than 10 fields returns empty string.
        """
        msh_line = 'MSH|^~\\&|SendApp|SendFac'
        result = extract_control_id(msh_line)
        assert result == ''

# ################################################################################################################################
# ################################################################################################################################

class TestMessageDeduplicator:
    """ Tests for MessageDeduplicator.
    """

    def test_first_message_not_duplicate(self) -> 'None':
        """ A fresh cache reports is_duplicate as False.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        result = dedup.is_duplicate('CTRL001')
        assert result is False

    def test_same_id_is_duplicate(self) -> 'None':
        """ Same control ID within TTL reports True.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        _ = dedup.is_duplicate('CTRL001')

        result = dedup.is_duplicate('CTRL001')
        assert result is True

    def test_different_id_not_duplicate(self) -> 'None':
        """ Different control ID reports False.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        _ = dedup.is_duplicate('CTRL001')

        result = dedup.is_duplicate('CTRL002')
        assert result is False

    def test_expired_id_not_duplicate(self) -> 'None':
        """ After TTL expires, same control ID reports False.
        """
        dedup = MessageDeduplicator(ttl_seconds=0.1)
        _ = dedup.is_duplicate('CTRL001')

        time.sleep(0.2)

        result = dedup.is_duplicate('CTRL001')
        assert result is False

    def test_eviction(self) -> 'None':
        """ Expired entries are removed from _seen after a new is_duplicate call.
        """
        dedup = MessageDeduplicator(ttl_seconds=0.1)
        _ = dedup.is_duplicate('OLD_CTRL')

        time.sleep(0.2)

        # This call triggers eviction of OLD_CTRL before checking NEW_CTRL
        _ = dedup.is_duplicate('NEW_CTRL')

        assert 'OLD_CTRL' not in dedup._seen
        assert 'NEW_CTRL' in dedup._seen

    def test_clear(self) -> 'None':
        """ clear() empties the cache.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        _ = dedup.is_duplicate('CTRL001')
        _ = dedup.is_duplicate('CTRL002')

        dedup.clear()

        assert len(dedup._seen) == 0

    def test_clear_allows_resubmission(self) -> 'None':
        """ After clear(), a previously seen ID is no longer considered duplicate.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        _ = dedup.is_duplicate('CTRL001')
        dedup.clear()

        result = dedup.is_duplicate('CTRL001')
        assert result is False

# ################################################################################################################################
# ################################################################################################################################

class TestTheCacheStaysBounded:
    """ A sender that never repeats a control id would grow the cache for as long as the TTL
    window lasts, so the cache holds a fixed number of ids and drops what it has held longest.
    """

    def test_the_cache_never_exceeds_its_cap(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=3600.0, max_entries=10)

        for index in range(100):
            _ = dedup.is_duplicate(f'CTRL{index}')

        assert len(dedup._seen) == 10

    def test_the_oldest_ids_are_the_ones_dropped(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=3600.0, max_entries=3)

        for control_id in ['FIRST', 'SECOND', 'THIRD', 'FOURTH']:
            _ = dedup.is_duplicate(control_id)

        assert 'FIRST' not in dedup._seen
        assert 'FOURTH' in dedup._seen

    def test_an_id_dropped_for_room_is_accepted_again(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=3600.0, max_entries=2)

        _ = dedup.is_duplicate('FIRST')
        _ = dedup.is_duplicate('SECOND')
        _ = dedup.is_duplicate('THIRD')

        assert dedup.is_duplicate('FIRST') is False

    def test_a_repeat_within_the_cap_is_still_caught(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=3600.0, max_entries=10)

        _ = dedup.is_duplicate('CTRL001')

        assert dedup.is_duplicate('CTRL001') is True

# ################################################################################################################################
# ################################################################################################################################

class TestEvictionCostsWhatItDrops:
    """ Eviction walks the entries it actually drops rather than everything received so far,
    which is what keeps the per-message cost from growing with the volume already handled.
    """

    def test_entries_inside_the_window_are_left_alone(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=60.0)

        for index in range(50):
            _ = dedup.is_duplicate(f'CTRL{index}')

        _ = dedup.is_duplicate('LATEST')

        assert len(dedup._seen) == 51

    def test_everything_expired_goes_in_one_pass(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=0.05)

        for index in range(50):
            _ = dedup.is_duplicate(f'CTRL{index}')

        time.sleep(0.1)

        _ = dedup.is_duplicate('LATEST')

        assert list(dedup._seen) == ['LATEST']

    def test_eviction_stops_at_the_first_live_entry(self) -> 'None':
        dedup = MessageDeduplicator(ttl_seconds=0.15)

        _ = dedup.is_duplicate('OLD')
        time.sleep(0.2)

        # The entry behind the expired one arrived late enough to still be inside the window
        _ = dedup.is_duplicate('RECENT')
        _ = dedup.is_duplicate('LATEST')

        assert list(dedup._seen) == ['RECENT', 'LATEST']

# ################################################################################################################################
# ################################################################################################################################

class TestTTLMultipliers:
    """ Tests for TTL_Multipliers correctness.
    """

    def test_ttl_minutes(self) -> 'None':
        """ ttl_value=2, ttl_unit='minutes' produces 120 seconds.
        """
        result = 2 * TTL_Multipliers['minutes']
        assert result == 120

    def test_ttl_hours(self) -> 'None':
        """ ttl_value=1, ttl_unit='hours' produces 3600 seconds.
        """
        result = 1 * TTL_Multipliers['hours']
        assert result == 3600

    def test_ttl_days(self) -> 'None':
        """ ttl_value=14, ttl_unit='days' produces 1209600 seconds.
        """
        result = 14 * TTL_Multipliers['days']
        assert result == 1209600

# ################################################################################################################################
# ################################################################################################################################
