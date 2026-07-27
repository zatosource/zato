# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy
from http.client import OK
from io import StringIO
from logging import DEBUG, getLogger
from traceback import format_exc
from urllib.parse import quote, urlencode

# requests
from requests import Response as _RequestsResponse
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout
from requests.sessions import Session as RequestsSession
from requests.utils import super_len

# requests-ntlm
from requests_ntlm import HttpNtlmAuth

# requests-toolbelt
from requests_toolbelt import MultipartEncoder

# Zato
from zato.common.api import ContentType, CONTENT_TYPE, DATA_FORMAT, EnvVariable, HTTP_SOAP, MISC, NotGiven, SEC_DEF_TYPE, \
    URL_TYPE, Wrapper_Name_Prefix_List
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.exception import BadRequest, Inactive, BackendInvocationError
from zato.common.json_ import dumps, loads
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import Content_Type as SOAP_Content_Type, Envelope_NS, SOAP_Action_Header, SOAPFault, \
    SOAPVersion
from zato.common.marshal_.api import extract_model_class, is_list, Model
from zato.common.typing_ import cast_
from zato.common.util.api import get_component_name, utcnow
from zato.common.util.config import extract_param_placeholders
from zato.common.util.http_retry import RetryPolicy, send_with_retry
from zato.common.util.open_ import open_rb
from zato.common.util.tls_verify import resolve_tls_verify
from zato.server.connection.http_soap.invocation import build_jsonata_context, build_soap_jsonata_context, \
    evaluate_soap_headers, maybe_run_callback, maybe_run_fault_callback, maybe_run_soap_callback, \
    merge_declarative_request, merge_declarative_soap_request
from zato.server.metrics import get_error_source_from_status_class, get_status_code_class, \
    zato_rest_outgoing_request_duration_seconds, zato_rest_outgoing_requests_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.bearer_token import BearerTokenInfoResult
    from zato.common.typing_ import any_, callnone, dictnone, list_, stranydict, strbytes, strdictnone, strlist, strnone, \
        strstrdict, type_
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigDict
    callnone = callnone
    ConfigDict = ConfigDict
    SASession = SASession
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_rest')
has_debug = logger.isEnabledFor(DEBUG)

# ################################################################################################################################
# ################################################################################################################################

# The envelope each SOAP version's legacy string-formatting path wraps the outgoing data in.
# Templates are shared by every connection, so they live here rather than being rebuilt per wrapper.
SOAP_Envelope_Template = {

    SOAPVersion.V11: """<?xml version="1.0" encoding="utf-8"?>
<s11:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s11="%s">
  {header}
  <s11:Body>{data}</s11:Body>
</s11:Envelope>""" % (Envelope_NS[SOAPVersion.V11],),

    SOAPVersion.V12: """<?xml version="1.0" encoding="utf-8"?>
<s12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s12="%s">{header}
  <s12:Body>{data}</s12:Body>
</s12:Envelope>""" % (Envelope_NS[SOAPVersion.V12],),
}

# ################################################################################################################################
# ################################################################################################################################

# The smallest pool a connection may configure. A pool of zero is not a small pool, it is one that
# closes every connection the moment it is done with, so a stored zero means "never configured"
# rather than "keep nothing".
Minimum_Pool_Size = 1

_API_Key = SEC_DEF_TYPE.APIKEY
_Basic_Auth = SEC_DEF_TYPE.BASIC_AUTH
_MTLS = SEC_DEF_TYPE.MTLS
_NTLM = SEC_DEF_TYPE.NTLM
_OAuth = SEC_DEF_TYPE.OAUTH
_SPNEGO = SEC_DEF_TYPE.SPNEGO

_retry = HTTP_SOAP.Retry
_invocation = HTTP_SOAP.Invocation

# What a retry of an outgoing REST request is called in the logs.
_rest_retry_label = 'REST out'

# What a connection sends when it has said nothing at all about its content type - neither an explicit
# one, nor a SOAP version, nor a data format.
Default_Content_Type = 'text/plain'

# An outgoing request goes to the address its connection is configured with and to no other one,
# so a redirect, which names a different address, is not followed.
Allow_Redirects = False

# What a configuration field's value is replaced with before the configuration is logged.
Masked_Value = '***'

# The configuration fields that never reach a log. The password is the plain one, and the
# declarative rows are where a token typed into a header, a query parameter or a body ends up.
Masked_Config_Fields = (
    'password',
    'salt',
    'security',
    'body_credentials',
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Data,
)

