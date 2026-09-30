# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import delete_all_rows, get_message_rows
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# The topic and subscriber all the retry settings assertions share.
_topic = 'pubsub.backend.test.retry-settings'
_sub_key = 'zpsk.test.retry-settings.1'

# The settings a publisher gives, none of which is a default of any policy.
_max_retries = 7
_sleep_time = 11
_backoff_threshold = 170
_backoff_multiplier = 3

# ################################################################################################################################
# ################################################################################################################################

def _assert_carries_settings(message:'anydict') -> 'None':
    """ A message read back carries exactly the settings its publisher gave.
    """
    assert message[_retry.Field_Max_Retries] == _max_retries, message
    assert message[_retry.Field_Sleep_Time] == _sleep_time, message
    assert message[_retry.Field_Backoff_Threshold] == _backoff_threshold, message
    assert message[_retry.Field_Backoff_Multiplier] == _backoff_multiplier, message

# ################################################################################################################################

def _assert_carries_no_settings(message:'anydict') -> 'None':
    """ A message published without settings has none of the keys, so that the policy's defaults apply to it.
    """
    for name in _retry.FieldList:
        assert name not in message, message

# ################################################################################################################################

def run_retry_settings_scenario() -> 'None':
    """ Retry settings given at publish time travel with the message - they are stored in the message's row,
    every read path hands them back, and a message published without them has none.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
    backend.subscribe(_sub_key, _topic)

    # One message with settings and one without ..
    with_settings = backend.publish(
        _topic,
        'retry-settings-given',
        max_retries=_max_retries,
        retry_sleep_time=_sleep_time,
        retry_backoff_threshold=_backoff_threshold,
        retry_backoff_multiplier=_backoff_multiplier,
    )

    without_settings = backend.publish(_topic, 'retry-settings-absent')

    # .. the row of the first carries the settings and the row of the second carries nulls ..
    rows = get_message_rows(_topic)

    assert len(rows) == 2, rows

    assert rows[0].max_retries == _max_retries, rows[0]
    assert rows[0].retry_sleep_time == _sleep_time, rows[0]
    assert rows[0].retry_backoff_threshold == _backoff_threshold, rows[0]
    assert rows[0].retry_backoff_multiplier == _backoff_multiplier, rows[0]

    assert rows[1].max_retries is None, rows[1]
    assert rows[1].retry_sleep_time is None, rows[1]
    assert rows[1].retry_backoff_threshold is None, rows[1]
    assert rows[1].retry_backoff_multiplier is None, rows[1]

    # .. a fetch hands the settings back with the message ..
    messages = backend.fetch_messages(_sub_key)

    assert len(messages) == 2, messages
    assert messages[0]['msg_id'] == with_settings.msg_id, messages[0]
    assert messages[1]['msg_id'] == without_settings.msg_id, messages[1]

    _assert_carries_settings(messages[0])
    _assert_carries_no_settings(messages[1])

    # .. and so does a browse, with and without the payload.
    browsed, _ignored = backend.browse_messages(_topic, _sub_key, state='pending', needs_data=True)

    assert len(browsed) == 2, browsed

    _assert_carries_settings(browsed[0])
    _assert_carries_no_settings(browsed[1])

    browsed, _ignored = backend.browse_messages(_topic, _sub_key, state='pending', needs_data=False)

    _assert_carries_settings(browsed[0])
    _assert_carries_no_settings(browsed[1])

# ################################################################################################################################
# ################################################################################################################################
