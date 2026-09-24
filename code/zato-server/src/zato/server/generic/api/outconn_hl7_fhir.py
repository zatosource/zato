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
from fhirpy.base.resource import serialize
from fhirpy.base.resource_protocol import get_resource_type_id_and_class
from fhirpy.base.utils import AttrDict

# requests
import requests

# Zato
from zato.common.api import HL7, HTTP_SOAP
from zato.common.audit_log.api import AuditLog
from zato.common.bearer_token import normalize_scopes
from zato.common.hl7.fhir.fields import Outgoing_Bool_Names, Outgoing_Config_Defaults, Outgoing_Int_Names
from zato.common.json_internal import dumps
from zato.common.pubsub.outgoing import Attempts_None, Key_Data, Key_Method, Key_Params, Key_Path, OutgoingPublisher, \
    OutgoingType, SendRejected, SendResult
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid_server
from zato.common.util.http_retry import RetryPolicy, send_with_retry
from zato.server.connection.queue import Wrapper
from zato.server.generic.api.outconn_hl7_fhir_audit import FHIRAuditMixin, get_fhir_rejection, Operation_Outcome_Type
from zato.server.generic.api.outconn_hl7_fhir_resource import HL7FHIRResource

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

# The path a ping and a health check read - what every FHIR server answers with its capabilities
_ping_path = '/CapabilityStatement'
_ping_method = 'get'

# What a retry loop of this connection's direct sends is called in the log
_retry_label = 'FHIR'

# The methods that write, which is what the connection's queue is for - a read always goes to the wire
_write_methods = frozenset(('POST', 'PUT', 'PATCH', 'DELETE'))

# A publication through publish() is created under the path its resource type names
_publish_method = 'POST'

# A request with no body stores an empty text in its envelope
_no_data_text = ''

_use_queue_field = HTTP_SOAP.Queue.Field_Use_Queue

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_fhir_config_defaults = Outgoing_Config_Defaults

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_fhir_int_config_keys = Outgoing_Int_Names

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_fhir_bool_config_keys = Outgoing_Bool_Names

# ################################################################################################################################
# ################################################################################################################################

def is_fhir_rejection(response:'Response') -> 'bool':
    """ Whether the server turned a write down - anything but a good response is a rejection, the direct attempt
    and the attempts from the queue agreeing on that.
    """
    if _status_ok_min <= response.status_code < _status_ok_max:
        return False

    out = response.status_code != _status_not_modified
    return out

# ################################################################################################################################
# ################################################################################################################################

class _HL7FHIRConnection(FHIRAuditMixin, SyncFHIRClient):
    zato_config: 'stranydict'

    # The correlation id of the service a copy of this client is handed to, so the calls a service makes
    # are audited and queued under the service's own id - the pooled client itself has none
    zato_cid = ''

    def __init__(self, config:'stranydict') -> 'None':

        self.zato_config = config
        self.zato_security_id = self.zato_config['security_id']
        self.zato_auth_type = self.zato_config['auth_type']

        # A connection whose audit log is on writes a request and a response event per call, and a health check
        # writes its pair whether or not the audit log is on, so the log itself is always at hand
        self.zato_is_audit_log_active = self.zato_config['is_audit_log_active']
        self.zato_audit_log = AuditLog(self.zato_config['server'].name)

        # Whether a write that did not go through waits in the connection's queue, and how a direct
        # send is tried again when the switch is off
        self.zato_use_queue = self.zato_config[_use_queue_field]
        self.zato_retry_policy = RetryPolicy.from_config(self.zato_config)

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
        """ Queues one FHIR document for delivery to this connection, returning as soon as it is stored - the same
        envelope a POST of the resource under the path its type names builds, with no direct attempt made.
        """

        # A document with no resource type has no path to be created under, so it could never
        # be delivered - it is refused here rather than left retrying in a queue forever.
        if 'resourceType' not in resource:
            raise Exception('A FHIR document to publish needs a resourceType')

        request = self._build_request_part(_publish_method, resource['resourceType'], resource, None)

        out = self.zato_publisher.publish_request('', Attempts_None, request, **kwargs)
        return out