# ################################################################################################################################
# ################################################################################################################################

def _get_body_length(data:'any_') -> 'int':
    """ Returns how long a request body is, for the log message that describes the request.

    Strings and bytes answer directly. Everything else - a multipart encoder, a file object,
    a stream - is measured by the same function that requests itself uses to decide what
    Content-Length to send, and it answers zero for a body whose size cannot be known in
    advance. A multipart encoder in particular publishes its length as a property rather than
    through __len__, so len() applied to one raises rather than returning anything.
    """
    if isinstance(data, (str, bytes)):
        out = len(data)
    else:
        out = super_len(data)

    return out

# ################################################################################################################################

def _needs_serialization(data:'any_') -> 'bool':
    """ Says whether a request body still has to be serialized on its way out.

    A string is sent exactly as it stands, and so is a multipart encoder, which is an already
    encoded body that carries its own content type. Anything else - a dict, a list, a model -
    is serialized according to the connection's data format.
    """
    if isinstance(data, (str, MultipartEncoder)):
        out = False
    else:
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

class Response(_RequestsResponse):

    # What the raw body turned into, which is genuinely of no one shape - the text as it arrived when
    # nothing says otherwise, whatever JSON parsed into when the response is JSON, and a model
    # instance or a list of them when the caller named a model class.
    data: 'any_'

    zato_method: 'str'
    zato_address: 'str'
    zato_qs_params: 'strdictnone' = None

# ################################################################################################################################
# ################################################################################################################################

class HTTPSAdapter(HTTPAdapter):
    """ An adapter which exposes a method for clearing out the underlying pool. Useful with HTTPS as it allows to update TLS
    material on the fly.
    """
    def clear_pool(self):
        self.poolmanager.clear()

# ################################################################################################################################
# ################################################################################################################################

class SPNEGOAuth:
    """ A requests auth object that acquires Kerberos credentials from a keytab lazily,
    on the first request, so that a connection can be created and edited before its keytab
    is mounted into the container.
    """
    def __init__(self, principal:'str', keytab_path:'str', target_spn:'strnone', needs_delegation:'bool') -> 'None':
        self.principal = principal
        self.keytab_path = keytab_path
        self.target_spn = target_spn
        self.needs_delegation = needs_delegation
        self._impl = None

    def _build_impl(self) -> 'any_':

        # Imported here because the underlying gssapi package needs system Kerberos
        # libraries which may be absent from installations that never use SPNEGO.
        import gssapi
        from requests_gssapi import HTTPSPNEGOAuth

        # Credentials are acquired explicitly from the keytab, so no external kinit
        # or credential cache is needed - gssapi re-acquires tickets from the keytab
        # on its own when they expire.
        creds = gssapi.Credentials(
            name=gssapi.Name(self.principal, gssapi.NameType.kerberos_principal),
            store={'client_keytab': self.keytab_path},
            usage='initiate',
        )

        # The remote service's SPN is optional - when it is not given,
        # it is derived from the target host name.
        if self.target_spn:
            target_name = gssapi.Name(self.target_spn, gssapi.NameType.hostbased_service)
        else:
            target_name = None

        # The library's own annotation says this is a string, which it never is - it takes a GSSAPI
        # name object or nothing at all, and deriving the name from the target host is exactly what
        # passing nothing means.
        target_name = cast_('str', target_name)

        return HTTPSPNEGOAuth(creds=creds, target_name=target_name, delegate=self.needs_delegation)

    def __call__(self, request:'any_') -> 'any_':

        # The underlying auth object is built on first use - the keytab has to exist
        # only when the connection is actually invoked, not when it is configured.
        if self._impl is None:
            self._impl = self._build_impl()

        return self._impl(request)

# ################################################################################################################################
# ################################################################################################################################

class BaseHTTPSOAPWrapper:
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
        self.needs_audit = (server is not None) and (not self.config['is_internal']) and (not is_wrapper_name)

        # A connection whose audit log was turned off explicitly does not write events either
        if self.needs_audit:
            self.needs_audit = self.config['is_audit_log_active']

        # Read through self.server rather than the argument - a connection only audits when it was
        # given a server, so by this point the two are the same thing and self.server is the one
        # already narrowed to a ParallelServer.
        if self.needs_audit:
            self.audit_log = AuditLog(self.server.name)

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
        """ Updates outgoing REST metrics with duration, status class, and error source.
        """
        duration = (utcnow() - start_time).total_seconds()
        connection_name = self.config['name']

        status_class = get_status_code_class(status_code)
        error_source = get_error_source_from_status_class(status_class)

        _ = zato_rest_outgoing_requests_total.labels(
            connection_name=connection_name,
            status_code=status_class,
            error_source=error_source,
        ).inc()

        _ = zato_rest_outgoing_request_duration_seconds.labels(
            connection_name=connection_name
        ).observe(duration)

