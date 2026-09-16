# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from base64 import b64encode
from logging import getLogger
from time import monotonic
from traceback import format_exc

# fhirpy
from fhirpy import SyncFHIRClient
from fhirpy.base.exceptions import AuthorizationError, ForbiddenError, MultipleResourcesFound, OperationOutcome, ResourceNotFound
from fhirpy.base.utils import AttrDict

# requests
import requests

# Zato
from zato.common.api import HL7
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import classify_transport_error
from zato.common.bearer_token import normalize_scopes
from zato.common.hl7.fhir.fields import Outgoing_Config_Defaults, Outgoing_Int_Names
from zato.common.json_internal import dumps
from zato.common.pubsub.outgoing import OutgoingPublisher, OutgoingType
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, new_cid_server
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.ext.bunch import Bunch
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, stranydict, strdictnone
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_basic_auth = HL7.Const.FHIR_Auth_Type.Basic_Auth.id
_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# How many milliseconds one second holds - used when converting request durations
_ms_per_second = 1000

# The statuses the client tells apart, as fhirpy does - a good response, a not-modified one and the failures
# fhirpy raises a typed exception for, everything else being an OperationOutcome
_status_ok_min = 200
_status_ok_max = 300
_status_not_modified = 304
_status_unauthorized = 401
_status_forbidden = 403
_status_not_found = (404, 410)
_status_precondition_failed = 412

# The resource type of a failed response that carries an issue code
_operation_outcome_type = 'OperationOutcome'

# The path a ping and a health check read - what every FHIR server answers with its capabilities
_ping_path = '/CapabilityStatement'
_ping_method = 'get'

# The audit source a call's pair is written under - the connection's own traffic or its health checks
_source_by_is_health_check = {
    False: AuditSource.FHIR,
    True: AuditSource.FHIR_Health,
}

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_fhir_config_defaults = Outgoing_Config_Defaults

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_fhir_int_config_keys = Outgoing_Int_Names

# ################################################################################################################################
# ################################################################################################################################

class _HL7FHIRConnection(SyncFHIRClient):
    zato_config: 'stranydict'

    def __init__(self, config:'stranydict') -> 'None':

        self.zato_config = config
        self.zato_security_id = self.zato_config['security_id']
        self.zato_auth_type = self.zato_config['auth_type']

        # A connection whose audit log is on writes a request and a response event per call, and a health check
        # writes its pair whether or not the audit log is on, so the log itself is always at hand
        self.zato_is_audit_log_active = as_bool(self.zato_config['is_audit_log_active'])
        self.zato_audit_log = AuditLog(self.zato_config['server'].name)

        # This can be built in advance in case we are using Basic Auth
        if self.zato_auth_type == _basic_auth:
            self.zato_basic_auth_header = self.zato_get_basic_auth_header()
        else:
            self.zato_basic_auth_header = None

        # What a guaranteed delivery to this connection goes through. It is built from the connection's
        # id rather than its name because that is what a rename leaves alone.
        self.zato_publisher = OutgoingPublisher(
            self.zato_config['server'],
            OutgoingType.FHIR,
            self.zato_config['id'],
        )

        address = self.zato_config['address']
        super().__init__(address)

# ################################################################################################################################

    def publish(self, resource:'stranydict', **kwargs:'any_') -> 'PublishResult':
        """ Queues one FHIR document for delivery to this connection, returning as soon as it is stored.
        """

        # A document with no resource type has no path to be created under, so it could never
        # be delivered - it is refused here rather than left retrying in a queue forever.
        if 'resourceType' not in resource:
            raise Exception('A FHIR document to publish needs a resourceType')

        out = self.zato_publisher.publish(resource, **kwargs)
        return out

# ################################################################################################################################

    def _do_request( # noqa: PLR0913
        self,
        method:'str',
        path:'str',
        data:'strdictnone'=None,
        params:'strdictnone'=None,
        extra_headers:'strdictnone'=None,
        *,
        returning_status:'bool'=False,
        returning_response:'bool'=False,
        needs_audit:'bool'=True,
        is_health_check:'bool'=False,
        cid:'str'='',
        ) -> 'any_':
        """ Every fhirpy operation funnels through here - reads, saves, deletes and raw execute calls alike - which
        makes it the one place the audit pair is written from. The request is performed here rather than by fhirpy
        so that the response is in hand when the pair is written - its status line, its outcome and, on a failure,
        the issue code of the OperationOutcome it carries - and then the exceptions fhirpy raises for each status
        are raised exactly as fhirpy raises them, so no caller sees a change. A resubmit turns needs_audit off
        because it records its own events, linked to the original by the correlation id. A health check writes
        its pair under the connection's health source whether or not the connection's own audit log is on,
        and reads the response itself rather than what fhirpy would make of it.
        """
        headers = self._build_request_headers()
        if extra_headers:
            headers = {**headers, **extra_headers}

        url = self._build_request_url(path, params)

        # A health check is always written, the traffic a connection carries only when its audit log is on
        if is_health_check:
            needs_audit = True
        elif not self.zato_is_audit_log_active:
            needs_audit = False

        if needs_audit:
            if not cid:
                cid = new_cid_server()

            attrs = self._record_request(cid, method, path, data, is_health_check)
            request_start = monotonic()

            # A failure before any response arrived names how it failed - a timeout is a timeout.
            try:
                response = requests.request(method, url, json=data, headers=headers, **self.requests_config)
            except Exception as e:
                duration_ms = int((monotonic() - request_start) * _ms_per_second)
                self._record_transport_error(cid, e, duration_ms, attrs, is_health_check)

                raise

            # A response that came back is written with its status line and application outcome.
            duration_ms = int((monotonic() - request_start) * _ms_per_second)
            application_outcome = self._get_application_outcome(response)
            self._record_response(cid, response, application_outcome, duration_ms, attrs, is_health_check)

        # .. calls without auditing only send the request.
        else:
            response = requests.request(method, url, json=data, headers=headers, **self.requests_config)

        # A health check reads the response as it is
        if returning_response:
            return response

        self._raise_for_status(response)

        # A 304 carries no body to parse
        if response.status_code == _status_not_modified:
            r_data = None
        elif response.content:
            r_data = json.loads(response.content.decode(), object_hook=AttrDict)
        else:
            r_data = None

        if returning_status:
            out = (r_data, response.status_code)
        else:
            out = r_data

        return out