# ################################################################################################################################

    def resource(self, resource_type:'any_', **kwargs:'any_') -> 'any_':
        """ A resource of this client - one that hands back what its save came back with, a SendResult included.
        """
        if isinstance(resource_type, str):
            out = HL7FHIRResource(self, resource_type=resource_type, **kwargs)
        else:
            out = resource_type(**kwargs)

        return out

# ################################################################################################################################

    def save(self, resource:'any_', fields:'any_'=None, *, _search_params:'any_'=None, _as_dict:'bool'=False) -> 'any_':
        """ Saves a resource the way fhirpy does, except that a save which went to the queue comes back as its SendResult.
        """
        response_data = super().save(resource, fields, _search_params=_search_params, _as_dict=True)

        if isinstance(response_data, SendResult):
            return response_data

        if _as_dict:
            return response_data

        out = resource.__class__(**response_data)
        return out

# ################################################################################################################################

    def patch(self, resource_type_or_resource_or_ref:'any_', id_or_ref:'any_'=None, **kwargs:'any_') -> 'any_':
        """ Patches a resource the way fhirpy does, except that a patch which went to the queue comes back as its SendResult
        rather than being read as the resource it would otherwise be turned into.
        """
        resource_type, resource_id, custom_resource_class = get_resource_type_id_and_class(
            resource_type_or_resource_or_ref, id_or_ref)

        if resource_id is None:
            raise TypeError('Resource `id` is required for patch operation')

        path = f'{resource_type}/{resource_id}'
        response_data = self._do_request('patch', path, data=serialize(kwargs, drop_nulls_from_dicts=False))

        if isinstance(response_data, SendResult):
            return response_data

        if custom_resource_class:
            out = custom_resource_class(**response_data)
        else:
            out = response_data

        return out

# ################################################################################################################################

    def _needs_queue(self, method:'str', is_health_check:'bool', returning_response:'bool') -> 'bool':
        """ Whether a request goes through the connection's queue - a write with the switch on does, a read,
        a ping and a health check never do.
        """
        if not self.zato_use_queue:
            return False

        if is_health_check or returning_response:
            return False

        out = method.upper() in _write_methods
        return out

# ################################################################################################################################

    def _build_request_part(self, method:'str', path:'str', data:'strdictnone', params:'strdictnone') -> 'stranydict':
        """ What the connection's queue stores of one request - enough to make the same call again.
        """
        if data is None:
            data_text = _no_data_text
        else:
            data_text = dumps(data)

        if params is None:
            params = {}

        out = {
            Key_Method: method.upper(),
            Key_Path: path,
            Key_Data: data_text,
            Key_Params: params,
        }

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
        """ Every fhirpy operation funnels through here - reads, saves, deletes and raw execute calls alike. A write
        with the queue switch on is handed to the connection's queue and comes back as a SendResult. Everything else
        goes to the wire under the connection's retry policy and comes back the way fhirpy answers - the parsed body,
        or the exception fhirpy raises for the status - so no caller sees a change. A resubmit turns needs_audit off
        because it records its own events, linked to the original by the correlation id. A health check writes
        its pair under the connection's health source whether or not the connection's own audit log is on,
        and reads the response itself rather than what fhirpy would make of it.
        """

        # The calls a service makes travel under the service's own correlation id
        if not cid:
            cid = self.zato_cid

        if self._needs_queue(method, is_health_check, returning_response):
            out = self._send_or_queue(cid, method, path, data, params)
            return out

        response = self._send(cid, method, path, data, params, extra_headers,
            needs_audit=needs_audit, is_health_check=is_health_check, needs_retry=True)

        # A health check reads the response as it is
        if returning_response:
            return response

        out = self._read_response(response, returning_status)
        return out

