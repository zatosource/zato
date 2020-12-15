# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from gzip import GzipFile
from hashlib import sha256
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_FOUND, UNAUTHORIZED
from io import StringIO
from traceback import format_exc

# Django
from django.http import QueryDict

# Paste
from paste.util.converters import asbool

# regex
from regex import compile as regex_compile

# Python 2/3 compatibility
from six import PY3
from past.builtins import basestring, unicode

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, JSON_RPC, HL7, HTTP_SOAP, RATE_LIMIT, SEC_DEF_TYPE, SIMPLE_IO, TRACE1, \
     URL_PARAMS_PRIORITY, URL_TYPE, ZATO_NONE, ZATO_OK
from zato.common.exception import HTTP_RESPONSES
from zato.common.hl7 import HL7Exception
from zato.common.json_internal import dumps, loads
from zato.common.json_schema import DictError as JSONSchemaDictError, ValidationException as JSONSchemaValidationException
from zato.common.rate_limiting.common import AddressNotAllowed, BaseException as RateLimitingException, RateLimitReached
from zato.common.util.api import payload_from_request
from zato.common.xml_ import zato_namespace
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, Forbidden, MethodNotAllowed, NotFound, \
     TooManyRequests, Unauthorized
from zato.server.service.internal import AdminService

stack_format = None

# ################################################################################################################################

if 0:
    from zato.server.service import Service
    from zato.server.service.reqresp import Response
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.http_soap.url_data import URLData

    # For pyflakes
    ParallelServer = ParallelServer
    Response = Response
    Service = Service
    URLData = URLData

# ################################################################################################################################

logger = logging.getLogger(__name__)
_has_debug = logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################

accept_any_http = HTTP_SOAP.ACCEPT.ANY
accept_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

# ################################################################################################################################

TOO_MANY_REQUESTS = 429

_status_bad_request = '{} {}'.format(BAD_REQUEST, HTTP_RESPONSES[BAD_REQUEST])
_status_internal_server_error = '{} {}'.format(INTERNAL_SERVER_ERROR, HTTP_RESPONSES[INTERNAL_SERVER_ERROR])
_status_not_found = '{} {}'.format(NOT_FOUND, HTTP_RESPONSES[NOT_FOUND])
_status_method_not_allowed = '{} {}'.format(METHOD_NOT_ALLOWED, HTTP_RESPONSES[METHOD_NOT_ALLOWED])
_status_unauthorized = '{} {}'.format(UNAUTHORIZED, HTTP_RESPONSES[UNAUTHORIZED])
_status_forbidden = '{} {}'.format(FORBIDDEN, HTTP_RESPONSES[FORBIDDEN])
_status_too_many_requests = '{} {}'.format(TOO_MANY_REQUESTS, HTTP_RESPONSES[TOO_MANY_REQUESTS])

# ################################################################################################################################

_data_format_hl7 = HL7.Const.Version.v2.id

# ################################################################################################################################

_basic_auth = SEC_DEF_TYPE.BASIC_AUTH
_jwt = SEC_DEF_TYPE.JWT
_sso_ext_auth = _basic_auth, _jwt

# ################################################################################################################################

status_response = {}
for code, response in HTTP_RESPONSES.items():
    status_response[code] = '{} {}'.format(code, response)

# ################################################################################################################################

soap_doc = """<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="https://zato.io/ns/20130518"><soap:Body>{body}</soap:Body></soap:Envelope>""" # noqa

# ################################################################################################################################

zato_message_soap = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="https://zato.io/ns/20130518">
  <soap:Body>{data}</soap:Body>
</soap:Envelope>"""

# ################################################################################################################################

zato_message_plain = b'{data}'
zato_message_declaration = b"<?xml version='1.0' encoding='UTF-8'?>" + zato_message_plain
zato_message_declaration_uni = zato_message_declaration.decode('utf8')

# ################################################################################################################################

# Returned if there has been any exception caught.
soap_error = """<?xml version='1.0' encoding='UTF-8'?>
<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/1999/XMLSchema">
   <SOAP-ENV:Body>
     <SOAP-ENV:Fault>
     <faultcode>SOAP-ENV:{faultcode}</faultcode>
     <faultstring><![CDATA[cid [{cid}], faultstring [{faultstring}]]]></faultstring>
      </SOAP-ENV:Fault>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

