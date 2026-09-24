# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# requests
from requests import Response as _RequestsResponse
from requests.adapters import HTTPAdapter
from requests.sessions import Session as RequestsSession

# Zato
from zato.common.api import CONTENT_TYPE, MISC, NotGiven, URL_TYPE, Wrapper_Name_Prefix_List
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import TransportStatus
from zato.common.bearer_token import normalize_scopes
from zato.common.exception import Inactive, BackendInvocationError
from zato.common.pubsub.outgoing import http_soap_outgoing_types, OutgoingPublisher
from zato.common.soap.common import Content_Type as SOAP_Content_Type
from zato.common.typing_ import cast_
from zato.common.util.api import get_component_name, utcnow
from zato.common.util.config import extract_param_placeholders
from zato.common.util.http_retry import RetryPolicy, send_with_retry
from zato.common.util.tls_verify import resolve_tls_verify
from zato.server.connection.http_soap.outgoing.audit import insert_audit_event
from zato.server.connection.http_soap.outgoing.auth import AuthMixin
from zato.server.connection.http_soap.outgoing.common import logger, Allow_Redirects, Default_Content_Type, HTTPSAdapter, \
    Masked_Config_Fields, Masked_Value, Minimum_Pool_Size, Response, _connection_statuses, _get_body_length, _OAuth, \
    _rest_retry_label, _retry
from zato.server.connection.http_soap.outgoing.metrics import push_metrics, push_transport_error_metrics
from zato.server.connection.http_soap.outgoing.ping import ping, Default_Ping_Path
from zato.server.connection.http_soap.outgoing.rest_call import RESTCallMixin
from zato.server.connection.http_soap.outgoing.soap import SOAPMixin

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone, stranydict, strlist, strstrdict
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################

class BaseHTTPSOAPWrapper(AuthMixin):
    """ Base class for HTTP/SOAP connection wrappers.
    """
    def __init__(
        self,
        config, # type: stranydict
        server=None # type: ParallelServer | None
    ) -> 'None':
        self.config = config

        # A connection with no timeout configured means no timeout at all, which requests spells as
        # None. A zero handed to requests is not an absent timeout, it is one that expires before
        # the socket can connect, so every request through such a connection would fail outright.
        self.config['timeout'] = float(self.config['timeout']) if self.config['timeout'] else None
        self.config_no_sensitive = self._get_config_no_sensitive()
        self.server = cast_('ParallelServer', server)
        self.session = RequestsSession()

        # The connection's configured pool size decides how many connections the adapters keep alive.
        pool_size = self._get_pool_size()

        self.https_adapter = HTTPSAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
        self.session.mount('https://', self.https_adapter)

        # Plain HTTP needs the same treatment - mounting the sized adapter only under https
        # would leave every non-TLS connection on the default pool.
        self.session.mount('http://', HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size))
        self._component_name = get_component_name()
        self.default_content_type = self.get_default_content_type()

        self.address = ''
        self.path_params:'strlist' = []
        self.base_headers:'strstrdict' = {}
        self.sec_type = self.config['sec_type']

        # Only user-defined outgoing REST and SOAP connections go to the audit log -
        # internal ones and wrapper-prefixed ones would only flood it.
        is_wrapper_name = self.config['name'].startswith(tuple(Wrapper_Name_Prefix_List))
        self.can_audit = (server is not None) and (not self.config['is_internal']) and (not is_wrapper_name)

        # A connection whose audit log was turned off explicitly does not write its traffic, though its health
        # check's pings are still written, because a check nobody can see is not a check - so the log is opened
        # for every connection that may write at all. Read through self.server rather than the argument -
        # a connection only audits when it was given a server, so by this point the two are the same thing
        # and self.server is the one already narrowed to a ParallelServer.
        if self.can_audit:
            self.audit_log = AuditLog(self.server.name)
            self.needs_audit = self.config['is_audit_log_active']
        else:
            self.needs_audit = False

        self.set_address_data()
        self.set_auth()