# ################################################################################################################################

    def _record_request(
        self,
        cid:'str',
        method:'str',
        path:'str',
        data:'strdictnone',
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

        # The stored document is the resubmit convention - payload plus the method
        # and path a per-hop resend needs to repeat the exact same call.
        stored_data = dumps({
            'payload': request_body,
            'method': method,
            'path': path,
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

        if parsed.get('resourceType') != _operation_outcome_type:
            return ''

        issues = parsed.get('issue')
        if not issues:
            return ''

        out = issues[0].get('code', '')
        return out

# ################################################################################################################################

    def _raise_for_status(self, response:'Response') -> 'None':
        """ The exceptions fhirpy 2.2.0 raises for each status - what every caller of this client expects.
        """
        status_code = response.status_code

        if _status_ok_min <= status_code < _status_ok_max:
            return

        if status_code == _status_not_modified:
            return

        content = response.content.decode()

        if status_code == _status_unauthorized:
            raise AuthorizationError(content)

        if status_code == _status_forbidden:
            raise ForbiddenError(content)

        if status_code in _status_not_found:
            raise ResourceNotFound(content)

        if status_code == _status_precondition_failed:
            raise MultipleResourcesFound(content)

        try:
            parsed_data = json.loads(content)
            if parsed_data['resourceType'] == _operation_outcome_type:
                raise OperationOutcome(resource=parsed_data)
            raise OperationOutcome(reason=content)
        except (KeyError, json.JSONDecodeError) as exc:
            raise OperationOutcome(reason=content) from exc

# ################################################################################################################################

    def _build_request_headers(self) -> 'stranydict':

        # This is constant
        headers = {
            'Accept': 'application/json'
        }

        # This is inherited from the parent class
        if self.extra_headers is not None:
            headers = {**headers, **self.extra_headers}

        # This is already available ..
        if self.zato_auth_type == _basic_auth:
            auth_header = self.zato_basic_auth_header

        # .. while this needs to be dynamically created ..
        elif self.zato_auth_type == _oauth:
            auth_header = self.zato_get_oauth_header()

        else:
            auth_header = None

        # .. now, it can be assigned ..
        if auth_header:
            headers['Authorization'] = auth_header

        # .. and the whole set of headers can be returned.
        return headers

# ################################################################################################################################

    def zato_get_basic_auth_header(self) -> 'str':

        username = self.zato_config['username']
        password = self.zato_config['secret']

        auth_header = f'{username}:{password}'
        auth_header = auth_header.encode('ascii')
        auth_header = b64encode(auth_header)
        auth_header = auth_header.decode('ascii')
        auth_header = f'Basic {auth_header}'

        return auth_header

# ################################################################################################################################

    def zato_get_oauth_header(self) -> 'str':

        # The server gives us access to security definitions and the bearer token manager
        server = self.zato_config['server'] # type: ParallelServer

        # Each OAuth definition specifies its own data format and scopes ..
        sec_def = server.security_facade.get_bearer_token_by_id(self.zato_security_id)
        data_format = sec_def['data_format']

        if scopes := sec_def.get('scopes'):
            scopes = normalize_scopes(scopes)
        else:
            scopes = ''

        # .. this returns the token from the server's cache or fetches a new one from the auth server ..
        result = server.bearer_token_manager.get_bearer_token_info_by_sec_def_id(self.zato_security_id, scopes, data_format)

        # .. and now the header can be built.
        out = f'Bearer {result.info.token}'
        return out

# ################################################################################################################################

    def zato_ping(self, cid:'str'='', *, is_health_check:'bool'=False) -> 'Response':
        """ Reads the server's CapabilityStatement, answering the response as it came - a health check reads its
        status itself and writes the pair under the connection's health source.
        """
        out = self._do_request(_ping_method, _ping_path, returning_response=True, is_health_check=is_health_check, cid=cid)
        out = cast_('Response', out)
        return out

# ################################################################################################################################

    def zato_delete_impl(self, reason:'str | None'=None) -> 'None':
        """ What the connection queue calls when this connection is deleted - it must exist
        because the inherited .delete is fhirpy's resource-level API, not a teardown hook,
        and there is nothing to release since each request opens its own HTTP connection.
        """

# ################################################################################################################################
# ################################################################################################################################

class OutconnHL7FHIRWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 FHIR servers.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.auth_url = config.address
        config.server = server
        super(OutconnHL7FHIRWrapper, self).__init__(config, 'HL7 FHIR', server)

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = _HL7FHIRConnection(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding an HL7 FHIR client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self, cid:'str'='', *, return_response:'bool'=False, needs_audit:'bool'=False) -> 'Response | None':
        """ Pings the server. A health check asks for the response and for the pair to be written under
        the connection's health source, the Dashboard's ping button for neither.
        """
        with self.client() as client:
            client = cast_('_HL7FHIRConnection', client)
            response = client.zato_ping(cid, is_health_check=needs_audit)

        if return_response:
            return response

# ################################################################################################################################
# ################################################################################################################################