# ################################################################################################################################

response_404     = 'URL not found (CID:{})'
response_404_log = 'URL not found `%s` (Method:%s; Accept:%s; CID:%s)'

# ################################################################################################################################

def client_json_error(cid, details):
    message = {'result':'Error', 'cid':cid}
    if details:
        message['details'] = details
    return dumps(message)

# ################################################################################################################################

def client_soap_error(cid, faultstring):
    return soap_error.format(**{'faultcode':'Client', 'cid':cid, 'faultstring':faultstring})

# ################################################################################################################################

def server_soap_error(cid, faultstring):
    return soap_error.format(**{'faultcode':'Server', 'cid':cid, 'faultstring':faultstring})

# ################################################################################################################################

client_error_wrapper = {
    DATA_FORMAT.JSON: client_json_error,
    DATA_FORMAT.SOAP: client_soap_error,
    HL7.Const.Version.v2.id: client_json_error,
}

# ################################################################################################################################

def get_client_error_wrapper(transport, data_format):
    try:
        return client_error_wrapper[transport]
    except KeyError:
        # Any KeyError must be caught by the caller
        return client_error_wrapper[data_format]

# ################################################################################################################################

class _CachedResponse(object):
    """ A wrapper for responses served from caches.
    """
    __slots__ = ('payload', 'content_type', 'headers', 'status_code')

    def __init__(self, payload, content_type, headers, status_code):
        self.payload = payload
        self.content_type = content_type
        self.headers = headers
        self.status_code = status_code

# ################################################################################################################################

class _HashCtx(object):
    """ Encapsulates information needed to compute a hash value of an incoming request.
    """
    def __init__(self, raw_request, channel_item, channel_params, wsgi_environ):
        self.raw_request = raw_request
        self.channel_item = channel_item
        self.channel_params = channel_params
        self.wsgi_environ = wsgi_environ

# ################################################################################################################################

class RequestDispatcher(object):
    """ Dispatches all the incoming HTTP/SOAP requests to appropriate handlers.
    """
    def __init__(self, server=None, url_data=None, security=None, request_handler=None, simple_io_config=None,
            return_tracebacks=None, default_error_message=None, http_methods_allowed=None):
        # type: (ParallelServer, URLData, object, object, dict, bool, unicode, list)

        self.server = server
        self.url_data = url_data
        self.security = security

        self.request_handler = request_handler
        self.simple_io_config = simple_io_config
        self.return_tracebacks = return_tracebacks

        self.default_error_message = default_error_message
        self.http_methods_allowed = http_methods_allowed

        # To reduce the number of attribute lookups
        self._sso_api_user = self.server.sso_api.user if self.server.sso_api else None

# ################################################################################################################################

    def wrap_error_message(self, cid, url_type, msg):
        """ Wraps an error message in a transport-specific envelope.
        """
        if url_type == URL_TYPE.SOAP:
            return server_soap_error(cid, msg)

        # Let's return the message as-is if we didn't have any specific envelope
        # to use.
        return msg

# ################################################################################################################################

    def _handle_quotes_soap_action(self, soap_action):
        """ Make sure quotes around SOAP actions are ignored so these two
        are equivalent:
        - SOAPAction: "my.soap.action"
        - SOAPAction: my.soap.action
        """
        if soap_action[0] == '"' and soap_action[-1] == '"':
            soap_action = soap_action[1:-1]

        return soap_action if isinstance(soap_action, unicode) else soap_action.decode('utf-8')

