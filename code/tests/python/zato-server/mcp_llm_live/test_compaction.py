# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
import _constants
import _helpers
from _helpers import call_and_read_event as _call_and_read_event

# Zato
from zato.common.util.safeguards.common import Base64_Marker_Template

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The customer record carries exactly these null fields - two at the top level and one nested
_null_field_count = 3

# What a stripped base64 blob is replaced with
_base64_marker_prefix = '[binary content removed:'

# The whitespace run the customer notes carry when no stage collapses it
_notes_raw_run = 'Alpha    Beta'

# The same words once the collapse has run
_notes_collapsed_run = 'Alpha Beta'

# The tags array of the record - its null element keeps its position under null stripping
_tags_with_null = ['vip', None, 'beta']

# The avatar blob as the fixture builds it - the marker must name exactly its length
_avatar_blob = 'data:image/png;base64,' + 'QUJDREVG' * 40

# The base64-looking string below the stripping floor - it always survives
_thumb_blob = 'data:image/png;base64,QUJDREVG'

# ################################################################################################################################
# ################################################################################################################################

def _get_customer_record(zato_server:'anydict', url_path:'str', gateway_name:'str') -> 'anytuple':
    """ One customer call through the given gateway, returning the record
    and the audit data document of the call's event.
    """

    body, event_data = _call_and_read_event(
        zato_server, url_path, gateway_name,
        _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID})

    data = _helpers.get_result_data(body)

    out = data, event_data
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCompaction:
    """ The compaction stages strip nulls, collapse whitespace and remove base64 blobs,
    each counting exactly what it did - and stay silent when off.
    """

# ################################################################################################################################

    def test_nulls_are_stripped_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Compaction, _constants.Gateway_Compaction)

        # The null fields are gone from the record, the nested one included ..
        assert 'fax' not in data, data
        assert 'secondary_email' not in data, data
        assert 'iban' not in data['billing'], data

        # .. and the audit trace counts exactly them.
        assert event_data['nulls_removed'] == _null_field_count, event_data

# ################################################################################################################################

    def test_whitespace_is_collapsed_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Compaction, _constants.Gateway_Compaction)

        # The runs in the notes have collapsed to single spaces ..
        notes = data['notes']
        assert _notes_collapsed_run in notes, notes
        assert '  ' not in notes, notes

        # .. and the count says how many characters the collapse removed.
        assert event_data['whitespace_chars_removed'] > 0, event_data

# ################################################################################################################################

    def test_base64_blobs_are_stripped_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Compaction, _constants.Gateway_Compaction)

        # The avatar blob is a size marker now ..
        avatar = data['avatar']
        assert avatar.startswith(_base64_marker_prefix), avatar
        assert 'base64' not in avatar, avatar

        # .. and exactly one blob was counted.
        assert event_data['base64_blobs_removed'] == 1, event_data

# ################################################################################################################################

    def test_stages_off_leave_the_content_untouched(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Main, _constants.Gateway_Main)

        # With every compaction stage off, the record comes back as the service built it ..
        assert data['fax'] is None, data
        assert data['secondary_email'] is None, data
        assert _notes_raw_run in data['notes'], data['notes']
        assert 'base64' in data['avatar'], data['avatar']

        # .. and the audit event carries no compaction keys at all.
        assert 'nulls_removed' not in event_data, event_data
        assert 'whitespace_chars_removed' not in event_data, event_data
        assert 'base64_blobs_removed' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################

class TestCompactionBoundaries:
    """ Each compaction rule alone and at its exact boundary - nulls in objects
    against arrays, whitespace inside strings, the base64 marker and its floor.
    """

# ################################################################################################################################

    def test_each_safeguard_acts_alone(self, zato_server:'anydict') -> 'None':

        # The null-stripping gateway leaves whitespace and base64 alone ..
        data, event_data = _get_customer_record(zato_server, _constants.Path_Nulls, _constants.Gateway_Nulls)

        assert 'fax' not in data, data
        assert _notes_raw_run in data['notes'], data['notes']
        assert data['avatar'] == _avatar_blob, data['avatar']

        assert event_data['nulls_removed'] == _null_field_count, event_data
        assert 'whitespace_chars_removed' not in event_data, event_data
        assert 'base64_blobs_removed' not in event_data, event_data

        # .. the whitespace gateway leaves nulls and base64 alone ..
        data, event_data = _get_customer_record(zato_server, _constants.Path_Whitespace, _constants.Gateway_Whitespace)

        assert data['fax'] is None, data
        assert _notes_collapsed_run in data['notes'], data['notes']
        assert data['avatar'] == _avatar_blob, data['avatar']

        assert event_data['whitespace_chars_removed'] > 0, event_data
        assert 'nulls_removed' not in event_data, event_data
        assert 'base64_blobs_removed' not in event_data, event_data

        # .. and the base64 gateway leaves both alone.
        data, event_data = _get_customer_record(zato_server, _constants.Path_Base64, _constants.Gateway_Base64)

        assert data['fax'] is None, data
        assert _notes_raw_run in data['notes'], data['notes']
        assert data['avatar'] != _avatar_blob, data['avatar']

        assert event_data['base64_blobs_removed'] == 1, event_data
        assert 'nulls_removed' not in event_data, event_data
        assert 'whitespace_chars_removed' not in event_data, event_data