# ################################################################################################################################

    def _get_config_no_sensitive(self) -> 'stranydict':
        """ Returns a copy of this connection's configuration that is safe to log.

        Whatever a connection keeps its secrets in is masked - the password column, the security
        definition it carries whole, and the declarative request rows, which hold whatever was
        typed into a header, a query parameter or a body.
        """
        out = deepcopy(self.config)

        for name in Masked_Config_Fields:
            if name in out:
                out[name] = Masked_Value

        return out

# ################################################################################################################################

    def _get_pool_size(self) -> 'int':
        """ Returns how many connections this wrapper's adapters keep pooled.

        A pool of zero is not a smaller pool, it is one that discards every connection, so anything
        below the floor falls back to the shared default rather than being honoured literally.
        """
        pool_size = self.config['pool_size']

        # A connection created or edited through the dashboard brings its pool size in as form input,
        # i.e. as text, whereas one read from the ODB already has it as a number.
        if pool_size:
            pool_size = int(pool_size)
        else:
            pool_size = MISC.DEFAULT_HTTP_POOL_SIZE

        if pool_size < Minimum_Pool_Size:
            pool_size = MISC.DEFAULT_HTTP_POOL_SIZE

        out = pool_size
        return out

# ################################################################################################################################

    def _push_metrics(self, start_time:'any_', status_code:'str') -> 'None':
        push_metrics(self, start_time, status_code)

# ################################################################################################################################

    def _insert_audit_event(
        self,
        cid:'str',
        event_type:'str',
        endpoint:'str',
        outcome:'str',
        data:'any_',
        status:'str' = '',
        method:'str' = '',
        *,
        is_health_check:'bool' = False,
        application_outcome:'str' = '',
        address:'str' = '',
        qs_params:'dictnone' = None,
        user_headers:'dictnone' = None,
        redacted:'strlist | None' = None,
    ) -> 'None':
        insert_audit_event(self, cid, event_type, endpoint, outcome, data, status, method, is_health_check=is_health_check,
            application_outcome=application_outcome,
            address=address, qs_params=qs_params, user_headers=user_headers, redacted=redacted)

# ################################################################################################################################
# ################################################################################################################################

    def _get_retry_policy(self, kwargs:'stranydict') -> 'RetryPolicy':
        """ Returns the retry policy for one invocation, with an explicit call argument winning
        over what the connection is configured with.

        The four settings are removed from kwargs whether or not they were given, because whatever
        is left there is handed straight to requests, which would reject a keyword it does not know.
        """
        overrides = {}

        for name in _retry.FieldList:
            value = kwargs.pop(name, None)

            # An absent override has to stay absent rather than become a None that would shadow
            # the connection's own value.
            if value is not None:
                overrides[name] = value

        if not overrides:
            return RetryPolicy.from_config(self.config)

        config = dict(self.config)
        config.update(overrides)

        out = RetryPolicy.from_config(config)
        return out