# ################################################################################################################################

    def dispatch(self, cid, req_timestamp, wsgi_environ, worker_store, _status_response=status_response,
        no_url_match=(None, False), _response_404=response_404, _response_404_log=response_404_log, _has_debug=_has_debug,
        _http_soap_action='HTTP_SOAPACTION', _stringio=StringIO, _gzipfile=GzipFile, _accept_any_http=accept_any_http,
        _accept_any_internal=accept_any_internal, _rate_limit_type_http=RATE_LIMIT.OBJECT_TYPE.HTTP_SOAP,
        _rate_limit_type_sso_user=RATE_LIMIT.OBJECT_TYPE.SSO_USER, _stack_format=stack_format, _exc_sep='*' * 80,
        _jwt=_jwt, _sso_ext_auth=_sso_ext_auth, _data_format_hl7=_data_format_hl7):

        # Needed as one of the first steps
        http_method = wsgi_environ['REQUEST_METHOD']
        http_method = http_method if isinstance(http_method, unicode) else http_method.decode('utf8')

        http_accept = wsgi_environ.get('HTTP_ACCEPT') or _accept_any_http
        http_accept = http_accept.replace('*', _accept_any_internal).replace('/', 'HTTP_SEP')
        http_accept = http_accept if isinstance(http_accept, unicode) else http_accept.decode('utf8')

        # Needed in later steps
        path_info = wsgi_environ['PATH_INFO'] if PY3 else wsgi_environ['PATH_INFO'].decode('utf8')

        # Immediately reject the request if it is not a support HTTP method, no matter what channel
        # it would have otherwise matched.
        if http_method not in self.http_methods_allowed:
            wsgi_environ['zato.http.response.status'] = _status_method_not_allowed
            return client_json_error(cid, 'Unsupported HTTP method')

        if _http_soap_action in wsgi_environ:
            soap_action = self._handle_quotes_soap_action(wsgi_environ[_http_soap_action])
        else:
            soap_action = ''

        # Can we recognize this combination of URL path and SOAP action at all?
        # This gives us the URL info and security data - but note that here
        # we still haven't validated credentials, only matched the URL.
        # Credentials are checked in a call to self.url_data.check_security
        url_match, channel_item = self.url_data.match(path_info, soap_action, http_method, http_accept, bool(soap_action))

        if _has_debug and channel_item:
            logger.debug('url_match:`%r`, channel_item:`%r`', url_match, sorted(channel_item.items()))

        # This is needed in parallel.py's on_wsgi_request
        wsgi_environ['zato.channel_item'] = channel_item

        # Read the raw data
        payload = wsgi_environ['wsgi.input'].read()

        # Store for later use prior to any kind of parsing
        wsgi_environ['zato.http.raw_request'] = payload

        # OK, we can possibly handle it
        if url_match not in no_url_match:

            try:

                # Raise 404 if the channel is inactive
                if not channel_item['is_active']:
                    logger.warn('url_data:`%s` is not active, raising NotFound', sorted(url_match.items()))
                    raise NotFound(cid, 'Channel inactive')

                # We need to read security info here so we know if POST needs to be
                # parsed. If so, we do it here and reuse it in other places
                # so it doesn't have to be parsed two or more times.
                post_data = {}

                match_target = channel_item['match_target']
                sec = self.url_data.url_sec[match_target]

                if sec.sec_def != ZATO_NONE or sec.sec_use_rbac is True:

                    if sec.sec_def != ZATO_NONE:

                        if sec.sec_def.sec_type == SEC_DEF_TYPE.OAUTH:
                            post_data.update(QueryDict(payload, encoding='utf-8'))

                        # Eagerly parse the request but only if we expect XPath-based credentials. The request will be re-used
                        # in later steps, it won't be parsed twice or more.
                        elif sec.sec_def.sec_type == SEC_DEF_TYPE.XPATH_SEC:
                            wsgi_environ['zato.request.payload'] = payload_from_request(
                                cid, payload, channel_item.data_format, channel_item.transport)

                    # Will raise an exception on any security violation
                    auth_result = self.url_data.check_security(
                        sec, cid, channel_item, path_info, payload, wsgi_environ, post_data, worker_store)

                # Check rate limiting now - this could not have been done earlier because we wanted
                # for security checks to be made first. Otherwise, someone would be able to invoke
                # our endpoint without credentials as many times as it is needed to exhaust the rate limit
                # denying in this manner access to genuine users.
                if channel_item.get('is_rate_limit_active'):
                    self.server.rate_limiting.check_limit(
                        cid, _rate_limit_type_http, channel_item['name'], wsgi_environ['zato.http.remote_addr'])

                # Security definition-based checks went fine but it is still possible
                # that this sec_def is linked to an SSO user whose rate limits we need to check.

                # Check SSO-related limits only if SSO is enabled
                if self._sso_api_user:

                    # Not all sec_def types may have associated SSO users
                    if sec.sec_def != ZATO_NONE:

                        if sec.sec_def.sec_type in _sso_ext_auth:

                            # JWT comes with external sessions whereas Basic Auth does not
                            if sec.sec_def.sec_type == _jwt:
                                ext_session_id = auth_result.raw_token
                            else:
                                ext_session_id = None

                            # Try to log in the user to SSO by that account's external credentials.
                            self.server.sso_tool.on_external_auth(
                                sec.sec_def.sec_type, sec.sec_def.id, sec.sec_def.username, cid,
                                wsgi_environ, ext_session_id)
                        else:
                            raise Exception('Unexpected sec_type `{}`'.format(sec.sec_def.sec_type))

                # This is handy if someone invoked URLData's OAuth API manually
                wsgi_environ['zato.oauth.post_data'] = post_data

                # OK, no security exception at that point means we can finally invoke the service.
                response = self.request_handler.handle(cid, url_match, channel_item, wsgi_environ,
                    payload, worker_store, self.simple_io_config, post_data, path_info, soap_action)

                wsgi_environ['zato.http.response.headers']['Content-Type'] = response.content_type
                wsgi_environ['zato.http.response.headers'].update(response.headers)
                wsgi_environ['zato.http.response.status'] = _status_response[response.status_code]

                if channel_item['content_encoding'] == 'gzip':

                    s = _stringio()
                    with _gzipfile(fileobj=s, mode='w') as f:
                        f.write(response.payload)
                    response.payload = s.getvalue()
                    s.close()

                    wsgi_environ['zato.http.response.headers']['Content-Encoding'] = 'gzip'

                # Finally, return payload to the client
                return response.payload

            except Exception as e:
                _format_exc = format_exc()
                status = _status_internal_server_error

                if isinstance(e, ClientHTTPError):

                    response = e.msg
                    status_code = e.status

                    # TODO: Refactor this series of if/else's into a lookup dict.

                    if isinstance(e, Unauthorized):
                        status = _status_unauthorized
                        wsgi_environ['zato.http.response.headers']['WWW-Authenticate'] = e.challenge

                    elif isinstance(e, BadRequest):
                        status = _status_bad_request

                    elif isinstance(e, NotFound):
                        status = _status_not_found

                    elif isinstance(e, MethodNotAllowed):
                        status = _status_method_not_allowed

                    elif isinstance(e, Forbidden):
                        status = _status_forbidden

                    elif isinstance(e, TooManyRequests):
                        status = _status_too_many_requests

                else:

                    # JSON Schema validation
                    if isinstance(e, JSONSchemaValidationException):
                        status_code = _status_bad_request
                        needs_prefix = False if e.needs_err_details else True
                        response = JSONSchemaDictError(
                            cid, e.needs_err_details, e.error_msg, needs_prefix=needs_prefix).serialize()

                    # Rate limiting and whitelisting
                    elif isinstance(e, RateLimitingException):
                        response, status_code, status = self._on_rate_limiting_exception(cid, e, channel_item)

                    # HL7
                    elif channel_item['data_format'] == _data_format_hl7:
                        response, status_code, status = self._on_hl7_exception(cid, e, channel_item)

                    else:
                        status_code = INTERNAL_SERVER_ERROR
                        response = _format_exc if self.return_tracebacks else self.default_error_message

                _exc = _stack_format(e, style='color', show_vals='like_source', truncate_vals=5000,
                    add_summary=True, source_lines=20) if _stack_format else _format_exc

                # TODO: This should be configurable. Some people may want such
                # things to be on DEBUG whereas for others ERROR will make most sense
                # in given circumstances.
                logger.error(
                    'Caught an exception, cid:`%s`, status_code:`%s`, `%s`', cid, status_code, _exc)

                try:
                    error_wrapper = get_client_error_wrapper(channel_item['transport'], channel_item['data_format'])
                except KeyError:
                    # It's OK. Apparently it's neither 'soap' nor json'
                    if logger.isEnabledFor(TRACE1):
                        msg = 'No client error wrapper for transport:`{}`, data_format:`{}`'.format(
                            channel_item.get('transport'), channel_item.get('data_format'))
                        logger.log(TRACE1, msg)
                else:
                    response = error_wrapper(cid, response)

                wsgi_environ['zato.http.response.status'] = status

                return response

        # This is 404, no such URL path and SOAP action is not known either.
        else:

            # Indicate HTTP 404
            wsgi_environ['zato.http.response.status'] = _status_not_found

            # This is returned to the caller - note that it does not echo back the URL requested ..
            response = _response_404.format(cid)

            # .. this goes to logs and it includes the URL sent by the client.
            logger.error(_response_404_log, path_info, wsgi_environ.get('REQUEST_METHOD'), wsgi_environ.get('HTTP_ACCEPT'), cid)

            # This is the payload for the caller
            return response

