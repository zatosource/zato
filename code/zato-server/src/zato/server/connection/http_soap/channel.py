# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from gzip import GzipFile
from hashlib import sha256
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_FOUND, UNAUTHORIZED
from io import StringIO
from traceback import format_exc

# regex
from regex import compile as regex_compile

# Zato
from zato.common.api import CHANNEL, CONTENT_TYPE, DATA_FORMAT, HTTP_SOAP, MISC, SEC_DEF_TYPE, SIMPLE_IO, \
    TRACE1, URL_PARAMS_PRIORITY, ZATO_NONE
from zato.common.const import ServiceConst
from zato.common.exception import HTTP_RESPONSES, ServiceMissingException
from zato.common.json_internal import dumps, loads
from zato.common.marshal_.api import Model, ModelValidationError
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, utcnow
from zato.common.util.auth import enrich_with_sec_data, extract_basic_auth
from zato.common.util.exception import pretty_format_exception
from zato.common.util.http_ import get_form_data as util_get_form_data, QueryDict
from zato.cy.reqresp.payload import SimpleIOPayload as CySimpleIOPayload
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, Forbidden, MethodNotAllowed, NotFound, \
     TooManyRequests, Unauthorized
from zato.server.groups.ctx import SecurityGroupsCtx
from zato.server.service.internal import AdminService

# ################################################################################################################################

if 0:
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import any_, anydict, anytuple, callable_, dictnone, stranydict, strlist, strstrdict
    from zato.server.service import Service
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore
    from zato.server.connection.http_soap.url_data import URLData
    BrokerClient = BrokerClient
    ParallelServer = ParallelServer
    Service = Service
    URLData = URLData

# ################################################################################################################################

logger = logging.getLogger('zato_rest')
_logger_is_enabled_for = logger.isEnabledFor
_logging_info = logging.INFO
split_re = regex_compile('........?').findall # type: ignore

# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################

accept_any_http = HTTP_SOAP.ACCEPT.ANY
accept_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

# ################################################################################################################################

# https://tools.ietf.org/html/rfc6585
TOO_MANY_REQUESTS = 429

_status_bad_request = '{} {}'.format(BAD_REQUEST, HTTP_RESPONSES[BAD_REQUEST])
_status_internal_server_error = '{} {}'.format(INTERNAL_SERVER_ERROR, HTTP_RESPONSES[INTERNAL_SERVER_ERROR])
_status_not_found = '{} {}'.format(NOT_FOUND, HTTP_RESPONSES[NOT_FOUND])
_status_method_not_allowed = '{} {}'.format(METHOD_NOT_ALLOWED, HTTP_RESPONSES[METHOD_NOT_ALLOWED])
_status_unauthorized = '{} {}'.format(UNAUTHORIZED, HTTP_RESPONSES[UNAUTHORIZED])
_status_forbidden = '{} {}'.format(FORBIDDEN, HTTP_RESPONSES[FORBIDDEN])
_status_too_many_requests = '{} {}'.format(TOO_MANY_REQUESTS, HTTP_RESPONSES[TOO_MANY_REQUESTS])

# ################################################################################################################################

stack_format = None
_utcnow=utcnow

# ################################################################################################################################

_basic_auth = SEC_DEF_TYPE.BASIC_AUTH

# ################################################################################################################################

status_response = {}
for code, response in HTTP_RESPONSES.items():
    status_response[code] = '{} {}'.format(code, response)

# ################################################################################################################################

class ModuleCtx:
    Channel = CHANNEL.HTTP_SOAP
    No_URL_Match = (None, False)
    Exception_Separator = '*' * 80
    SIO_JSON = SIMPLE_IO.FORMAT.JSON
    SIO_FORM_DATA = SIMPLE_IO.FORMAT.FORM_DATA
    Dict_Like = {DATA_FORMAT.JSON, DATA_FORMAT.DICT, DATA_FORMAT.FORM_DATA}
    Form_Data_Content_Type = ('application/x-www-form-urlencoded', 'multipart/form-data')

# ################################################################################################################################

