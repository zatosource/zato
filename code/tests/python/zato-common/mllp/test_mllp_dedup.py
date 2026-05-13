# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.hl7.mllp.dedup import MessageDeduplicator, extract_control_id
from zato.common.hl7.mllp.server import TTL_Multipliers

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
        dedup.is_duplicate('CTRL001')

        result = dedup.is_duplicate('CTRL001')
        assert result is True

    def test_different_id_not_duplicate(self) -> 'None':
        """ Different control ID reports False.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        dedup.is_duplicate('CTRL001')

        result = dedup.is_duplicate('CTRL002')
        assert result is False

    def test_expired_id_not_duplicate(self) -> 'None':
        """ After TTL expires, same control ID reports False.
        """
        dedup = MessageDeduplicator(ttl_seconds=0.1)
        dedup.is_duplicate('CTRL001')

        time.sleep(0.2)

        result = dedup.is_duplicate('CTRL001')
        assert result is False

    def test_eviction(self) -> 'None':
        """ Expired entries are removed from _seen after a new is_duplicate call.
        """
        dedup = MessageDeduplicator(ttl_seconds=0.1)
        dedup.is_duplicate('OLD_CTRL')

        time.sleep(0.2)

        # This call triggers eviction of OLD_CTRL before checking NEW_CTRL
        dedup.is_duplicate('NEW_CTRL')

        assert 'OLD_CTRL' not in dedup._seen
        assert 'NEW_CTRL' in dedup._seen

    def test_clear(self) -> 'None':
        """ clear() empties the cache.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        dedup.is_duplicate('CTRL001')
        dedup.is_duplicate('CTRL002')

        dedup.clear()

        assert len(dedup._seen) == 0

    def test_clear_allows_resubmission(self) -> 'None':
        """ After clear(), a previously seen ID is no longer considered duplicate.
        """
        dedup = MessageDeduplicator(ttl_seconds=60.0)
        dedup.is_duplicate('CTRL001')
        dedup.clear()

        result = dedup.is_duplicate('CTRL001')
        assert result is False

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
