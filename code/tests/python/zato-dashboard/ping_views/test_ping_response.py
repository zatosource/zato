# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every ping view answers with one display-ready shape - a one-line summary for
# the tippy, the full text for the details modal and the lexer the details
# highlight with. The frontend renders this as-is, without any string surgery.

# stdlib
from json import loads

# Zato
from zato.admin.web.views import ping_json_response, Action_Message_Max_Length, _get_ping_error_message

# ################################################################################################################################
# ################################################################################################################################

# The very error a FHIR connection pointing at an unresolvable host pings with
_fhir_error = (
    "HTTPSConnectionPool(host='demo-ehr.invalid', port=443): Max retries exceeded with url: /fhir/CapabilityStatement "
    "(Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x78b9bee26d50>: "
    "Failed to establish a new connection: [Errno -2] Name or service not known'))"
)

# What the summary keeps of it - everything before the root-cause clause, capped
_fhir_error_head = "HTTPSConnectionPool(host='demo-ehr.invalid', port=443): Max retries exceeded with url: /fhir/CapabilityStatement"

# A failure whose details are a Python traceback
_traceback_error = (
    'Could not ping the connection\n'
    'Traceback (most recent call last):\n'
    '  File "server.py", line 10, in ping\n'
    'ConnectionRefusedError: [Errno 111] Connection refused\n'
)

# ################################################################################################################################
# ################################################################################################################################

def _body(response) -> 'dict':
    out = loads(response.content)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPingErrorMessage:

    def test_the_root_cause_clause_is_dropped_and_the_rest_capped(self):
        message = _get_ping_error_message(_fhir_error)

        assert message == _fhir_error_head[:Action_Message_Max_Length] + ' ..'

# ################################################################################################################################

    def test_only_the_first_line_is_kept(self):
        message = _get_ping_error_message(_traceback_error)

        assert message == 'Could not ping the connection'

# ################################################################################################################################

    def test_a_short_message_stays_as_it_is(self):
        message = _get_ping_error_message('Connection refused')

        assert message == 'Connection refused'

# ################################################################################################################################
# ################################################################################################################################

class TestPingJSONResponse:

    def test_a_success_carries_its_info_as_the_message(self):
        body = _body(ping_json_response(True, 'Ping OK, took 12 ms'))

        assert body == {
            'is_success': True,
            'message': 'Ping OK, took 12 ms',
            'details': 'Ping OK, took 12 ms',
            'details_lexer': 'python',
        }

# ################################################################################################################################

    def test_a_failure_carries_the_summary_and_the_full_details(self):
        body = _body(ping_json_response(False, _fhir_error))

        assert body['is_success'] is False
        assert body['message'] == _fhir_error_head[:Action_Message_Max_Length] + ' ..'
        assert body['details'] == _fhir_error
        assert body['details_lexer'] == 'python'

# ################################################################################################################################

    def test_a_traceback_highlights_as_one(self):
        body = _body(ping_json_response(False, _traceback_error))

        assert body['message'] == 'Could not ping the connection'
        assert body['details'] == _traceback_error
        assert body['details_lexer'] == 'pytb'

# ################################################################################################################################
# ################################################################################################################################