response_404     = 'URL not found (CID:{})'
response_404_log = 'URL not found `%s` (Method:%s; Accept:%s; CID:%s)'

# ################################################################################################################################

def client_json_error(cid:'str', details:'any_') -> 'str':

    # This may be a tuple of arguments to an exception object
    if isinstance(details, tuple):
        exc_details = []
        for item in details: # type: ignore
            if isinstance(item, bytes):
                item = item.decode('utf8')
            exc_details.append(item)
    else:
        exc_details = details
        if isinstance(exc_details, bytes):
            exc_details = exc_details.decode('utf8')

    message = {'result':'Error', 'cid':cid} # type: stranydict
    if details:
        message['details'] = exc_details

    return dumps(message)

# ################################################################################################################################

client_error_wrapper = {
    DATA_FORMAT.JSON: client_json_error,
}

# ################################################################################################################################

def get_client_error_wrapper(transport:'str', data_format:'str') -> 'callable_':
    try:
        result = client_error_wrapper[transport]
        return result
    except KeyError:
        # Any KeyError must be caught by the caller
        return client_error_wrapper[data_format]

# ################################################################################################################################

class _CachedResponse:
    """ A wrapper for responses served from caches.
    """
    __slots__ = ('payload', 'content_type', 'headers', 'status_code')

    def __init__(self, payload:'any_', content_type:'str', headers:'stranydict', status_code:'int') -> 'None':
        self.payload = payload
        self.content_type = content_type
        self.headers = headers
        self.status_code = status_code

# ################################################################################################################################

class _HashCtx:
    """ Encapsulates information needed to compute a hash value of an incoming request.
    """
    def __init__(
        self,
        raw_request:'str',
        channel_item:'any_',
        channel_params:'stranydict',
        wsgi_environ:'stranydict'
    ) -> 'None':
        self.raw_request = raw_request
        self.channel_item = channel_item
        self.channel_params = channel_params
        self.wsgi_environ = wsgi_environ

# ################################################################################################################################

class RequestDispatcher:
    """ Dispatches all the incoming HTTP requests to appropriate handlers.
    """
    def __init__(
        self,
        *,
        server:'ParallelServer',
        url_data:'URLData',
        request_handler:'RequestHandler',
        simple_io_config:'stranydict',
        return_tracebacks:'bool',
        default_error_message:'str',
        http_methods_allowed:'strlist'
    ) -> 'None':

        self.server = server
        self.url_data = url_data

        self.request_handler = request_handler
        self.simple_io_config = simple_io_config
        self.return_tracebacks = return_tracebacks

        self.default_error_message = default_error_message
        self.http_methods_allowed = http_methods_allowed