# ################################################################################################################################

    def _insert_audit_event(
        self,
        cid:'str',
        event_type:'str',
        endpoint:'str',
        outcome:'str',
        data:'any_',
    ) -> 'None':
        """ Writes one audit event describing a request sent to or a response received
        from an outgoing REST or SOAP connection.
        """

        # Payloads reach here in whatever shape their caller had them in - bytes as they went on the
        # wire, which are decoded with what cannot be decoded replaced ..
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='replace')

        # .. or an object such as a dict or a multipart encoder, which is described rather than decoded.
        elif not isinstance(data, str):
            data = str(data)

        # .. the source depends on the connection's transport ..
        if self.config['transport'] == URL_TYPE.PLAIN_HTTP:
            source = AuditSource.REST_Outgoing
        else:
            source = AuditSource.SOAP_Outgoing

        # .. now, write out the event.
        self.audit_log.insert(
            source,
            event_type,
            self.config['name'],
            cid=cid,
            endpoint=endpoint,
            size=len(data),
            outcome=outcome,
            data=data,
        )

# ################################################################################################################################

    def _check_password(self) -> 'None':
        """ Notes whether this connection's password is still the placeholder that an import leaves
        behind for a value whose environment variable was not set. Such a connection has no
        credentials at all, which is what invoking it reports rather than sending the placeholder.
        """
        self.missing_password = ''

        # A connection may have no password to begin with - a definition that authenticates
        # with a certificate or a keytab is the usual case.
        password = self.config['password']

        if password:
            if password.startswith(EnvVariable.Missing_Value_Prefix):
                self.missing_password = password
                logger.warning('Connection `%s` has no password, its value was never provided -> `%s`',
                    self.config['name'], password)

# ################################################################################################################################

    def set_auth(self) -> 'None':

        # Local variables
        self.requests_auth = None
        self.username = None

        # The headers that the security definition contributes are rebuilt on each call, so the set
        # always describes the definition as it stands now and not as it once stood.
        base_headers:'strstrdict' = {}

        # The SOAP client is built lazily and dropped here so security changes take effect on the next call.
        self._soap_client:'SOAPClient | None' = None

        self._check_password()

        # #######################################
        #
        # API Keys
        #
        # #######################################
        if self.sec_type == _API_Key:
            username = self.config['orig_username']
            if not username:
                username = self.config['username']
            base_headers[username] = self.config['password']

        # #######################################
        #
        # HTTP Basic Auth
        #
        # #######################################
        elif self.sec_type in {_Basic_Auth}:
            self.requests_auth = self.auth
            self.username = self.requests_auth[0]

        # #######################################
        #
        # NTLM
        #
        # #######################################
        elif self.sec_type == _NTLM:
            _username, _password = self.auth
            _requests_auth = HttpNtlmAuth(_username, _password)
            self.requests_auth = _requests_auth
            self.username = _username

        # #######################################
        #
        # mTLS
        #
        # #######################################
        elif self.sec_type == _MTLS:

            # The definition's certificate material replaces whatever TLS details
            # the connection itself may have been configured with.
            self.config['tls_client_cert'] = self.config['cert_path']
            self.config['tls_client_key'] = self.config['key_path']

            # Pooled connections were established with the material that was in place when they were
            # opened, so they are discarded here - a definition edited to present a different
            # certificate would otherwise keep presenting the previous one for as long as
            # a pooled connection lasted.
            self.https_adapter.clear_pool()

        # #######################################
        #
        # Kerberos (SPNEGO)
        #
        # #######################################
        elif self.sec_type == _SPNEGO:

            principal = self.config['principal']
            keytab_path = self.config['keytab_path']
            target_spn = self.config['target_spn']
            needs_delegation = self.config['needs_delegation']

            # The auth object defers all gssapi work until the first request goes out.
            _requests_auth = SPNEGOAuth(principal, keytab_path, target_spn, bool(needs_delegation))
            self.requests_auth = _requests_auth
            self.username = principal

        # Whatever the definition contributed replaces the previous set in one assignment,
        # so a request being built elsewhere sees either all of the old headers or all of the new ones.
        self.base_headers = base_headers

