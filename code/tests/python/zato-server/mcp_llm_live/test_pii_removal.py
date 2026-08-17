# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
import _constants
import _helpers
from _helpers import call_and_read_event as _call_and_read_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The detector names the audit trace counts findings under
_detector_email     = 'email'
_detector_imei      = 'imei'
_detector_ipv4      = 'ipv4'
_detector_my_number = 'jp_my_number'

# The plain replacements of gateways without stable replacements
_replacement_email_plain     = 'REPLACED_EMAIL'
_replacement_imei_plain      = 'REPLACED_IMEI'
_replacement_my_number_plain = 'REPLACED_JP_MY_NUMBER'

# The numbered replacements of the stable-replacement gateways - each string value is replaced
# on its own, so a value that is the whole string always gets the first number of its detector.
_replacement_email_stable = 'REPLACED_EMAIL_1'
_replacement_imei_stable  = 'REPLACED_IMEI_1'

# What the network field of the customer record reads once its addresses are replaced -
# the repeated address shares one replacement and the distinct one gets the next number.
_network_replaced = 'primary REPLACED_IPV4_1 standby REPLACED_IPV4_1 gateway REPLACED_IPV4_2'

# What the Greek contacts line reads once its two distinct emails
# get two differently numbered replacements
_contacts_replaced = 'primary REPLACED_EMAIL_1 backup REPLACED_EMAIL_2'

# How many valid IMEIs the customer record carries
_valid_imei_count = 3

# ################################################################################################################################
# ################################################################################################################################

def _get_customer_record(
    zato_server:'anydict',
    url_path:'str',
    gateway_name:'str',
    customer_id:'str',
    ) -> 'anytuple':
    """ One customer call through the given gateway, returning the record
    and the audit data document of the call's event.
    """

    body, event_data = _call_and_read_event(
        zato_server, url_path, gateway_name,
        _constants.Service_Customer_Get, {'customer_id': customer_id})

    data = _helpers.get_result_data(body)

    out = data, event_data
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPIIRemoval:
    """ The detectors of the selected land replace confirmed values with tokens
    and the audit trace counts the findings per detector.
    """

# ################################################################################################################################

    def test_one_email_is_replaced_and_counted_as_one(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII, _constants.Customer_ID)

        # The one email is a token now ..
        assert data['email'] == _replacement_email_stable, data['email']
        assert _constants.Customer_Email not in str(data), data

        # .. and the count is exactly one, for the singular pane line.
        assert event_data['pii_removed'][_detector_email] == 1, event_data

# ################################################################################################################################

    def test_three_imeis_in_mixed_forms_are_replaced_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII, _constants.Customer_ID)

        # Each of the three written forms is recognized and replaced ..
        devices = {}

        for device in data['devices']:
            devices[device['label']] = device['imei']

        assert devices['phone-main'] == _replacement_imei_stable, devices
        assert devices['phone-backup'] == _replacement_imei_stable, devices
        assert devices['tablet'] == _replacement_imei_stable, devices

        # .. and the count is three, for the plural pane line.
        assert event_data['pii_removed'][_detector_imei] == _valid_imei_count, event_data

# ################################################################################################################################

    def test_an_unselected_land_leaves_everything_alone(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_Other_Land, _constants.Gateway_PII_Other_Land,
            _constants.Customer_ID)

        # The record's values match no detector of the selected land, so nothing changed ..
        assert data['email'] == _constants.Customer_Email, data['email']
        assert data['devices'][0]['imei'] == _constants.Customer_IMEI_Compact, data['devices']
        assert _constants.Customer_IPv4 in data['network'], data['network']

        # .. and no count was written.
        assert 'pii_removed' not in event_data, event_data

# ################################################################################################################################

    def test_an_excluded_detector_leaves_its_values_alone(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_Exclude, _constants.Gateway_PII_Exclude,
            _constants.Customer_ID)

        # The email detector is excluded, so the email survives ..
        assert data['email'] == _constants.Customer_Email, data['email']

        # .. while the other detectors of the same land keep working.
        assert data['devices'][0]['imei'] == _replacement_imei_plain, data['devices']

        pii_removed = event_data['pii_removed']
        assert _detector_email not in pii_removed, pii_removed
        assert pii_removed[_detector_imei] == _valid_imei_count, pii_removed

# ################################################################################################################################

    def test_validation_keeps_a_broken_checksum_intact(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII, _constants.Customer_ID)

        # The retired device's IMEI has a broken checksum, so it is not replaced ..
        devices = {}

        for device in data['devices']:
            devices[device['label']] = device['imei']

        assert devices['retired'] == _constants.Customer_IMEI_Invalid, devices

        # .. and only the confirmed ones were counted.
        assert event_data['pii_removed'][_detector_imei] == _valid_imei_count, event_data