# ################################################################################################################################

    def dispatch(
        self,
        cid:'str',
        req_timestamp:'str',
        wsgi_environ:'stranydict',
        worker_store:'WorkerStore',
        user_agent:'str',
        remote_addr:'str',
        _needs_details=_needs_details,
    ) -> 'any_':

        # Reusable
        _has_log_info  = _logger_is_enabled_for(_logging_info)

        # Needed as one of the first steps
        http_method = wsgi_environ['REQUEST_METHOD']
        http_method = http_method if isinstance(http_method, str) else http_method.decode('utf8')

        http_accept = wsgi_environ.get('HTTP_ACCEPT') or accept_any_http
        http_accept = http_accept.replace('*', accept_any_internal).replace('/', 'HTTP_SEP')

        # Needed in later steps
        path_info        = wsgi_environ['PATH_INFO']
        wsgi_raw_uri     = wsgi_environ['RAW_URI']
        wsgi_remote_port = wsgi_environ['REMOTE_PORT']

        # Immediately reject the request if it is not a support HTTP method, no matter what channel
        # it would have otherwise matched.
        if http_method not in self.http_methods_allowed:
            wsgi_environ['zato.http.response.status'] = _status_method_not_allowed
            return client_json_error(cid, 'Unsupported HTTP method')

        # Can we recognize this URL path?
        # This gives us the URL info and security data - but note that here
        # we still haven't validated credentials, only matched the URL.
        # Credentials are checked in a call to self.url_data.check_security
        url_match, channel_item = self.url_data.match(path_info, http_method, http_accept) # type: ignore

        url_match = cast_('str', url_match)
        channel_item = cast_('anydict', channel_item)

        # .. the item itself may be None in case it is a 404 ..
        if channel_item:
            channel_name = channel_item['name']
        else:
            channel_name = '(None)'

        # This is needed in parallel.py's on_wsgi_request
        wsgi_environ['zato.channel_item'] = channel_item

        # Read the raw data
        payload = wsgi_environ['wsgi.input'].read()

        # Store for later use prior to any kind of parsing
        wsgi_environ['zato.http.raw_request'] = payload

        # This dictionary may be populated by a service with HTTP headers,
        # which the headers will be still in the dictionary even if the service
        # raises an exception. In this way we can return both the headers
        # and a non-200 response to the caller.
        zato_response_headers_container = {}

        # .. before proceeding, log what we have learned so far about the request ..
        # .. but do not do it for paths that are explicitly configured to be ignored ..
        if _has_log_info:
            if not path_info in self.server.rest_log_ignore:
                msg  = f'REST cha → cid={cid}; {http_method} {wsgi_raw_uri} name={channel_name}; len={len(payload)}; '
                msg += f'agent={user_agent}; remote-addr={remote_addr}:{wsgi_remote_port}'
                logger.info(msg)

        # .. we have a match and ee can possibly handle the incoming request ..
        if url_match not in ModuleCtx.No_URL_Match: # type: ignore

            try:

                # Raise 404 if the channel is inactive
                if not channel_item['is_active']:
                    logger.warning('url_data:`%s` is not active, raising NotFound', url_match)
                    raise NotFound(cid, 'Channel inactive')

                # This the string pointing to the URL path that we matched
                match_target = channel_item['match_target']

                # This is the channel's security definition, if any
                sec = self.url_data.url_sec[match_target] # type: ignore

                # This may point to security groups attached to this channel
                security_groups_ctx = channel_item.get('security_groups_ctx')

                # Assume we have no form (POST) data by default.
                post_data = {}

                # Extract the form (POST) data in case we expect it and the content type indicates it will exist.
                if channel_item['data_format'] == ModuleCtx.SIO_FORM_DATA:
                    if wsgi_environ.get('CONTENT_TYPE', '').startswith(ModuleCtx.Form_Data_Content_Type):
                        post_data = util_get_form_data(wsgi_environ)

                        # This is handy if someone invoked URLData's OAuth API manually
                        wsgi_environ['zato.oauth.post_data'] = post_data

                #
                # This will check credentials based on a security definition attached to the channel
                #
                if sec.sec_def != ZATO_NONE:

                    if _needs_details:
                        logger.info('*' * 60)

                        logger.info('Channel item: `%s`', channel_item)
                        logger.info('Path info: `%s`', path_info)

                        logger.info('Payload: `%s`', payload)
                        logger.info('POST data: `%s`', post_data)

                        for key, value in sorted(wsgi_environ.items()):
                            logger.info('WSGI key=`%s` value=`%s`', key, value)

                    # Do check credentials based on a security definition
                    _ = self.url_data.check_security(
                        sec,
                        cid,
                        channel_item,
                        path_info,
                        payload,
                        wsgi_environ,
                        post_data,
                        worker_store,
                        enforce_auth=True
                    )

                #
                # This will check credentials based on security groups potentially assigned to the channel ..
                #
                if security_groups_ctx:

                    # .. if we do not have any members, we do not check anything ..
                    if security_groups_ctx.has_members():

                        # .. this will raise an exception if the validation fails.
                        self.check_security_via_groups(cid, channel_item['name'], security_groups_ctx, wsgi_environ)

                #
                # If we are here, it means that credentials are correct or they were not required
                #

                if channel_item['merge_url_params_req']:
                    channel_params = self.request_handler.create_channel_params(
                        url_match, # type: ignore
                        channel_item,
                        wsgi_environ,
                        payload,
                        post_data
                    )
                else:
                    channel_params = {}

                # This is the call that obtains a response.
                response = self.request_handler.handle(cid, url_match, channel_item, wsgi_environ,
                    payload, worker_store, self.simple_io_config, post_data, path_info, channel_params,
                    zato_response_headers_container)

                # Add the default headers.
                wsgi_environ['zato.http.response.headers']['Content-Type'] = response.content_type
                wsgi_environ['zato.http.response.headers'].update(response.headers)
                wsgi_environ['zato.http.response.status'] = status_response[response.status_code]

                if channel_item['content_encoding'] == 'gzip':

                    s = StringIO()
                    with GzipFile(fileobj=s, mode='w') as f: # type: ignore
                        _ = f.write(response.payload)
                    response.payload = s.getvalue()
                    s.close()

                    wsgi_environ['zato.http.response.headers']['Content-Encoding'] = 'gzip'

                # Finally, return payload to the client, potentially deserializing it from CySimpleIO first.
                if isinstance(response.payload, CySimpleIOPayload):
                    payload = response.payload.getvalue()
                    if isinstance(payload, dict):
                        if 'response' in payload:
                            payload = payload['response']
                            payload = dumps(payload)
                else:
                    payload = response.payload

                return payload

            except Exception as e:
                _format_exc = format_exc()
                status = _status_internal_server_error

                if isinstance(e, (ClientHTTPError, ModelValidationError)):

                    response = e.msg
                    status_code = e.status

                    # TODO: Refactor this series of if/else's into a lookup dict.

                    if isinstance(e, Unauthorized):
                        status = _status_unauthorized
                        if e.challenge:
                            wsgi_environ['zato.http.response.headers']['WWW-Authenticate'] = e.challenge

                    elif isinstance(e, (BadRequest, ModelValidationError)):
                        status = _status_bad_request

                        # This is the channel that Dashboard uses and we want to return
                        # all the details in such cases because it is useful during development
                        if channel_item['name'] == MISC.DefaultAdminInvokeChannel:
                            response = e.msg
                        else:
                            needs_msg = e.needs_msg
                            response = e.msg if needs_msg else 'Bad request'

                    elif isinstance(e, NotFound):
                        status = _status_not_found

                    elif isinstance(e, MethodNotAllowed):
                        status = _status_method_not_allowed

                    elif isinstance(e, Forbidden):
                        status = _status_forbidden

                    elif isinstance(e, TooManyRequests):
                        status = _status_too_many_requests

                else:

                    status_code = INTERNAL_SERVER_ERROR

                    # Same comment as in BadRequest, ModelValidationError above
                    if channel_item['name'] == MISC.DefaultAdminInvokeChannel:
                        wsgi_environ['zato.http.response.headers']['X-Zato-Message'] = str(e.args)
                        response = pretty_format_exception(e, cid)
                    else:
                        response = e.args if self.return_tracebacks else self.default_error_message

                # Check whether this was a JSON-based channel, in which case our response should
                # have a JSON data format on ouput too.
                if channel_item['data_format'] == DATA_FORMAT.JSON:
                    wsgi_environ['zato.http.response.headers']['Content-Type'] = CONTENT_TYPE['JSON']

                # We need a traceback unless we merely report information about a missing service,
                # which may happen if enmasse runs before such a service has been deployed.
                needs_traceback = not isinstance(e, ServiceMissingException)

                if needs_traceback:
                    _exc_string = stack_format(e, style='color', show_vals='like_source', truncate_vals=5000,
                        add_summary=True, source_lines=20) if stack_format else _format_exc # type: str

                    # Log what happened
                    logger.info(
                        'Caught an exception, cid:`%s`, status_code:`%s`, `%s`', cid, status_code, _exc_string)

                try:
                    error_wrapper = get_client_error_wrapper(channel_item['transport'], channel_item['data_format'])
                except KeyError:
                    # It is not a data format that we have a wrapper for.
                    if logger.isEnabledFor(TRACE1):
                        msg = 'No client error wrapper for transport:`{}`, data_format:`{}`'.format(
                            channel_item.get('transport'), channel_item.get('data_format'))
                        logger.log(TRACE1, msg)
                else:
                    response = error_wrapper(cid, response)

                wsgi_environ['zato.http.response.status'] = status

                return response

            finally:
                # No matter if we had an exception or not, we can add the headers that the service potentially produced.
                if zato_response_headers_container:
                    wsgi_environ['zato.http.response.headers'].update(zato_response_headers_container)

        # This is 404, no such URL path.
        else:

            # Indicate HTTP 404
            wsgi_environ['zato.http.response.status'] = _status_not_found

            # This is returned to the caller - note that it does not echo back the URL requested ..
            response = response_404.format(cid)

            # .. this goes to logs and it includes the URL sent by the client.
            logger.warning(response_404_log, path_info, wsgi_environ.get('REQUEST_METHOD'), wsgi_environ.get('HTTP_ACCEPT'), cid)

            # This is the payload for the caller
            return response

