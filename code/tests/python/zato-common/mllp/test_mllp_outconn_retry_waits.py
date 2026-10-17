# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest.mock import patch

# pytest
import pytest

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.typing_ import list_
from zato.common.util.retry import RetryPolicy
from zato.server.generic.api.outconn_hl7_mllp import _HL7MLLPConnection

# ################################################################################################################################
# ################################################################################################################################

# The waits a direct send made, in seconds
intlist = list_[int]

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

_cid = 'test-cid-retry-waits'
_conn_name = 'outgoing.mllp.retry'

_no_ack_error = 'No acknowledgment'

# ################################################################################################################################
# ################################################################################################################################

def _build_connection(max_retries:'int', sleep_time:'int', threshold:'int', multiplier:'int') -> '_HL7MLLPConnection':
    config = {
        _retry.Field_Max_Retries: max_retries,
        _retry.Field_Sleep_Time: sleep_time,
        _retry.Field_Backoff_Threshold: threshold,
        _retry.Field_Backoff_Multiplier: multiplier,
    }

    out = _HL7MLLPConnection.__new__(_HL7MLLPConnection)
    out.retry_policy = RetryPolicy.from_config(config, _retry)
    out.name = _conn_name

    return out

# ################################################################################################################################

def _send_until_exhausted(connection:'_HL7MLLPConnection') -> 'intlist':

    # Every wait the loop makes, recorded rather than slept through
    out:'intlist' = []

    def _send() -> 'None':
        raise Exception(_no_ack_error)

    with patch('zato.server.generic.api.outconn_hl7_mllp.sleep', out.append):
        with pytest.raises(Exception, match=_no_ack_error):
            _ = connection._send_with_policy(_cid, _send, True)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDirectRetryWaits:

    def test_the_first_wait_of_a_direct_send_is_held_under_the_ceiling_on_a_single_wait(self) -> 'None':

        connection = _build_connection(1, 10, 24, 1)
        waits = _send_until_exhausted(connection)

        assert waits == [_retry.Max_Sleep_Time]

# ################################################################################################################################

    def test_the_first_wait_of_a_direct_send_is_held_under_the_threshold(self) -> 'None':

        connection = _build_connection(1, 8, 1, 4)
        waits = _send_until_exhausted(connection)

        assert waits == [1]

# ################################################################################################################################
# ################################################################################################################################