# ################################################################################################################################

    def test_stable_replacements_repeat_for_the_same_value(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII, _constants.Customer_ID)

        # The address that appears twice shares one replacement
        # and the different address gets the next number.
        assert data['network'] == _network_replaced, data['network']

        assert event_data['pii_removed'][_detector_ipv4] == 3, event_data

# ################################################################################################################################
# ################################################################################################################################

class TestPIIOptions:
    """ PII removal across its options - two lands at once, a directly named detector,
    validation off, distinct values and nested data.
    """

# ################################################################################################################################

    def test_two_lands_catch_both(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_Two_Lands, _constants.Gateway_PII_Two_Lands,
            _constants.Customer_ID_Japanese)

        # The international land catches the email and the IMEI ..
        assert data['email'] == _replacement_email_plain, data['email']
        assert data['profile']['device']['imei'] == _replacement_imei_plain, data['profile']

        # .. the Japanese land catches the national id in the same one response ..
        assert data['national_id'] == _replacement_my_number_plain, data['national_id']

        # .. and the trace counts both lands' findings.
        pii_removed = event_data['pii_removed']

        assert pii_removed[_detector_email] == 2, pii_removed
        assert pii_removed[_detector_imei] == 1, pii_removed
        assert pii_removed[_detector_my_number] == 1, pii_removed

# ################################################################################################################################

    def test_explicit_detectors_need_no_land(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_Detector, _constants.Gateway_PII_Detector,
            _constants.Customer_ID)

        # The directly named detector runs with no land configured anywhere ..
        assert data['email'] == _replacement_email_plain, data['email']

        # .. and everything outside it stays as the service built it.
        assert data['devices'][0]['imei'] == _constants.Customer_IMEI_Compact, data['devices']
        assert _constants.Customer_IPv4 in data['network'], data['network']

        pii_removed = event_data['pii_removed']

        assert pii_removed == {_detector_email: 1}, pii_removed

# ################################################################################################################################

    def test_validation_off_tokenizes_lookalikes(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII_No_Validate, _constants.Gateway_PII_No_Validate,
            _constants.Customer_ID)

        # The broken-checksum IMEI the validating gateway keeps intact is a token here ..
        devices = {}

        for device in data['devices']:
            devices[device['label']] = device['imei']

        assert devices['retired'] == _replacement_imei_plain, devices

        # .. so all four written forms count, not three.
        assert event_data['pii_removed'][_detector_imei] == 4, event_data

# ################################################################################################################################

    def test_distinct_values_get_distinct_replacements(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII,
            _constants.Customer_ID_Greek)

        # The two distinct emails of the one contacts line get two differently
        # numbered replacements ..
        assert data['contacts'] == _contacts_replaced, data['contacts']

        # .. and the email field, a string of its own, starts its numbering over.
        assert data['email'] == _replacement_email_stable, data['email']

        assert event_data['pii_removed'][_detector_email] == 3, event_data

# ################################################################################################################################

    def test_nested_data_gets_the_same_tokens(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII,
            _constants.Customer_ID_Japanese)

        # PII nested in objects and arrays is replaced at every level
        # with the same tokens a flat response gets ..
        assert data['email'] == _replacement_email_stable, data['email']
        assert data['profile']['emails'] == [_replacement_email_stable], data['profile']
        assert data['profile']['device']['imei'] == _replacement_imei_stable, data['profile']

        # .. the national id stays - its land is not on this gateway ..
        assert data['national_id'] == _constants.Customer_National_ID_Japanese, data['national_id']

        # .. and the counts match the two levels' findings.
        pii_removed = event_data['pii_removed']

        assert pii_removed[_detector_email] == 2, pii_removed
        assert pii_removed[_detector_imei] == 1, pii_removed

# ################################################################################################################################
# ################################################################################################################################

class TestScriptsThroughPII:
    """ PII inside Greek diacritic prose - the values are replaced
    and the surrounding text comes back byte-identical.
    """

# ################################################################################################################################

    def test_diacritics_around_pii_survive_byte_identical(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_PII, _constants.Gateway_PII,
            _constants.Customer_ID_Diacritics)

        # Each notes line is a string of its own, so both emails get the first number,
        # and everything around them is untouched to the byte ..
        expected_support = _constants.Customer_Notes_Support.replace(_constants.Customer_Email_Support, _replacement_email_stable)
        expected_billing = _constants.Customer_Notes_Billing.replace(_constants.Customer_Email_Billing, _replacement_email_stable)

        assert data['notes_support'] == expected_support, data['notes_support']
        assert data['notes_billing'] == expected_billing, data['notes_billing']

        # .. the fields with no PII at all are byte-identical too ..
        assert data['name'] == _constants.Customer_Name_Diacritics, data['name']
        assert data['city'] == _constants.Customer_City_Diacritics, data['city']

        # .. and the trace counts the two emails, nothing else.
        assert event_data['pii_removed'] == {_detector_email: 2}, event_data

# ################################################################################################################################
# ################################################################################################################################