# ################################################################################################################################

    def check_security_via_groups(
        self,
        cid:'str',
        channel_name:'str',
        security_groups_ctx:'SecurityGroupsCtx',
        wsgi_environ:'stranydict'
    ) -> 'None':

        # Local variables
        sec_def = None

        # Extract Basic Auth information from input ..
        basic_auth_info = wsgi_environ.get('HTTP_AUTHORIZATION')

        # .. extract API key information too ..
        apikey_header_value = wsgi_environ.get(self.server.api_key_header_wsgi)

        # .. we cannot have both on input ..
        if basic_auth_info and apikey_header_value:
            logger.warning('Received both Basic Auth and API key (groups)')
            raise BadRequest(cid)

        # Handle Basic Auth via groups ..
        if basic_auth_info:

            # .. extract credentials ..
            username, password = extract_basic_auth(cid, basic_auth_info)

            # .. run the validation now ..
            if security_id := security_groups_ctx.check_security_basic_auth(cid, channel_name, username, password):
                sec_def = self.url_data.basic_auth_get_by_id(security_id)
            else:
                logger.warning('Invalid Basic Auth credentials (groups)')
                raise Forbidden(cid)

        # Handle API keys via groups ..
        elif apikey_header_value:

            # .. run the validation now ..
            if security_id := security_groups_ctx.check_security_apikey(cid, channel_name, apikey_header_value):
                sec_def = self.url_data.apikey_get_by_id(security_id)
            else:
                logger.warning('Invalid API key (groups)')
                raise Forbidden(cid)

        else:
            logger.warning('Received neither Basic Auth nor API key (groups)')
            raise Forbidden(cid)

        # Now we can enrich the WSGI environment with information
        # that will become self.channel.security for services.
        if sec_def:
            enrich_with_sec_data(wsgi_environ, sec_def, sec_def['sec_type'])