# ################################################################################################################################

    def _on_rate_limiting_exception(self, cid, e, channel_item, _json=DATA_FORMAT.JSON, _json_rpc=JSON_RPC.PREFIX.CHANNEL):
        # type: (unicode, RateLimitingException, dict, unicode, unicode) -> (unicode, int, unicode)

        if isinstance(e, RateLimitReached):
            status_code = TOO_MANY_REQUESTS
            status = _status_too_many_requests

        elif isinstance(e, AddressNotAllowed):
            status_code = FORBIDDEN
            status = _status_forbidden

        return 'Error {}'.format(status), status_code, status

# ################################################################################################################################

    def _on_hl7_exception(self, cid, e, channel_item, _json=DATA_FORMAT.JSON):
        # type: (unicode, HL7Exception, dict) -> (unicode, int, unicode)

        if channel_item['should_return_errors'] and isinstance(e, HL7Exception):
            details = '`{}`; data:`{}`'.format(e.args[0], e.data)
        else:
            details = ''

        return details, BAD_REQUEST, _status_bad_request

# ################################################################################################################################

class RequestHandler(object):
    """ Handles individual HTTP requests to a given service.
    """
    def __init__(self, server=None):
        # type: (ParallelServer)
        self.server = server
        self.use_soap_envelope = asbool(self.server.fs_server_config.misc.use_soap_envelope) # type: bool

