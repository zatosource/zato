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

# The detector names the audit trace counts findings under
_detector_email = 'intl_email'
_detector_imei  = 'intl_imei'
_detector_ipv4  = 'intl_ipv4'

# The tokens the detectors replace values with - each string value is tokenized on its own,
# so a value that is the whole string always gets the first number of its detector.
_token_email_stable = '{{EMAIL_1}}'
_token_imei_stable  = '{{INTL_IMEI_1}}'
_token_imei_plain   = '{{INTL_IMEI}}'

# What the network field of the customer record reads once its addresses are tokenized -
# the repeated address shares one token and the distinct one gets the next number.
_network_tokenized = 'primary {{IPV4_1}} standby {{IPV4_1}} gateway {{IPV4_2}}'

# How many valid IMEIs the customer record carries
_valid_imei_count = 3

# ################################################################################################################################
# ################################################################################################################################

def _get_customer_record(zato_server:'anydict', url_path:'str', gateway_name:'str') -> 'tuple':
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

    events = _audit.wait_for_events(
        audit_db_path, 1,
        object_name=gateway_name,
        event_type=AuditEvent.MCP_Tools_Call,
        min_id=min_id)

    out = data, events[-1]['data']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPIIRemoval:
    """ The detectors of the selected land replace confirmed values with tokens
    and the audit trace counts the findings per detector.
    """

# ################################################################################################################################

    def test_one_email_is_replaced_and_counted_as_one(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_PII, _constants.Gateway_PII)

        # The one email is a token now ..
        assert data['email'] == _token_email_stable, data['email']
        assert _constants.Customer_Email not in str(data), data

        # .. and the count is exactly one, for the singular pane line.
        assert event_data['pii_removed'][_detector_email] == 1, event_data

# ################################################################################################################################

    def test_three_imeis_in_mixed_forms_are_replaced_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_PII, _constants.Gateway_PII)

        # Each of the three written forms is recognized and replaced ..
        devices = {}

        for device in data['devices']:
            devices[device['label']] = device['imei']

        assert devices['phone-main'] == _token_imei_stable, devices
        assert devices['phone-backup'] == _token_imei_stable, devices
        assert devices['tablet'] == _token_imei_stable, devices

        # .. and the count is three, for the plural pane line.
        assert event_data['pii_removed'][_detector_imei] == _valid_imei_count, event_data

# ################################################################################################################################

    def test_an_unselected_land_leaves_everything_alone(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_Other_Land, _constants.Gateway_PII_Other_Land)

        # The record's values match no detector of the selected land, so nothing changed ..
        assert data['email'] == _constants.Customer_Email, data['email']
        assert data['devices'][0]['imei'] == _constants.Customer_IMEI_Compact, data['devices']
        assert _constants.Customer_IPv4 in data['network'], data['network']

        # .. and no count was written.
        assert 'pii_removed' not in event_data, event_data

# ################################################################################################################################

    def test_an_excluded_detector_leaves_its_values_alone(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_Exclude, _constants.Gateway_PII_Exclude)

        # The email detector is excluded, so the email survives ..
        assert data['email'] == _constants.Customer_Email, data['email']

        # .. while the other detectors of the same land keep working.
        assert data['devices'][0]['imei'] == _token_imei_plain, data['devices']

        pii_removed = event_data['pii_removed']
        assert _detector_email not in pii_removed, pii_removed
        assert pii_removed[_detector_imei] == _valid_imei_count, pii_removed

# ################################################################################################################################

    def test_validation_keeps_a_broken_checksum_intact(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_PII, _constants.Gateway_PII)

        # The retired device's IMEI has a broken checksum, so it is not replaced ..
        devices = {}

        for device in data['devices']:
            devices[device['label']] = device['imei']

        assert devices['retired'] == _constants.Customer_IMEI_Invalid, devices

        # .. and only the confirmed ones were counted.
        assert event_data['pii_removed'][_detector_imei] == _valid_imei_count, event_data

# ################################################################################################################################

    def test_stable_tokens_repeat_for_the_same_value(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(zato_server, _constants.Path_PII, _constants.Gateway_PII)

        # The address that appears twice shares one token
        # and the different address gets the next number.
        assert data['network'] == _network_tokenized, data['network']

        assert event_data['pii_removed'][_detector_ipv4] == 3, event_data

# ################################################################################################################################
# ################################################################################################################################