# ################################################################################################################################

class RequestHandler:
    """ Handles individual HTTP requests to a given service.
    """
    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

# ################################################################################################################################

    def _set_response_data(self, service:'Service', **kwargs:'any_'):
        """ A callback invoked by the services after it is done producing the response.
        """
        data_format = kwargs.get('data_format', '')
        transport = kwargs.get('transport', '')

        self.set_payload(service.response, data_format, transport, service)
        self.set_content_type(service.response, data_format)

        return service.response

# ################################################################################################################################

    def _get_flattened(self, params:'str') -> 'anydict':
        """ Returns a QueryDict of parameters with single-element lists unwrapped to point to the sole element directly.
        """
        out = {} # type: anydict

        if params:
            query_params = QueryDict(params, encoding='utf-8')

            for key, value in query_params.lists():
                if len(value) > 1:
                    out[key] = value
                else:
                    out[key] = value[0]

        return out

# ################################################################################################################################

    def create_channel_params(
        self,
        path_params:'strstrdict',
        channel_item:'any_',
        wsgi_environ:'stranydict',
        raw_request:'str',
        post_data:'dictnone'=None,
    ) -> 'strstrdict':
        """ Collects parameters specific to this channel (HTTP) and updates wsgi_environ
        with HTTP-specific data.
        """
        _qs = self._get_flattened(wsgi_environ.get('QUERY_STRING', ''))

        # Our caller has already parsed POST for us so we just use it as is
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
                channel_params = {key:value for key, value in _qs.items()}
            else:
                channel_params = {}
            channel_params.update(path_params)

        wsgi_environ['zato.http.GET'] = _qs
        wsgi_environ['zato.http.POST'] = post

        return channel_params