# ################################################################################################################################

    def _send_or_queue(self, cid:'str', method:'str', path:'str', data:'strdictnone', params:'strdictnone') -> 'SendResult':
        """ A write with the queue switch on - one direct attempt if the queue is empty, otherwise or on a rejection
        the request is queued, and the caller reads what happened off the result rather than catching anything.
        """
        request = self._build_request_part(method, path, data, params)

        # A send with no correlation id at all still needs one for the envelope and the audit log
        if not cid:
            cid = new_cid_server()

        def attempt() -> 'any_':
            response = self._send(cid, method, path, data, params, None, needs_audit=True, is_health_check=False,
                needs_retry=False)

            if is_fhir_rejection(response):
                error, body = get_fhir_rejection(response)
                raise SendRejected(error, body)

            out = self._read_response(response, False)
            return out

        out = self.zato_publisher.send_or_queue(cid, request, attempt)
        return out

# ################################################################################################################################

    def zato_send_from_queue(self, cid:'str', request:'stranydict') -> 'None':
        """ Makes one attempt to deliver a request the queue holds, raising when the server turned it down.
        """
        data_text = request[Key_Data]

        if data_text:
            data = json.loads(data_text)
        else:
            data = None

        response = self._send(cid, request[Key_Method], request[Key_Path], data, request[Key_Params], None,
            needs_audit=True, is_health_check=False, needs_retry=False)

        if is_fhir_rejection(response):
            error, body = get_fhir_rejection(response)
            raise SendRejected(error, body)

# ################################################################################################################################

    def _send( # noqa: PLR0913
        self,
        cid:'str',
        method:'str',
        path:'str',
        data:'strdictnone',
        params:'strdictnone',
        extra_headers:'strdictnone',
        *,
        needs_audit:'bool',
        is_health_check:'bool',
        needs_retry:'bool',
        ) -> 'Response':
        """ One call to the server, with its audit pair. The request is performed here rather than by fhirpy so that
        the response is in hand when the pair is written - its status line, its outcome and, on a failure, the issue
        code of the OperationOutcome it carries. A direct send is tried again under the connection's retry policy,
        an attempt from the queue is made once, the queue having a policy of its own.
        """
        headers = self._build_request_headers()
        if extra_headers:
            headers = {**headers, **extra_headers}

        url = self._build_request_url(path, params)

        def send() -> 'Response':
            out = requests.request(method, url, json=data, headers=headers, **self.requests_config)
            return out

        # A health check is always written, the traffic a connection carries only when its audit log is on
        if is_health_check:
            needs_audit = True
        elif not self.zato_is_audit_log_active:
            needs_audit = False

        if needs_audit:
            if not cid:
                cid = new_cid_server()

            attrs = self._record_request(cid, method, path, data, params, is_health_check)
            request_start = monotonic()

            # A failure before any response arrived names how it failed - a timeout is a timeout.
            try:
                response = self._send_with_policy(cid, send, needs_retry)
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
            response = self._send_with_policy(cid, send, needs_retry)

        return response

# ################################################################################################################################

    def _send_with_policy(self, cid:'str', send:'any_', needs_retry:'bool') -> 'Response':
        """ Runs one send, tried again under the connection's retry policy when asked to.
        """
        if needs_retry:
            out = send_with_retry(self.zato_retry_policy, send, cid, _retry_label)
        else:
            out = send()

        return out

# ################################################################################################################################

    def _read_response(self, response:'Response', returning_status:'bool') -> 'any_':
        """ What fhirpy makes of a response - the exception its status stands for, or its parsed body.
        """
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

    def _raise_for_status(self, response:'Response') -> 'None':
        """ The exceptions fhirpy 2.2.0 raises for each status - what every caller of this client expects.
        The response the status came on travels with the exception, the exception class alone not
        saying which status it was.
        """
        try:
            self._do_raise_for_status(response)
        except Exception as e:
            e.zato_response = response
            raise

# ################################################################################################################################

    def _do_raise_for_status(self, response:'Response') -> 'None':
        """ Raises what fhirpy raises for one status, with nothing said about where it is raised from.
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
            if parsed_data['resourceType'] == Operation_Outcome_Type:
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
