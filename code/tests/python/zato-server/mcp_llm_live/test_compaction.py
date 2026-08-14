# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
import _audit
import _constants
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The customer record carries exactly these two null fields
_null_field_count = 2

# What a stripped base64 blob is replaced with
_base64_marker_prefix = '[binary content removed:'

# ################################################################################################################################
# ################################################################################################################################

def _get_customer_record(zato_server:'anydict', url_path:'str') -> 'tuple':
    """ One customer call through the given gateway, returning the record
    and the audit data document of the call's event.
    """

    audit_db_path = zato_server['audit_db_path']
    min_id = _audit.last_event_id(audit_db_path)

    client = _helpers.make_client(zato_server, url_path)
    session_id = _helpers.open_session(client)

    body = _helpers.call_tool(client, session_id, _constants.Service_Customer_Get,
        {'customer_id': _constants.Customer_ID})

    data = _helpers.get_result_data(body)

    gateway_name = {
        _constants.Path_Compaction: _constants.Gateway_Compaction,
        _constants.Path_Main: _constants.Gateway_Main,
    }[url_path]

    events = _audit.wait_for_events(
        audit_db_path, 1,
        object_name=gateway_name,
        event_type=AuditEvent.MCP_Tools_Call,
        min_id=min_id)

    out = data, events[-1]['data']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCompaction:
    """ The compaction stages strip nulls, collapse whitespace and remove base64 blobs,
    each counting exactly what it did - and stay silent when off.
    """

# ################################################################################################################################

    def test_nulls_are_stripped_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Compaction)

        # The null fields are gone from the record ..
        assert 'fax' not in data, data
        assert 'secondary_email' not in data, data

        # .. and the audit trace counts exactly them.
        assert event_data['nulls_removed'] == _null_field_count, event_data

# ################################################################################################################################

    def test_whitespace_is_collapsed_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Compaction)

        # The runs in the notes have collapsed to single spaces ..
        notes = data['notes']
        assert 'Alpha Beta' in notes, notes
        assert '  ' not in notes, notes

        # .. and the count says how many characters the collapse removed.
        assert event_data['whitespace_chars_removed'] > 0, event_data

# ################################################################################################################################

    def test_base64_blobs_are_stripped_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Compaction)

        # The avatar blob is a size marker now ..
        avatar = data['avatar']
        assert avatar.startswith(_base64_marker_prefix), avatar
        assert 'base64' not in avatar, avatar

        # .. and exactly one blob was counted.
        assert event_data['base64_blobs_removed'] == 1, event_data

# ################################################################################################################################

    def test_stages_off_leave_the_content_untouched(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Main)

        # With every compaction stage off, the record comes back as the service built it ..
        assert data['fax'] is None, data
        assert data['secondary_email'] is None, data
        assert 'Alpha    Beta' in data['notes'], data['notes']
        assert 'base64' in data['avatar'], data['avatar']

        # .. and the audit event carries no compaction keys at all.
        assert 'nulls_removed' not in event_data, event_data
        assert 'whitespace_chars_removed' not in event_data, event_data
        assert 'base64_blobs_removed' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################