# ################################################################################################################################

    def get_response_from_cache(
        self,
        service:'Service',
        raw_request:'str',
        channel_item:'any_',
        channel_params:'stranydict',
        wsgi_environ:'stranydict'
    ) -> 'anytuple':
        """ Returns a cached response for incoming request or None if there is nothing cached for it.
        By default, an incoming request's hash is calculated by sha256 over a concatenation of:
          * WSGI REQUEST_METHOD   # E.g. GET or POST
          * WSGI PATH_INFO        # E.g. /my/api
          * sorted(zato.http.GET) # E.g. ?foo=123&bar=456 (query string aka channel_params)
          * payload bytes         # E.g. '{"customer_id":"123"}' - a string object, before parsing
        Note that query string is sorted which means that ?foo=123&bar=456 is equal to ?bar=456&foo=123,
        that is, the order of parameters in query string does not matter.
        """
        if service.get_request_hash:# type: ignore
            hash_value = service.get_request_hash(
                _HashCtx(raw_request, channel_item, channel_params, wsgi_environ) # type: ignore
                )
        else:
            query_string = str(sorted(channel_params.items()))
            data = '%s%s%s%s' % (wsgi_environ['REQUEST_METHOD'], wsgi_environ['PATH_INFO'], query_string, raw_request)
            hash_value = sha256(data.encode('utf8')).hexdigest()
            hash_value = '-'.join(split_re(hash_value)) # type: ignore

        # No matter if hash value is default or from service, always prefix it with channel's type and ID
        cache_key = 'http-channel-%s-%s' % (channel_item['id'], hash_value)

        # We have the key so now we can check if there is any matching response already stored in cache
        response = self.server.get_from_cache(channel_item['cache_type'], channel_item['cache_name'], cache_key)

        # If there is any response, we can now load into a format that our callers expect
        if response:
            response = loads(response)
            response = _CachedResponse(response['payload'], response['content_type'], response['headers'],
                response['status_code'])

        return cache_key, response

# ################################################################################################################################

    def set_response_in_cache(self, channel_item:'any_', key:'str', response:'any_'):
        """ Caches responses from this channel's invocation for as long as the cache is configured to keep it.
        """
        self.server.set_in_cache(channel_item['cache_type'], channel_item['cache_name'], key, dumps({
            'payload': response.payload,
            'content_type': response.content_type,
            'headers': response.headers,
            'status_code': response.status_code,
        }))