# ################################################################################################################################

    def _get_auth(self) -> 'any_':
        """ Returns a username and password pair or None, if no security definition has been attached.
        """
        if self.sec_type in {_Basic_Auth, _NTLM}:
            auth = (self.config['username'], self.config['password'])
        else:
            auth = None

        return auth

    auth = property(fget=_get_auth, doc=_get_auth.__doc__)

# ################################################################################################################################

    def _get_tls_client_cert(self) -> 'any_':
        """ Returns what to pass to requests as its client certificate - a single PEM path holding
        both the certificate and its private key, a (certificate, key) path pair when the key lives
        in its own file, or None when the connection does not present a client certificate.
        """
        client_cert = self.config['tls_client_cert']

        if not client_cert:
            return None

        if client_key := self.config['tls_client_key']:
            out = (client_cert, client_key)
        else:
            out = client_cert

        return out

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
                        scopes = sec_def.get('scopes') or ''
                        scopes = scopes.splitlines()
                        scopes = ' '.join(scopes)

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

        except RequestsTimeout as e:
            self._push_metrics(start_time, 'timeout')
            msg = f'Timeout error: {e}'
            raise BackendInvocationError(cid, msg, needs_msg=True)
        except RequestsConnectionError as e:
            self._push_metrics(start_time, 'connection_error')
            msg = f'Connection error: {e}'
            raise BackendInvocationError(cid, msg, needs_msg=True)
        except Exception:
            self._push_metrics(start_time, 'error')
            raise

# ################################################################################################################################

    def _get_bearer_token_auth(self, sec_def_name:'str', scopes:'str', data_format:'str') -> 'BearerTokenInfoResult':

        # This will get the token from cache or from the remote auth. server ..
        result = self.server.bearer_token_manager.get_bearer_token_info_by_sec_def_name(sec_def_name, scopes, data_format)

        # .. which we can return to our caller.
        return result

# ################################################################################################################################

    def ping(self, cid:'str', return_response:'bool'=False, log_verbose:'bool'=False, *, ping_path:'str'='/') -> 'any_':
        """ Pings a given HTTP/SOAP resource
        """
        logger.info('Pinging:`%s`', self.config_no_sensitive)

        # Session object will write some info to it ..
        verbose = StringIO()

        start = utcnow()
        ping_method = self.config['ping_method'] or 'HEAD'

        def zato_pre_request_hook(hook_data:'stranydict', *args:'any_', **kwargs:'any_') -> 'None':

            entry = '{} (UTC)\n{} {}\n'.format(utcnow().isoformat(),
                ping_method, hook_data['request'].url)
            _ = verbose.write(entry)

        # .. potential wrapper paths must be replaced ..
        ping_path = ping_path or '/'
        address = self.address.replace(r'{_zato_path}', ping_path)

        # .. invoke the other end ..
        response = self.invoke_http(cid, ping_method, address, '', self._create_headers(cid, {}),
            {'zato_pre_request':zato_pre_request_hook})

        # .. store additional info, get and close the stream.
        _ = verbose.write('Code: {}'.format(response.status_code))
        _ = verbose.write('\nResponse time: {}'.format(utcnow() - start))
        value = verbose.getvalue()
        verbose.close()

        if log_verbose:
            func = logger.info if response.status_code == OK else logger.warning
            func(value)

        return response if return_response else value

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

    def _add_soap_action(self, headers:'strstrdict') -> 'None':
        """ Adds the SOAPAction header a SOAP 1.1 request carries.

        Only 1.1 has this header - 1.2 replaced it with a Content-Type parameter, and sending it to
        a 1.2 endpoint anyway is at best ignored and at worst a routing decision made on a header
        that version does not define. The value is quoted because SOAP 1.1 defines it as a quoted
        string, and an unquoted one is what a strict peer rejects.
        """
        if self.config['soap_version'] != SOAPVersion.V11:
            return

        # A connection with no action configured sends no header at all
        soap_action = self.config['soap_action']

        if not soap_action:
            return

        headers[SOAP_Action_Header] = f'"{soap_action}"'

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

