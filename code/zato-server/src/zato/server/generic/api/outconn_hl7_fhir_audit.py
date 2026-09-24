# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit pair an outgoing FHIR connection writes for each call - the request as it went out and what came back.

# stdlib
import json

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import classify_transport_error
from zato.common.audit_log.request_context import Key_Method, Key_Params, Key_Payload
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, stranydict, strdictnone

    fhirrejection = tuple[str, any_]

# ################################################################################################################################
# ################################################################################################################################

# The resource type of a failed response that carries an issue code
Operation_Outcome_Type = 'OperationOutcome'

# The keys of an OperationOutcome that say why a write was turned down
_resource_type_key = 'resourceType'
_issue_key         = 'issue'
_diagnostics_key   = 'diagnostics'

# The audit source a call's pair is written under - the connection's own traffic or its health checks
_source_by_is_health_check = {
    False: AuditSource.FHIR,
    True: AuditSource.FHIR_Health,
}

# ################################################################################################################################
# ################################################################################################################################

def get_fhir_rejection(response:'Response') -> 'fhirrejection':
    """ Why a write was turned down and what the server answered with - the status line with the text of the
    OperationOutcome the body carries, or with the body itself when it is not one, and the body as parsed.
    """
    body:'any_' = response.text
    reason = response.text

    try:
        parsed = json.loads(response.content.decode())
    except (ValueError, UnicodeDecodeError):
        parsed = None

    if isinstance(parsed, dict):
        body = parsed

        if parsed.get(_resource_type_key) == Operation_Outcome_Type:
            issues = parsed.get(_issue_key)
            reason = ''

            # A server names the reason under an optional key, so there may be nothing to read.
            if issues:
                first_issue = issues[0]

                if _diagnostics_key in first_issue:
                    reason = first_issue[_diagnostics_key]

    error = f'HTTP {response.status_code} {reason}'.strip()

    # Our response to produce
    out = error, body

    return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRAuditMixin:
    """ Writes the audit pair of one call - the client this is mixed into carries the config and the log.
    """

    zato_config: 'stranydict'
    zato_audit_log: 'AuditLog'
# ################################################################################################################################

    def _record_request(
        self,
        cid:'str',
        method:'str',
        path:'str',
        data:'strdictnone',
        params:'strdictnone',
        is_health_check:'bool',
        ) -> 'stranydict':
        """ The first event of a call's pair - the request as it went out, stored as the resubmit convention document.
        """
        outconn_name = self.zato_config['name']

        # The resource type is the leading path element - what the browser searches by (R.1)
        resource_type = path.strip('/').split('/')[0]

        attrs = {
            'resource_type': resource_type,
            'method': method.upper(),
        }

        # A read carries no body, a save carries the resource being written
        if data is None:
            request_body = ''
        else:
            request_body = dumps(data)

        if params is None:
            params = {}

        # The stored document is the resubmit convention - payload plus the method, the path and the
        # search parameters a per-hop resend needs to repeat the exact same call. A search whose
        # parameters were dropped would come back as every resource of its type rather than the one.
        stored_data = dumps({
            Key_Payload: request_body,
            Key_Method: method,
            'path': path,
            Key_Params: params,
        })

        _ = self.zato_audit_log.insert(
            _source_by_is_health_check[is_health_check],
            AuditEvent.Request_Sent,
            outconn_name,
            cid=cid,
            endpoint=f'{method.upper()} {path}',
            size=len(request_body),
            outcome=AuditOutcome.OK,
            data=stored_data,
            attrs=attrs,
        )

        return attrs

# ################################################################################################################################

    def _record_transport_error(
        self,
        cid:'str',
        exception:'Exception',
        duration_ms:'int',
        attrs:'stranydict',
        is_health_check:'bool',
        ) -> 'None':
        """ The second event of a call's pair when no response arrived - its status names how the call failed.
        """
        _ = self.zato_audit_log.insert(
            _source_by_is_health_check[is_health_check],
            AuditEvent.Response_Received,
            self.zato_config['name'],
            cid=cid,
            outcome=AuditOutcome.Error,
            status=classify_transport_error(exception),
            duration_ms=duration_ms,
            data=str(exception),
            attrs=attrs,
        )

# ################################################################################################################################

    def _record_response(
        self,
        cid:'str',
        response:'Response',
        application_outcome:'str',
        duration_ms:'int',
        attrs:'stranydict',
        is_health_check:'bool',
        ) -> 'None':
        """ The second event of a call's pair - the response with the HTTP status it came with in whole, so a 500 reads
        as itself, and the issue code of the OperationOutcome it carries, if any, as its application outcome.
        """
        if response.ok:
            outcome = AuditOutcome.OK
        else:
            outcome = AuditOutcome.Error

        _ = self.zato_audit_log.insert(
            _source_by_is_health_check[is_health_check],
            AuditEvent.Response_Received,
            self.zato_config['name'],
            cid=cid,
            outcome=outcome,
            application_outcome=application_outcome,
            status=f'{response.status_code} {response.reason}',
            size=len(response.content),
            duration_ms=duration_ms,
            data=response.text,
            attrs=attrs,
        )

# ################################################################################################################################

    def _get_application_outcome(self, response:'Response') -> 'str':
        """ The issue code of the OperationOutcome a failed response carries - `exception`, `not-found` - or nothing
        for a good response or one whose body is not an OperationOutcome, so a plain 503 counts by its status alone.
        """
        if response.ok:
            return ''

        try:
            parsed = json.loads(response.content.decode())
        except (ValueError, UnicodeDecodeError):
            return ''

        if not isinstance(parsed, dict):
            return ''

        if parsed.get('resourceType') != Operation_Outcome_Type:
            return ''

        issues = parsed.get('issue')
        if not issues:
            return ''

        out = issues[0].get('code', '')
        return out

# ################################################################################################################################
# ################################################################################################################################