# ################################################################################################################################

    def _set_response_data(self, service, **kwargs):
        """ A callback invoked by the services after it is done producing the response.
        """
        data_format = kwargs.get('data_format')
        transport = kwargs.get('transport')

        self.set_payload(service.response, data_format, transport, service)
        self.set_content_type(service.response, data_format, transport, kwargs.get('url_match'), kwargs.get('channel_item'))

        return service.response

# ################################################################################################################################

    def _get_flattened(self, params):
        """ Returns a QueryDict of parameters with single-element lists unwrapped to point to the sole element directly.
        """
        if params:
            params = QueryDict(params, encoding='utf-8')
            out = {}
            for key, value in params.lists():
                if len(value) > 1:
                    out[key] = value
                else:
                    out[key] = value[0]
        else:
            out = {}

        return out

# ################################################################################################################################

    def create_channel_params(self, path_params, channel_item, wsgi_environ, raw_request, post_data=None, _has_debug=_has_debug):
        """ Collects parameters specific to this channel (HTTP) and updates wsgi_environ
        with HTTP-specific data.
        """
        _qs = self._get_flattened(wsgi_environ.get('QUERY_STRING'))

        # Whoever called us has already parsed POST for us so we just use it as is
        if post_data:
            post = post_data
        else:
            # We cannot parse incoming data if we know for sure that an explicit
            # data format was set for channel.
            post = self._get_flattened(raw_request) if not channel_item.data_format else {}

        if channel_item.url_params_pri == URL_PARAMS_PRIORITY.QS_OVER_PATH:
            if _qs:
                path_params.update((key, value) for key, value in _qs.items())
            channel_params = path_params
        else:
            if _qs:
                channel_params = dict((key, value) for key, value in _qs.items())
            else:
                channel_params = {}
            channel_params.update(path_params)

        if _has_debug:
            logger.debug('channel_params `%s`, path_params `%s`, _qs `%s`', channel_params, path_params, _qs)

        wsgi_environ['zato.http.GET'] = _qs
        wsgi_environ['zato.http.POST'] = post

        return channel_params