# ################################################################################################################################

    def invoke_http(
        self,
        cid:'str',
        method:'str',
        address:'str',
        data:'any_',
        headers:'strstrdict',
        hooks:'any_',
        *args:'any_',
        **kwargs:'any_'
    ) -> '_RequestsResponse':

        # A connection whose password was never provided has nothing to authenticate with,
        # so it says so here rather than sending a request that carries a placeholder.
        if self.missing_password:
            msg = f'Connection `{self.config["name"]}` has no password -> `{self.missing_password}`'
            raise BackendInvocationError(cid, msg, needs_msg=True)

        # Record start time for metrics
        start_time = utcnow()

        # Local variables
        json = kwargs.pop('json', None)

        # What to verify against - the process-wide skip, the connection's own flag and any pinned
        # CA bundle all resolve in one place, shared with the declarative SOAP path.
        tls_verify = resolve_tls_verify(self.config)

        # A mutual-TLS endpoint needs our client certificate, whose file is mounted into the
        # container - a single PEM holding both the certificate and its key, or a separate pair.
        tls_client_cert = self._get_tls_client_cert()

        # This is optional and, if not given, we will use the security configuration from self.config
        sec_def_name = kwargs.pop('sec_def_name', NotGiven)

        # If we have a security definition name on input, it must be a Bearer token (OAuth)
        if sec_def_name is not NotGiven:
            _sec_type = _OAuth
        else:
            sec_def_name = self.config['security_name']
            _sec_type = self.sec_type

        # Force type hints
        sec_def_name = cast_('str', sec_def_name)

        # Reusable
        is_bearer_token = _sec_type == _OAuth

        # OAuth scopes can be provided on input even if we do not have a Bearer token definition attached,
        # which is why we .pop them here, to make sure they do not propagate to the requests library.
        scopes = kwargs.pop('auth_scopes', '')

        try:

            # Bearer tokens are obtained dynamically or statically ..
            if is_bearer_token:

                # .. this is reusable ..
                sec_def = self.server.security_facade.get_bearer_token_by_name(sec_def_name)

                # .. static tokens live in the password column, while definitions created
                # .. before the token moved there keep it in the opaque attributes ..
                static_token = sec_def.get('static_token') or ''
                if (not static_token) and sec_def.get('is_static_token'):
                    static_token = sec_def['password']

                # .. static tokens have their value defined directly in the definition ..
                if static_token:

                    # .. build the header from the static definition fields ..
                    static_header = sec_def['static_header']
                    static_prefix = sec_def['static_prefix']

                    if static_prefix:
                        headers[static_header] = f'{static_prefix} {static_token}'
                    else:
                        headers[static_header] = static_token

                    token_is_cache_hit = None

                else:

                    # .. each OAuth definition will use a specific data format ..
                    data_format = sec_def['data_format']

                    # .. otherwise, we can check if they are provided in the security definition itself ..
                    if not scopes:
                        scopes = sec_def.get('scopes')
                        if scopes is None:
                            scopes = ''
                        scopes = normalize_scopes(scopes)

                    # .. get a Bearer token ..
                    result = self._get_bearer_token_auth(sec_def_name, scopes, data_format)

                    # .. populate headers ..
                    headers['Authorization'] = f'Bearer {result.info.token}'

                    token_is_cache_hit = result.is_cache_hit

                # This is needed by request
                auth = None

            # .. we enter here if this is not a Bearer token definition ..
            else:

                # .. otherwise, the credentials will have been already obtained ..
                auth = self.requests_auth

                # .. we have no token to report about.
                token_is_cache_hit = None

            # .. how much we are about to send ..
            data_length = _get_body_length(data)

            # .. basic details about what we are sending - the query string and the body are not
            # .. among them, the audit log being where a connection records what it sent ..
            message = f'REST out -> cid={cid}; {method} {address}; name:{self.config["name"]}' + \
                  f'; len={data_length}; sec={sec_def_name} ({_sec_type})'

            # .. optionally, log details of the Bearer token ..
            if is_bearer_token:
                message += f'; tok-from-cache={token_is_cache_hit}'

            # .. log the information about our request ..
            logger.info(message)

            # .. an explicit call argument overrides what the connection is configured with,
            # .. so the four settings are taken out of kwargs before the request sees them ..
            retry_policy = self._get_retry_policy(kwargs)

            def send() -> '_RequestsResponse':

                # .. do send it ..
                response = self.session.request(
                    method, address, data=data, json=json, auth=auth, headers=headers, hooks=hooks,
                    verify=tls_verify, cert=tls_client_cert, timeout=self.config['timeout'],
                    allow_redirects=Allow_Redirects, *args, **kwargs)

                # Update metrics
                self._push_metrics(start_time, str(response.status_code))

                # .. log what we received ..
                msg = f'REST out ← cid={cid}; {response.status_code} time={response.elapsed}; len={len(response.text)}'
                logger.info(msg)

                return response

            return send_with_retry(retry_policy, send, cid, _rest_retry_label)

        except Exception as e:

            # .. a call that failed before any response arrived is classified once, and the classification
            # .. travels with the error raised, so the audit log writes the same status the metrics counted ..
            transport_status = push_transport_error_metrics(self, start_time, e)

            if transport_status == TransportStatus.Timeout:
                msg = f'Timeout error: {e}'
            elif transport_status in _connection_statuses:
                msg = f'Connection error: {e}'
            else:
                raise

            raise BackendInvocationError(cid, msg, needs_msg=True, transport_status=transport_status)