class HTTPSOAPWrapper(BaseHTTPSOAPWrapper):
    """ A thin wrapper around the API exposed by the 'requests' package.
    """
    def __init__(
        self,
        server, # type: ParallelServer
        config, # type: stranydict
    ) -> 'None':
        super(HTTPSOAPWrapper, self).__init__(config, server)
        self.server = server

# ################################################################################################################################

    def __str__(self) -> 'str':
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    __repr__ = __str__

# ################################################################################################################################

    def format_address(self, cid:'str', params:'stranydict') -> 'tuple[str, stranydict]':
        """ Formats a URL path to an external resource. Note that exceptions raised
        do not contain anything except for CID. This is in order to keep any potentially
        sensitive data from leaking to clients.
        """
        if not params:
            msg = 'No parameters given for URL path template `{}`, missing parameters: {}'.format(
                self.config['address_url_path'],
                self.path_params
            )
            raise BadRequest(cid, msg, needs_msg=True)

        # Path parameters are taken out of a copy of what the caller gave us and whatever is left
        # of that copy becomes the query string, so the caller's own dict is never written into.
        qs_params = dict(params)

        path_params = {}
        try:
            for name in self.path_params:
                value = qs_params.pop(name)

                # A path parameter fills in one segment of the address and nothing beyond it, so
                # every character that means something to a URL is encoded, the percent sign
                # included. A value arrives as it is meant to be read, so a slash in it is a slash
                # in that one segment and a value spelled as ../ names no directory above it.
                path_params[name] = quote(str(value), safe='')

            address = self.address.format(**path_params)

            out = address, qs_params
            return out
        except(KeyError, ValueError):
            msg = 'Could not build URL path template `{}`, missing parameters: {}'.format(
                self.config['address_url_path'],
                self.path_params
            )
            raise BadRequest(cid, msg, needs_msg=True)

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

    def _soap_data(self, data:'strbytes', headers:'stranydict') -> 'tuple[strbytes, stranydict]':
        """ Wraps the data in a SOAP-specific messages and adds the headers required.
        """
        soap_version = self.config['soap_version']

        # The idea here is that even though there usually won't be the Content-Type
        # header provided by the user, we shouldn't overwrite it if one has been
        # actually passed in.
        if not headers.get('Content-Type'):
            headers['Content-Type'] = SOAP_Content_Type[soap_version]

        # The marker is looked for in the same kind of string the data is, there being no way to
        # search bytes for text or the other way around.
        if isinstance(data, bytes):
            has_envelope = b':Envelope' in data
        else:
            has_envelope = ':Envelope' in data

        # Data that arrives with an envelope of its own is left as it is - wrapping it again would
        # produce a body whose only child is another envelope.
        if has_envelope:
            out = data
        else:
            out = SOAP_Envelope_Template[soap_version].format(header='', data=data)

        return out, headers

# ################################################################################################################################

    def _new_soap_client(self) -> 'SOAPClient':
        """ Builds a SOAP client out of this connection's configuration - the transport details,
        the mutual-TLS material, the WS-Security definition and the body-credential mappings.
        """
        config:'stranydict' = {
            'address': self.address,
            'soap_version': self.config['soap_version'] or SOAPVersion.Default,
            'soap_action': self.config['soap_action'] or '',
            'timeout': self.config['timeout'],
            'validate_tls': self.config['validate_tls'],
            'content_type': self.config['content_type'],
            'tls_client_cert': self.config['tls_client_cert'],
            'tls_client_key': self.config['tls_client_key'],

            # An mTLS definition's pinned CA bundle is carried by the definition, not by the
            # connection, so it is only there when such a definition is attached.
            'ca_certs_path': self.config.get('ca_certs_path'),
            'use_ws_addressing': self.config['use_ws_addressing'] or False,
            'use_mtom': self.config['use_mtom'] or False,
            'wsa_action': self.config['wsa_action'],
            'wsa_to': self.config['wsa_to'],
            'wsa_reply_to': self.config['wsa_reply_to'],
        }

        # The retry settings live in the connection's opaque attributes and the client runs the
        # loop that reads them, so each one that the connection carries is handed over by name.
        for name in _retry.FieldList:
            config[name] = self.config[name]

        # Declarative WS-Addressing values imply the headers are wanted even if the flag is off
        if config['wsa_action'] or config['wsa_to'] or config['wsa_reply_to']:
            config['use_ws_addressing'] = True

        # Body credentials pair the mapping rows with the username and password
        # of the security definition attached to the connection.
        if mappings := self.config['body_credentials']:
            if isinstance(mappings, str):
                mappings = loads(mappings)
            if mappings:
                config['body_credentials'] = {
                    'username': self.config['username'],
                    'password': self.config['password'],
                    'mappings': mappings,
                }

        # A WS-Security definition travels whole, with the connection-level password kept
        # authoritative so a password change reaches the client without a full reload.
        if security := self.config.get('security'):
            security = dict(security)
            if password := self.config['password']:
                security['password'] = password
            config['security'] = security

        out = SOAPClient(config)

        # The client records what it sends and receives - it is the layer where
        # the raw envelope bytes exist in both directions.
        if self.needs_audit:
            out.audit_callback = self._insert_audit_event

        return out

