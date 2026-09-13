# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.common import classify_transport_error
from zato.common.util.api import utcnow
from zato.server.metrics import get_error_source_from_status_class, get_status_code_class, \
    zato_rest_outgoing_request_duration_seconds, zato_rest_outgoing_requests_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.connection.http_soap.outgoing import BaseHTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

def push_metrics(wrapper:'BaseHTTPSOAPWrapper', start_time:'any_', status_code:'str') -> 'None':
    """ Updates outgoing REST metrics with duration, status class, and error source. The status is a response's
    HTTP code or, for a call that failed before any response arrived, its transport status, which the error
    source label then carries by name.
    """
    duration = (utcnow() - start_time).total_seconds()
    connection_name = wrapper.config['name']

    status_class = get_status_code_class(status_code)
    error_source = get_error_source_from_status_class(status_class, status_code)

    _ = zato_rest_outgoing_requests_total.labels(
        connection_name=connection_name,
        status_code=status_class,
        error_source=error_source,
    ).inc()

    _ = zato_rest_outgoing_request_duration_seconds.labels(
        connection_name=connection_name
    ).observe(duration)

# ################################################################################################################################

def push_transport_error_metrics(wrapper:'BaseHTTPSOAPWrapper', start_time:'any_', exception:'Exception') -> 'str':
    """ Counts a call that failed before any response arrived under its transport status and returns that status,
    so the audit log can write the same status the metrics counted.
    """
    transport_status = classify_transport_error(exception)
    push_metrics(wrapper, start_time, transport_status)

    return transport_status

# ################################################################################################################################
# ################################################################################################################################