# ################################################################################################################################

    def handle(
        self,
        cid:'str',
        url_match:'any_',
        channel_item:'any_',
        wsgi_environ:'stranydict',
        raw_request:'str',
        worker_store:'WorkerStore',
        simple_io_config:'stranydict',
        post_data:'dictnone',
        path_info:'str',
        channel_params:'stranydict',
        zato_response_headers_container:'stranydict',
    ) -> 'any_':
        """ Create a new instance of a service and invoke it.
        """
        service, is_active = self.server.service_store.new_instance(channel_item.service_impl_name)
        if not is_active:
            logger.warning('Could not invoke an inactive service:`%s`, cid:`%s`', service.get_name(), cid)
            raise NotFound(cid, response_404.format(
                path_info, wsgi_environ.get('REQUEST_METHOD'), wsgi_environ.get('HTTP_ACCEPT'), cid))

        # This is needed for type checking to make sure the name is bound
        cache_key = ''

        # If caching is configured for this channel, we need to first check if there is no response already
        if channel_item['cache_type']:
            cache_key, response = self.get_response_from_cache(service, raw_request, channel_item, channel_params, wsgi_environ)
            if response:
                return response

        # Add any path params matched to WSGI environment so it can be easily accessible later on
        wsgi_environ['zato.http.path_params'] = url_match

        # If this is a POST / form submission then it becomes our payload
        if channel_item['data_format'] == ModuleCtx.SIO_FORM_DATA:
            wsgi_environ['zato.request.payload'] = post_data

        # No cache for this channel or no cached response, invoke the service then.
        response = service.update_handle(self._set_response_data, service, raw_request,
            CHANNEL.HTTP_SOAP, channel_item.data_format, channel_item.transport, self.server,
            cast_('BrokerClient', worker_store.broker_client),
            worker_store, cid, simple_io_config, wsgi_environ=wsgi_environ,
            url_match=url_match, channel_item=channel_item, channel_params=channel_params,
            merge_channel_params=channel_item.merge_url_params_req,
            params_priority=channel_item.params_pri,
            zato_response_headers_container=zato_response_headers_container)

        # Cache the response if needed (cache_key was already created on return from get_response_from_cache)
        if channel_item['cache_type']:
            self.set_response_in_cache(channel_item, cache_key, response)

        # Having used the cache or not, we can return the response now
        return response

# ################################################################################################################################

    def _needs_admin_response(
        self,
        service_instance:'Service',
        service_invoker_name:'str'=ServiceConst.ServiceInvokerName
        ) -> 'bool':

        is_admin_service = isinstance(service_instance, AdminService)
        is_admin_ignored = service_instance.name not in {service_invoker_name, 'zato.ping'}

        return is_admin_service and not (is_admin_ignored)

# ################################################################################################################################

    def set_payload(
        self,
        response:'any_',
        data_format:'str',
        transport:'str',
        service_instance:'Service'
    ) -> 'None':
        """ Sets the actual payload to represent the service's response out of what the service produced.
        This includes converting dictionaries into JSON or adding Zato metadata.
        """

        if self._needs_admin_response(service_instance):
            if data_format in {ModuleCtx.SIO_JSON, ModuleCtx.SIO_FORM_DATA}:
                zato_env = {'zato_env':{'result':response.result, 'cid':service_instance.cid, 'details':response.result_details}}
                is_not_str = not isinstance(response.payload, str)
                if is_not_str and response.payload:
                    payload = response.payload.getvalue(False)
                    payload.update(zato_env)
                else:
                    payload = zato_env

                response.payload = dumps(payload)
        else:
            if not isinstance(response.payload, str):
                if isinstance(response.payload, dict) and data_format in ModuleCtx.Dict_Like:
                    response.payload = dumps(response.payload)
                else:
                    if response.payload:
                        if isinstance(response.payload, Model):
                            value = response.payload.to_json()
                        else:
                            if hasattr(response.payload, 'getvalue'):
                                value = response.payload.getvalue() # type: ignore
                            else:
                                # Check if it's a list of models ..
                                is_model_list = isinstance(response.payload, list) and isinstance(response.payload[0], Model)

                                # .. if it is one, we need to turn each of the models into a dict ..
                                if is_model_list:
                                    value = []
                                    for item in response.payload:
                                        value.append(item.to_dict())
                                    value = dumps(value)

                                # .. it's not a list of models.
                                else:
                                    value = dumps(response.payload)
                    else:
                        value = ''
                    response.payload = value

# ################################################################################################################################

    def set_content_type(
        self,
        response:'any_',
        data_format:'str'
    ) -> 'None':
        """ Sets a response's content type if one hasn't been supplied by the user.
        """
        # A user provided his or her own content type ..
        if response.content_type_changed:
            content_type = response.content_type
        else:
            # .. or they did not so let's find out if we're using SimpleIO ..
            if data_format == SIMPLE_IO.FORMAT.JSON:
                content_type = self.server.json_content_type

            # .. alright, let's use the default value after all.
            else:
                content_type = response.content_type

        response.content_type = content_type

# ################################################################################################################################