# ################################################################################################################################

    def _get_soap_client(self) -> 'SOAPClient':
        """ Returns the underlying SOAP client, building it on first access.
        """
        if self._soap_client is None:
            self._soap_client = self._new_soap_client()
        return self._soap_client

    soap_client = property(fget=_get_soap_client, doc=_get_soap_client.__doc__)

# ################################################################################################################################

    def invoke(self, cid:'str', operation:'str'='', message:'any_'=None) -> 'any_':
        """ Invokes a SOAP operation over this connection - the message is a dot-accessed
        SOAPMessage that becomes the operation element in soap:Body, and the parsed response
        body comes back the same way, with faults raised as SOAPFault. An operation or message
        the caller does not pass comes from the connection's declarative invocation profile.
        """
        self._enforce_is_active()

        # Fill in the blanks from the connection's declarative invocation profile - explicit
        # arguments always win and JSONata values are evaluated at call time against
        # the message the caller passed in.
        context = build_soap_jsonata_context(message)
        operation, message = merge_declarative_soap_request(self.config, operation, message, context)
        soap_headers = evaluate_soap_headers(self.config, context)

        logger.info('SOAP out -> cid=%s; %s %s; name:%s', cid, operation, self.address, self.config['name'])

        try:
            response = self.soap_client.invoke(operation, message, cid=cid, soap_headers=soap_headers)
        except SOAPFault as fault:

            # The callback hears about the fault first, then the caller sees it re-raised unchanged
            maybe_run_fault_callback(self.server, self.config, cid, fault)
            raise

        # Deliver the response-mapped result to the configured callback in the background,
        # a no-op for connections without callback config
        maybe_run_soap_callback(self.server, self.config, cid, response)

        return response

# ################################################################################################################################

    def invoke_ebxml(self, cid:'str', info:'any_', parts:'any_', sign:'bool'=False, encrypt:'bool'=False) -> 'any_':
        """ Sends an ebXML Message Service message over this connection - payloads travel
        as MIME parts, each optionally signed and encrypted for the recipient. Returns the
        reply's EbXMLInfo, whose attachments are the reply's own payload parts.
        """
        self._enforce_is_active()

        logger.info('ebXML out -> cid=%s; %s; name:%s', cid, self.address, self.config['name'])

        return self.soap_client.invoke_ebxml(info, parts, sign=sign, encrypt=encrypt, cid=cid)

