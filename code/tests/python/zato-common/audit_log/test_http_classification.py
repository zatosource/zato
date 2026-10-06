# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_GATEWAY, BAD_REQUEST, CONFLICT, FORBIDDEN, GATEWAY_TIMEOUT, GONE, INTERNAL_SERVER_ERROR, \
    NOT_FOUND, NOT_MODIFIED, OK, REQUEST_TIMEOUT, SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS, UNAUTHORIZED, \
    UNPROCESSABLE_ENTITY

# Zato
from zato.common.audit_log.common import derive_http_classification, AuditClassification

# ################################################################################################################################
# ################################################################################################################################

class TestHTTPClassification:
    """ How a rejection is classified by the HTTP status it came with - the status alone, never the
    wording of the body, is what says whether another attempt with the same request can get past it.
    """

    def test_a_server_error_is_transient(self) -> 'None':
        for status_code in (INTERNAL_SERVER_ERROR, BAD_GATEWAY, SERVICE_UNAVAILABLE, GATEWAY_TIMEOUT):
            assert derive_http_classification(status_code) == AuditClassification.Transient, status_code

# ################################################################################################################################

    def test_a_server_that_was_busy_or_slow_is_transient(self) -> 'None':
        for status_code in (REQUEST_TIMEOUT, TOO_MANY_REQUESTS):
            assert derive_http_classification(status_code) == AuditClassification.Transient, status_code

# ################################################################################################################################

    def test_any_other_client_error_is_permanent(self) -> 'None':
        for status_code in (BAD_REQUEST, UNAUTHORIZED, FORBIDDEN, NOT_FOUND, CONFLICT, GONE, UNPROCESSABLE_ENTITY):
            assert derive_http_classification(status_code) == AuditClassification.Permanent, status_code

# ################################################################################################################################

    def test_a_status_that_is_not_a_rejection_is_not_classified(self) -> 'None':
        for status_code in (OK, NOT_MODIFIED):
            assert derive_http_classification(status_code) == '', status_code

# ################################################################################################################################
# ################################################################################################################################