# ################################################################################################################################

    def test_nulls_leave_objects_never_arrays(self, zato_server:'anydict') -> 'None':

        data, _ = _get_customer_record(zato_server, _constants.Path_Nulls, _constants.Gateway_Nulls)

        # Null-valued keys disappear at the top level and nested alike ..
        assert 'fax' not in data, data
        assert 'secondary_email' not in data, data
        assert 'iban' not in data['billing'], data

        # .. while the null array element keeps its position.
        assert data['tags'] == _tags_with_null, data['tags']

# ################################################################################################################################

    def test_whitespace_collapses_inside_strings_only(self, zato_server:'anydict') -> 'None':

        data, _ = _get_customer_record(zato_server, _constants.Path_Whitespace, _constants.Gateway_Whitespace)

        # Runs of spaces inside string values become one space ..
        notes = data['notes']

        assert _notes_collapsed_run in notes, notes
        assert '  ' not in notes, notes

        # .. an IMEI written with single spaces keeps them - single spaces are no run ..
        device_imeis = []

        for device in data['devices']:
            device_imeis.append(device['imei'])

        assert _constants.Customer_IMEI_Spaced in device_imeis, device_imeis

        # .. and the key names and the structure stay untouched.
        assert data['name'] == _constants.Customer_Name, data
        assert data['billing']['plan'] == 'monthly', data
        assert len(data['devices']) == 4, data['devices']

# ################################################################################################################################

    def test_the_base64_marker_names_the_size(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_Base64, _constants.Gateway_Base64)

        # The long blob is a marker naming exactly the original length ..
        expected_marker = Base64_Marker_Template.format(size=len(_avatar_blob))
        assert data['avatar'] == expected_marker, data['avatar']

        # .. the short base64-looking string below the floor passes through unchanged ..
        assert data['thumb'] == _thumb_blob, data['thumb']

        # .. and the count says one blob and one blob alone.
        assert event_data['base64_blobs_removed'] == 1, event_data

# ################################################################################################################################
# ################################################################################################################################

class TestScriptsThroughCompaction:
    """ Right-to-left text through the whitespace and pipeline gateways - clean Hebrew
    passes byte-identical and the collapse keeps its characters intact.
    """

# ################################################################################################################################

    def test_hebrew_collapses_safely_and_clean_text_is_byte_identical(self, zato_server:'anydict') -> 'None':

        # Through the whitespace gateway - the runs collapse and the letters stay ..
        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Whitespace, _constants.Gateway_Whitespace,
            _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID_Hebrew})

        data = _helpers.get_result_data(body)

        assert data['notes'] == _constants.Customer_Notes_Hebrew_Collapsed, data['notes']
        assert data['greeting'] == _constants.Customer_Greeting_Hebrew, data['greeting']

        # .. counting exactly the characters of the two runs ..
        assert event_data['whitespace_chars_removed'] == _constants.Hebrew_Whitespace_Removed, event_data

        # .. and through the everything-on pipeline - compaction, PII, safety and the cap -
        # the whole record is exact, the clean fields byte-identical among them.
        body, event_data = _call_and_read_event(
            zato_server, _constants.Path_Pipeline, _constants.Gateway_Pipeline,
            _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID_Hebrew})

        data = _helpers.get_result_data(body)

        expected = {
            'name': _constants.Customer_Name_Hebrew,
            'city': _constants.Customer_City_Hebrew,
            'greeting': _constants.Customer_Greeting_Hebrew,
            'notes': _constants.Customer_Notes_Hebrew_Collapsed,
            'customer_id': _constants.Customer_ID_Hebrew,
            'found': True,
        }

        assert data == expected, data

        # No stage but the collapse found anything in the right-to-left text.
        assert event_data['whitespace_chars_removed'] == _constants.Hebrew_Whitespace_Removed, event_data
        assert 'pii_removed' not in event_data, event_data
        assert 'unicode_chars_removed' not in event_data, event_data
        assert 'was_truncated' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################