# ################################################################################################################################
# ################################################################################################################################

    def ping(
        self,
        cid:'str',
        return_response:'bool'=False,
        log_verbose:'bool'=False,
        *,
        ping_path:'str'=Default_Ping_Path,
        needs_audit:'bool | None'=None,
    ) -> 'any_':
        out = ping(self, cid, return_response, log_verbose, ping_path=ping_path, needs_audit=needs_audit)
        return out

# ################################################################################################################################

    def get_default_content_type(self) -> 'str':
        """ Returns the content type a request goes out with when its caller does not name one.
        """
        # An explicit content type on the connection is the whole answer, whatever else is configured.
        if content_type := self.config['content_type']:
            return content_type

        transport = self.config['transport']

        # A SOAP connection's content type is decided by its SOAP version, whatever data format it carries
        if transport == URL_TYPE.SOAP:
            out = SOAP_Content_Type[self.config['soap_version']]

        # A plain HTTP connection that names a data format at all is a JSON one, that being the only
        # format the outgoing side serialises to.
        elif transport == URL_TYPE.PLAIN_HTTP and self.config['data_format']:
            out = CONTENT_TYPE['JSON']

        else:
            out = Default_Content_Type

        return out

# ################################################################################################################################

    def _create_headers(self, cid:'str', user_headers:'strstrdict', now:'str'='') -> 'strstrdict':

        # The content type is taken out of the user headers below, so the work is done on a copy -
        # a caller that reuses one dict across calls would otherwise lose it after the first one.
        user_headers = dict(user_headers)

        headers = dict(self.base_headers)
        headers.update({
            'X-Zato-CID': cid,
            'X-Zato-Component': self._component_name,
            'X-Zato-Msg-TS': now or utcnow().isoformat(),
        })

        if self.config['transport'] == URL_TYPE.SOAP:
            self._add_soap_action(headers)

        content_type = user_headers.pop('Content-Type', self.default_content_type)
        if content_type:
            headers['Content-Type'] = content_type

        headers.update(user_headers)

        return headers

# ################################################################################################################################
# ################################################################################################################################

    def set_address_data(self) -> 'None':
        """Sets the full address to invoke and parses input URL's configuration,
        to extract any named parameters that will have to be passed in by users
        during actual calls to the resource.
        """

        # Set the full adddress ..
        self.address = '{}{}'.format(self.config['address_host'], self.config['address_url_path'])

        # .. and parse out placeholders for path parameters.
        for param_name in extract_param_placeholders(self.config['address_url_path']):
            self.path_params.append(param_name[1:-1])

# ################################################################################################################################
# ################################################################################################################################

class HTTPSOAPWrapper(BaseHTTPSOAPWrapper, SOAPMixin, RESTCallMixin):
    """ A thin wrapper around the API exposed by the 'requests' package.
    """
    def __init__(
        self,
        server, # type: ParallelServer
        config, # type: stranydict
    ) -> 'None':
        super(HTTPSOAPWrapper, self).__init__(config, server)
        self.server = server

        # A REST or a SOAP connection can queue what its endpoint turned down - the publisher
        # is given the connection's id because that is what a rename of the connection leaves alone.
        outgoing_type = http_soap_outgoing_types[config['transport']]
        self.publisher = OutgoingPublisher(server, outgoing_type, config['id'])

# ################################################################################################################################

    def __str__(self) -> 'str':
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    __repr__ = __str__

# ################################################################################################################################
# ################################################################################################################################

    def _impl(self) -> 'RequestsSession':
        """ Returns the self.session object through which access to HTTP/SOAP resources is provided.
        """
        return self.session

    impl = property(fget=_impl, doc=_impl.__doc__)

# ################################################################################################################################

    def _enforce_is_active(self) -> 'None':
        if not self.config['is_active']:
            raise Inactive(self.config['name'])

# ################################################################################################################################
# ################################################################################################################################

RESTWrapper = HTTPSOAPWrapper

# The response class is what callers of the wrapper import from here, the way they always have
Response = Response

# ################################################################################################################################
# ################################################################################################################################
