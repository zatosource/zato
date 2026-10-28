# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_GATEWAY, BAD_REQUEST, FORBIDDEN, GATEWAY_TIMEOUT, INTERNAL_SERVER_ERROR, NOT_FOUND, \
    REQUEST_TIMEOUT, SERVICE_UNAVAILABLE, TOO_MANY_REQUESTS, UNAUTHORIZED, UNPROCESSABLE_ENTITY

# Zato
from zato.common.audit_log.common import AuditClassification, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

# Markers meaning a failure is transient - resubmitting the message as-is can work
_transient_markers = (
    'timeout', 'timed out', 'connection', 'refused', 'unreachable', 'reset', 'unavailable', 'temporar',
    f'{REQUEST_TIMEOUT}', f'{TOO_MANY_REQUESTS}', f'{BAD_GATEWAY}', f'{SERVICE_UNAVAILABLE}', f'{GATEWAY_TIMEOUT}',
)

# What the status of a delivery an HL7 receiver answered with an AE or an AR opens with.
Ack_Rejected_Marker = 'HL7 ack rejected'

# Markers meaning a failure is permanent - the message needs to change before another attempt
_permanent_markers = (
    'validation', 'invalid', 'malformed', 'parse', 'schema', 'unauthorized', 'forbidden', 'not found', 'duplicate',
    Ack_Rejected_Marker.lower(),
    f'{BAD_REQUEST}', f'{UNAUTHORIZED}', f'{FORBIDDEN}', f'{NOT_FOUND}', f'{UNPROCESSABLE_ENTITY}',
)

# ################################################################################################################################

def derive_classification(outcome:'str', status:'str' = '', application_outcome:'str' = '') -> 'str':
    """ Derives the transient-vs-permanent classification of a failure out of its platform
    and application outcomes. Successful events and failures matching no known marker stay unclassified.
    """

    # Only failures are classified ..
    if outcome != AuditOutcome.Error:
        return ''

    # .. both outcome layers contribute to the match ..
    combined = f'{status} {application_outcome}'.lower()

    # .. a transient failure means resubmitting the message as-is can work ..
    for marker in _transient_markers:
        if marker in combined:
            out = AuditClassification.Transient
            break

    # .. a permanent one means the message needs to change first ..
    else:
        for marker in _permanent_markers:
            if marker in combined:
                out = AuditClassification.Permanent
                break

        # .. and anything unmatched stays unclassified.
        else:
            out = ''

    return out

# ################################################################################################################################

# The client errors that say the server could not take the request right now rather than that the request is wrong
_transient_client_errors = (REQUEST_TIMEOUT, TOO_MANY_REQUESTS)

# ################################################################################################################################

def derive_http_classification(status_code:'int') -> 'str':
    """ Classifies a rejection by the HTTP status it came with - a client error is permanent, except for the ones
    saying the server could not take the request right now, and a server error is transient.
    """

    # A server error is something the same request can get past later ..
    if status_code >= INTERNAL_SERVER_ERROR:
        out = AuditClassification.Transient

    # .. so is a client error that only says the server was busy or slow ..
    elif status_code in _transient_client_errors:
        out = AuditClassification.Transient

    # .. any other client error needs the request to change first ..
    elif status_code >= BAD_REQUEST:
        out = AuditClassification.Permanent

    # .. and anything below that is not a rejection at all.
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################
