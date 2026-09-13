# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Prometheus labels an outgoing call's outcome turns into - a response's status class and where the error
# came from, and for a call that failed before any response arrived, the transport status by its own name,
# so a timeout, a refused connection and a TLS failure are three numbers rather than one.

# Zato
from zato.common.audit_log.common import transport_statuses, TransportStatus
from zato.server.metrics import get_error_source_from_status_class, get_status_code_class, Error_Source_Gateway, \
    Error_Source_None, Error_Source_Upstream, Status_Class_Transport

# ################################################################################################################################
# ################################################################################################################################

class TestStatusCodeClass:

    def test_a_numeric_code_reads_as_its_class(self) -> 'None':
        assert get_status_code_class('200') == '2xx'
        assert get_status_code_class('301') == '3xx'
        assert get_status_code_class('404') == '4xx'
        assert get_status_code_class('503') == '5xx'

    def test_every_transport_status_reads_as_the_transport_class(self) -> 'None':
        for transport_status in transport_statuses:
            assert get_status_code_class(transport_status) == Status_Class_Transport, transport_status

# ################################################################################################################################
# ################################################################################################################################

class TestErrorSource:

    def test_a_success_has_no_error_source(self) -> 'None':
        assert get_error_source_from_status_class('2xx') == Error_Source_None
        assert get_error_source_from_status_class('3xx') == Error_Source_None

    def test_a_response_with_an_error_code_is_the_gateways(self) -> 'None':
        assert get_error_source_from_status_class('4xx') == Error_Source_Gateway
        assert get_error_source_from_status_class('5xx') == Error_Source_Gateway

    def test_a_timeout_keeps_its_name(self) -> 'None':
        out = get_error_source_from_status_class(Status_Class_Transport, TransportStatus.Timeout)
        assert out == TransportStatus.Timeout

    def test_a_connection_error_keeps_its_name(self) -> 'None':
        out = get_error_source_from_status_class(Status_Class_Transport, TransportStatus.Connection_Error)
        assert out == TransportStatus.Connection_Error

    def test_a_tls_error_keeps_its_name(self) -> 'None':
        out = get_error_source_from_status_class(Status_Class_Transport, TransportStatus.TLS_Error)
        assert out == TransportStatus.TLS_Error

    def test_any_other_transport_error_keeps_its_name(self) -> 'None':
        out = get_error_source_from_status_class(Status_Class_Transport, TransportStatus.Error)
        assert out == TransportStatus.Error

    def test_a_transport_class_without_a_status_is_upstream(self) -> 'None':

        # A caller that does not say how the call failed gets the one name it always got
        assert get_error_source_from_status_class(Status_Class_Transport) == Error_Source_Upstream

    def test_a_status_the_audit_log_does_not_write_is_upstream(self) -> 'None':
        assert get_error_source_from_status_class(Status_Class_Transport, 'something-else') == Error_Source_Upstream

# ################################################################################################################################
# ################################################################################################################################