# ################################################################################################################################

    def http_request(
        self,
        method:'str',
        cid:'str',
        data:'any_'='',
        params:'dictnone'=None,
        *args:'any_',
        **kwargs:'any_'
    ) -> 'Response':

        # First, make sure that the connection is active
        self._enforce_is_active()

        # A caller that records events of its own, such as the engine delivering to a channel's
        # destinations, turns this connection's own recording off for the duration of one call ..
        needs_audit = kwargs.pop('needs_audit', True)

        # .. and a connection that does not record anything anyway stays that way.
        if not self.needs_audit:
            needs_audit = False

        # Local variables
        _is_soap = self.config['transport'] == 'soap'

        # Pop it here for later use because we cannot pass it to the requests module
        model = kwargs.pop('model', None)

        # Fill in the blanks from the connection's declarative invocation profile (REST only) -
        # explicit arguments always win and JSONata values are evaluated at call time
        # against the data the caller passed in.
        if not _is_soap:
            declarative_headers = kwargs.pop('headers', None)
            context = build_jsonata_context(data)
            method, data, params, declarative_headers = merge_declarative_request(
                self.config, method, data, params, declarative_headers, context)
            if declarative_headers:
                kwargs['headers'] = declarative_headers

        # We do not serialize ourselves data based on this content type,
        # leaving it up to the underlying HTTP library to do it ..
        needs_serialize_based_on_content_type = self.config['content_type'] != ContentType.FormURLEncoded

        # .. otherwise, our input data may need to be serialized ..
        if needs_serialize_based_on_content_type:

            # .. we never serialize what already represents what ought to be sent as-is ..
            needs_request_serialize = _needs_serialization(data)

            # .. if we are here, we know check further if serialization is required ..
            if needs_request_serialize:

                # .. we are explicitly told to send JSON ..
                if self.config['data_format'] == DATA_FORMAT.JSON:

                    # .. models need to be converted to dicts before they can be serialized ..
                    if isinstance(data, Model):
                        data = data.to_dict()

                    # .. do serialize to JSON now ..
                    data = dumps(data)

                # .. we are explicitly told to submit form-like data ..
                elif self.config['data_format'] == DATA_FORMAT.FORM_DATA:
                    data = urlencode(data)

        # .. check if we have custom headers on input ..
        headers = kwargs.pop('headers', None) or {}

        # .. build a default set of headers now ..
        headers = self._create_headers(cid, headers)

        # .. SOAP requests need to be specifically formatted now ..
        if _is_soap:
            data, headers = self._soap_data(data, headers)

        # .. check if we have custom query parameters ..
        params = params or {}

        # .. if the address is a template, format it with input parameters ..
        if self.path_params:
            address, qs_params = self.format_address(cid, params)
        else:
            address, qs_params = self.address, dict(params)

        # .. make sure that Unicode objects are turned into bytes ..
        if needs_serialize_based_on_content_type and (not _is_soap):
            if isinstance(data, str):
                data = data.encode('utf-8')

        # .. record the outgoing request in the audit log ..
        if needs_audit:
            self._insert_audit_event(cid, AuditEvent.Request_Sent, f'{method} {address}', AuditOutcome.OK, data)

        # .. do invoke the connection ..
        try:
            response = self.invoke_http(cid, method, address, data, headers, {}, params=qs_params, *args, **kwargs)
        except Exception as e:

            # .. record the error in the audit log before re-raising, sharing the request's CID ..
            if needs_audit:
                self._insert_audit_event(cid, AuditEvent.Response_Received, f'{method} {address}', AuditOutcome.Error, str(e))
            raise

        response = cast_('Response', response)

        # .. record the received response in the audit log, sharing the request's CID ..
        if needs_audit:
            if response.ok:
                response_outcome = AuditOutcome.OK
            else:
                response_outcome = AuditOutcome.Error
            self._insert_audit_event(cid, AuditEvent.Response_Received, f'{method} {address}', response_outcome, response.text)

        # .. by default, we have no parsed response at all, ..
        # .. which means that we can assume it will be the same as the raw, text response ..
        response.data = response.text
        response.zato_method = method
        response.zato_address = address
        response.zato_qs_params = qs_params

        # .. check if we are explicitly told that we handle JSON ..
        _has_data_format_json = self.config['data_format'] == DATA_FORMAT.JSON

        # .. check if we perhaps received JSON in the response ..
        _has_json_content_type = 'application/json' in (response.headers.get('Content-Type') or '')

        # .. are we actually handling JSON in this response .. ?
        _is_json:'bool' = _has_data_format_json or _has_json_content_type

        # .. if yes, try to parse the response accordingly ..
        if _is_json:
            try:
                response.data = loads(response.text or '""')
            except ValueError as e:
                msg = 'Could not parse JSON response `{}`; e:`{}`'.format(response.text, e.args[0])
                raise BadRequest(cid, msg, needs_msg=True)

        # .. if we have a model class on input, deserialize the received response into one ..
        if model:
            response.data = self.server.marshal_api.from_dict(None, response.data, model)

        # .. deliver the response-mapped result to the configured callback in the background,
        # .. a no-op for connections without callback config ..
        if not _is_soap:
            maybe_run_callback(self.server, self.config, cid, response.data)

        # .. now, return the response to the caller.
        return response