# ################################################################################################################################

    def get_response_from_cache(self, service, raw_request, channel_item, channel_params, wsgi_environ, _loads=loads,
        _CachedResponse=_CachedResponse, _HashCtx=_HashCtx, _sha256=sha256, split_re=regex_compile('........?').findall):
        """ Returns a cached response for incoming request or None if there is nothing cached for it.
        By default, an incoming request's hash is calculated by sha256 over a concatenation of:
          * WSGI REQUEST_METHOD   # E.g. GET or POST
          * WSGI PATH_INFO        # E.g. /my/api
          * sorted(zato.http.GET) # E.g. ?foo=123&bar=456 (query string aka channel_params)
          * payload bytes         # E.g. '{"customer_id":"123"}' - a string object, before parsing
        Note that query string is sorted which means that ?foo=123&bar=456 is equal to ?bar=456&foo=123,
        that is, the order of parameters in query string does not matter.
        """
        if service.get_request_hash:
            hash_value = service.get_request_hash(_HashCtx(raw_request, channel_item, channel_params, wsgi_environ))
        else:
            query_string = str(sorted(channel_params.items()))
            data = '%s%s%s%s' % (wsgi_environ['REQUEST_METHOD'], wsgi_environ['PATH_INFO'], query_string, raw_request)
            hash_value = _sha256(data.encode('utf8')).hexdigest()
            hash_value = '-'.join(split_re(hash_value))

        # No matter if hash value is default or from service, always prefix it with channel's type and ID
        cache_key = 'http-channel-%s-%s' % (channel_item['id'], hash_value)

        # We have the key so now we can check if there is any matching response already stored in cache
        response = self.server.get_from_cache(channel_item['cache_type'], channel_item['cache_name'], cache_key)

        # If there is any response, we can now load into a format that our callers expect
        if response:
            response = _loads(response)
            response = _CachedResponse(response['payload'], response['content_type'], response['headers'],
                response['status_code'])

        return cache_key, response

# ################################################################################################################################

    def set_response_in_cache(self, channel_item, key, response, _dumps=dumps, _py3=PY3):
        """ Caches responses from this channel's invocation for as long as the cache is configured to keep it.
        """
        self.server.set_in_cache(channel_item['cache_type'], channel_item['cache_name'], key, _dumps({
            'payload': response.payload,
            'content_type': response.content_type,
            'headers': response.headers,
            'status_code': response.status_code.value if _py3 else response.status_code,
        }))

# ################################################################################################################################

    def handle(self, cid, url_match, channel_item, wsgi_environ, raw_request, worker_store, simple_io_config, post_data,
            path_info, soap_action, channel_type=CHANNEL.HTTP_SOAP, _response_404=response_404):
        """ Create a new instance of a service and invoke it.
        """
        service, is_active = self.server.service_store.new_instance(channel_item.service_impl_name)
        if not is_active:
            logger.warn('Could not invoke an inactive service:`%s`, cid:`%s`', service.get_name(), cid)
            raise NotFound(cid, _response_404.format(
                path_info, wsgi_environ.get('REQUEST_METHOD'), wsgi_environ.get('HTTP_ACCEPT'), cid))

        if channel_item.merge_url_params_req:
            channel_params = self.create_channel_params(url_match, channel_item, wsgi_environ, raw_request, post_data)
        else:
            channel_params = None

        # If caching is configured for this channel, we need to first check if there is no response already
        if channel_item['cache_type']:
            cache_key, response = self.get_response_from_cache(service, raw_request, channel_item, channel_params, wsgi_environ)
            if response:
                return response

        # Add any path params matched to WSGI environment so it can be easily accessible later on
        wsgi_environ['zato.http.path_params'] = url_match

        # No cache for this channel or no cached response, invoke the service then.
        response = service.update_handle(self._set_response_data, service, raw_request,
            channel_type, channel_item.data_format, channel_item.transport, self.server, worker_store.broker_client,
            worker_store, cid, simple_io_config, wsgi_environ=wsgi_environ,
            url_match=url_match, channel_item=channel_item, channel_params=channel_params,
            merge_channel_params=channel_item.merge_url_params_req,
            params_priority=channel_item.params_pri)

        # Cache the response if needed (cache_key was already created on return from get_response_from_cache)
        if channel_item['cache_type']:
            self.set_response_in_cache(channel_item, cache_key, response)

        # Having used the cache or not, we can return the response now
        return response

