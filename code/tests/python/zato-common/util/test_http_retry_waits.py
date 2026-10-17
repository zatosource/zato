# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest.mock import patch

# pytest
import pytest

# requests
from requests.exceptions import Timeout

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.typing_ import list_
from zato.common.util.http_retry import send_with_retry
from zato.common.util.retry import RetryPolicy

# ################################################################################################################################
# ################################################################################################################################

# The waits a send made, in seconds
intlist = list_[int]

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

_cid = 'test-cid-http-retry-waits'
_label = 'REST'

_timeout_error = 'Read timed out'

# ################################################################################################################################
# ################################################################################################################################

def _build_policy(max_retries:'int', sleep_time:'int', threshold:'int', multiplier:'int') -> 'RetryPolicy':
    config = {
        _retry.Field_Max_Retries: max_retries,
        _retry.Field_Sleep_Time: sleep_time,
        _retry.Field_Backoff_Threshold: threshold,
        _retry.Field_Backoff_Multiplier: multiplier,
    }

    out = RetryPolicy.from_config(config, _retry)
    return out

# ################################################################################################################################

def _send_until_exhausted(policy:'RetryPolicy') -> 'intlist':

    # Every wait the loop makes, recorded rather than slept through
    out:'intlist' = []

    def _send() -> 'None':
        raise Timeout(_timeout_error)

    with patch('zato.common.util.http_retry.sleep', out.append):
        with pytest.raises(Timeout, match=_timeout_error):
            _ = send_with_retry(policy, _send, _cid, _label)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestHTTPRetryWaits:

    def test_the_first_wait_is_held_under_the_ceiling_on_a_single_wait(self) -> 'None':

        policy = _build_policy(3, 20, 60, 2)
        waits = _send_until_exhausted(policy)

        assert waits == [_retry.Max_Sleep_Time, _retry.Max_Sleep_Time, _retry.Max_Sleep_Time]

# ################################################################################################################################

    def test_the_first_wait_is_held_under_the_threshold(self) -> 'None':

        policy = _build_policy(3, 10, 5, 2)
        waits = _send_until_exhausted(policy)

        assert waits == [5]

# ################################################################################################################################

    def test_each_next_wait_grows_by_the_multiplier_up_to_the_ceiling(self) -> 'None':

        policy = _build_policy(5, 2, 60, 2)
        waits = _send_until_exhausted(policy)

        assert waits == [2, 4, _retry.Max_Sleep_Time, _retry.Max_Sleep_Time, _retry.Max_Sleep_Time]

# ################################################################################################################################
# ################################################################################################################################