# ################################################################################################################################

    def get(self, cid:'str', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('GET', cid, '', params, *args, **kwargs)

    def delete(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('DELETE', cid, data, params, *args, **kwargs)

    def options(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('OPTIONS', cid, data, params, *args, **kwargs)

    def post(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('POST', cid, data, params, *args, **kwargs)

    send = post

    def put(self, cid:'str', data:'str'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('PUT', cid, data, params, *args, **kwargs)

    def patch(self, cid:'str', data:'str'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('PATCH', cid, data, params, *args, **kwargs)

    def rest_invoke(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        """ Invokes the connection with no explicit arguments needed - the HTTP method,
        query string, path params, headers and body all come from the connection's
        declarative invocation profile, with anything given explicitly winning.
        """
        return self.http_request('', cid, data, params, *args, **kwargs)

    def upload(
        self,
        cid,  # type: str
        item, # type: str
        field_name = 'data',      # type: str
        mime_type  = 'text/plain' # type: str
    ) -> 'Response':

        # Make sure such a file exists
        if not os.path.exists(item):
            raise Exception(f'File to upload not found -> `{item}`')

        # Ensure that the path actually is a file
        if not os.path.isfile(item):
            raise Exception(f'Path is not a file -> `{item}`')

        # Extract the file
        file_name = os.path.basename(item)

        # At this point, we have collected everything needed to upload the file and we can proceed
        with open_rb(item) as file_to_upload:

            # Build a list of fields to be encoded as a multi-part upload
            fields = {
                field_name: (file_name, file_to_upload, mime_type)
            }

            # .. this is  the object that builds a multi-part message out of the file ..
            encoder = MultipartEncoder(fields=fields)

            # .. build user headers based on what the encoder produced ..
            headers = {
                'Content-Type': encoder.content_type
            }

            # .. now, we can invoke the remote endpoint with our file on input.
            return self.post(cid, data=encoder, headers=headers)

# ################################################################################################################################

    def rest_call(
        self,
        *,
        cid,          # type: str
        data='',      # type: any_
        model=None,   # type: type_[Model] | None
        callback,     # type: callnone
        params=None,  # type: strdictnone
        headers=None, # type: strdictnone
        method='',    # type: str
        sec_def_name=None,    # type: any_
        auth_scopes=None,     # type: any_
        log_response=False,   # type: bool
        needs_exception=True, # type: bool
        max_retries=None,     # type: int | None
        retry_sleep_time=None,   # type: int | None
        retry_backoff_threshold=None, # type: int | None
        retry_backoff_multiplier=None, # type: int | None
    ) -> 'any_':

        # Invoke the system ..
        try:
            response:'Response' = self.http_request(
                method,
                cid,
                data=data,
                sec_def_name=sec_def_name,
                auth_scopes=auth_scopes,
                params=params,
                headers=headers,
                max_retries=max_retries,
                retry_sleep_time=retry_sleep_time,
                retry_backoff_threshold=retry_backoff_threshold,
                retry_backoff_multiplier=retry_backoff_multiplier,
            )
        except Exception as e:
            if needs_exception:
                raise
            else:
                logger.warning('Caught an exception -> %s -> %s', e, format_exc())
        else:

            # .. a response body is only logged by a caller that asked for it ..
            if log_response:
                logger.info('REST call response received -> %s', response.text)

            if not response.ok:
                if response.zato_qs_params:
                    qs_path = '?' + urlencode(response.zato_qs_params)
                else:
                    qs_path = ''
                msg =  f'Error calling outgoing connection: {self.config["name"]} -> {response.zato_method}'
                msg += f' {response.zato_address}{qs_path} -> {response.data}'

                logger.info(msg)
                raise BackendInvocationError(cid, msg, needs_msg=True)

            # .. extract the underlying data ..
            response_data = response.data

            # .. if we have a model, do make use of it here ..
            if model:

                # .. if this model is actually a list ..
                if is_list(model, True):

                    # .. extract the underlying model ..
                    model_class:'type_[Model]' = extract_model_class(model)

                    # .. build a list that we will map the response to ..
                    model_list:'list_[Model]' = []

                    # .. go through everything we had in the response ..
                    for item in response_data:

                        # .. build an actual model instance ..
                        _item = model_class.from_dict(item)

                        # .. and append it to the data that we are producing ..
                        model_list.append(_item)

                    data = model_list
                else:
                    data = model.from_dict(response_data)

            # .. if there is no model, use the response as-is ..
            else:
                data = response_data

            # .. run our callback, if there is any ..
            if callback:
                data = callback(data, cid=cid, model=model, callback=callback)

            # .. and return the data to our caller ..
            return data, response

RESTWrapper = HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################