# ################################################################################################################################

    def _get_xml_admin_payload(self, service_instance, zato_message_template, payload):

        if payload:
            data=payload.getvalue()
        else:
            data="""<{response_elem} xmlns="{namespace}">
                <zato_env>
                  <cid>{cid}</cid>
                  <result>{result}</result>
                </zato_env>
              </{response_elem}>
            """.format(response_elem=getattr(service_instance.SimpleIO, 'response_elem', 'response'),
                       namespace=getattr(service_instance.SimpleIO, 'namespace', zato_namespace),
                         cid=service_instance.cid, result=ZATO_OK)

        return zato_message_template.format(data=data.encode('utf-8') if isinstance(data, unicode) else data)

# ################################################################################################################################

    def set_payload(self, response, data_format, transport, service_instance):
        """ Sets the actual payload to represent the service's response out of what the service produced.
        This includes converting dictionaries into JSON, adding Zato metadata and wrapping the mesasge in SOAP if need be.
        """
        # type: (Response, str, str, Service)

        if isinstance(service_instance, AdminService):
            if data_format == SIMPLE_IO.FORMAT.JSON:
                zato_env = {'zato_env':{'result':response.result, 'cid':service_instance.cid, 'details':response.result_details}}
                if response.payload:
                    payload = response.payload.getvalue(False)
                    payload.update(zato_env)
                else:
                    payload = zato_env

                response.payload = dumps(payload)

            else:
                if transport == URL_TYPE.SOAP:
                    zato_message_template = zato_message_soap
                else:
                    zato_message_template = zato_message_declaration_uni

                if response.payload:
                    if not isinstance(response.payload, basestring):
                        response.payload = self._get_xml_admin_payload(service_instance, zato_message_template, response.payload)
                else:
                    response.payload = self._get_xml_admin_payload(service_instance, zato_message_template, None)
        else:
            if not isinstance(response.payload, basestring):
                if isinstance(response.payload, dict) and data_format in (DATA_FORMAT.JSON, DATA_FORMAT.DICT):
                    response.payload = dumps(response.payload)
                else:
                    response.payload = response.payload.getvalue() if response.payload else ''

        if transport == URL_TYPE.SOAP:
            if not isinstance(service_instance, AdminService):
                if self.use_soap_envelope:
                    response.payload = soap_doc.format(body=response.payload)

# ################################################################################################################################

    def set_content_type(self, response, data_format, transport, ignored_url_match, channel_item):
        """ Sets a response's content type if one hasn't been supplied by the user.
        """
        # type: (Response, str, str, object, object)

        # A user provided his or her own content type ..
        if response.content_type_changed:
            content_type = response.content_type
        else:
            # .. or they did not so let's find out if we're using SimpleIO ..
            if data_format == SIMPLE_IO.FORMAT.XML:
                if transport == URL_TYPE.SOAP:
                    if channel_item.soap_version == '1.1':
                        content_type = self.server.soap11_content_type
                    else:
                        content_type = self.server.soap12_content_type
                else:
                    content_type = self.server.plain_xml_content_type
            elif data_format == SIMPLE_IO.FORMAT.JSON:
                content_type = self.server.json_content_type

            # .. alright, let's use the default value after all.
            else:
                content_type = response.content_type

        response.content_type = content_type

# ################################################################################################################################
