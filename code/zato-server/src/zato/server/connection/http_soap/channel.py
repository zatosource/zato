# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import socket
import struct
from datetime import datetime as _datetime_class, timedelta as _timedelta, timezone as _timezone
from email.utils import format_datetime as _format_datetime
from gzip import GzipFile
from hashlib import sha256
from http.client import INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_FOUND, TOO_MANY_REQUESTS
from io import StringIO
from traceback import format_exc
from typing import NamedTuple

# regex
from regex import compile as regex_compile

# Zato
from zato.common.api import CHANNEL, CONTENT_TYPE, DATA_FORMAT, HTTP_SOAP, MISC, SEC_DEF_TYPE, SIMPLE_IO, \
    TRACE1, URL_PARAMS_PRIORITY, ZATO_NONE
from zato.common.const import ServiceConst
from zato.common.exception import HTTP_RESPONSES, BackendInvocationError, ServiceMissingException
from zato.common.json_ import dumps
from zato.common.json_internal import loads
from zato.common.marshal_.api import Model, ModelValidationError
from zato.common.rate_limiting.common import current_time_us
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, utcnow
from zato.common.util.auth import enrich_with_sec_data, extract_basic_auth
from zato.common.util.exception import pretty_format_exception
from zato.common.util.http_ import get_form_data as util_get_form_data, QueryDict
from zato.cy.reqresp.payload import SimpleIOPayload as CySimpleIOPayload
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, Forbidden, NotFound, Unauthorized
from zato.server.groups.ctx import SecurityGroupsCtx
from zato.server.service.internal import AdminService

# ################################################################################################################################

if 0:
    from zato.common.config_dispatcher import ConfigDispatcher
    from zato.common.rate_limiting.cidr import SlottedCheckResult
    from zato.common.typing_ import any_, anydict, anytuple, callable_, dictnone, stranydict, strlist, strstrdict
    from zato.server.service import Service
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore
    from zato.server.connection.http_soap.url_data import URLData
    ConfigDispatcher = ConfigDispatcher
    ParallelServer = ParallelServer
    Service = Service
    SlottedCheckResult = SlottedCheckResult
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

_status_internal_server_error = '{} {}'.format(INTERNAL_SERVER_ERROR, HTTP_RESPONSES[INTERNAL_SERVER_ERROR])
_status_not_found = '{} {}'.format(NOT_FOUND, HTTP_RESPONSES[NOT_FOUND])
_status_method_not_allowed = '{} {}'.format(METHOD_NOT_ALLOWED, HTTP_RESPONSES[METHOD_NOT_ALLOWED])
_status_too_many_requests = '{} {}'.format(TOO_MANY_REQUESTS, HTTP_RESPONSES[TOO_MANY_REQUESTS])

_socket_SOL_SOCKET = socket.SOL_SOCKET
_socket_SO_LINGER = socket.SO_LINGER
_so_linger_on = struct.pack('ii', 1, 0)
_microseconds_per_second = 1_000_000
_utc = _timezone.utc

def _datetime_utcnow():
    return _datetime_class.now(_utc)
_content_type_json = CONTENT_TYPE['JSON']
_content_type_sse = 'text/event-stream'
_streaming_flag = 'zato.mcp.is_streaming'
_bad_request_types = (BadRequest, ModelValidationError, BackendInvocationError)
_default_admin_channel = MISC.DefaultAdminInvokeChannel

# ################################################################################################################################

stack_format = None
_utcnow=utcnow

# ################################################################################################################################

_basic_auth = SEC_DEF_TYPE.BASIC_AUTH

_sec_def_key_prefix_map = {
    SEC_DEF_TYPE.BASIC_AUTH: 'basic{}:',
    SEC_DEF_TYPE.APIKEY:     'apikey{}:',
}

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

class _RequestMeta(NamedTuple):
    http_method: 'str'
    http_accept: 'str'
    path_info: 'str'
    wsgi_raw_uri: 'str'
    wsgi_remote_port: 'str'

# ################################################################################################################################

class _URLMatchResult(NamedTuple):
    url_match: 'str'
    channel_item: 'anydict'
    channel_name: 'str'
    payload: 'bytes'

# ################################################################################################################################

class _ErrorClassification(NamedTuple):
    status: 'str'
    response: 'any_'
    status_code: 'int'

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

    def _extract_request_meta(self, wsgi_environ:'stranydict') -> '_RequestMeta':
        """ Extracts HTTP method, accept header, path and port from the WSGI environment.
        """
        http_method = wsgi_environ['REQUEST_METHOD']

        http_accept = wsgi_environ.get('HTTP_ACCEPT') or accept_any_http
        http_accept = http_accept.replace('*', accept_any_internal).replace('/', 'HTTP_SEP')

        out = _RequestMeta(
            http_method=http_method,
            http_accept=http_accept,
            path_info=wsgi_environ['PATH_INFO'],
            wsgi_raw_uri=wsgi_environ['RAW_URI'],
            wsgi_remote_port=wsgi_environ['REMOTE_PORT'],
        )

        return out

# ################################################################################################################################

    def _log_incoming_request(
        self,
        cid:'str',
        meta:'_RequestMeta',
        channel_item:'anydict',
        channel_name:'str',
        payload:'bytes',
        user_agent:'str',
        remote_addr:'str',
    ) -> 'None':
        """ Logs a summary of the incoming REST request unless the path is explicitly ignored.
        """
        if meta.path_info not in self.server.rest_log_ignore:
            service_name = channel_item['service_name'] if channel_item else '<no-channel>'
            logger.info(
                f'REST cha \u2192 cid={cid}; {meta.http_method} {meta.wsgi_raw_uri} name={channel_name};'
                f' service={service_name}; len={len(payload)}; agent={user_agent};'
                f' remote-addr={remote_addr}:{meta.wsgi_remote_port}'
            )

# ################################################################################################################################

    def _extract_post_data(self, channel_item:'anydict', wsgi_environ:'stranydict') -> 'anydict':
        """ Extracts form/POST data from the WSGI environment if the channel expects it.
        """
        post_data:'anydict' = {}

        if channel_item['data_format'] == ModuleCtx.SIO_FORM_DATA:
            if wsgi_environ.get('CONTENT_TYPE', '').startswith(ModuleCtx.Form_Data_Content_Type):
                post_data = util_get_form_data(wsgi_environ)
                wsgi_environ['zato.oauth.post_data'] = post_data

        return post_data

# ################################################################################################################################

    def _check_security(
        self,
        cid:'str',
        meta:'_RequestMeta',
        channel_item:'anydict',
        wsgi_environ:'stranydict',
        payload:'bytes',
        post_data:'anydict',
        worker_store:'WorkerStore',
        _needs_details:'bool'=_needs_details,
    ) -> 'None':
        """ Validates credentials via sec_def and security groups.
        Both check_security and check_security_via_groups may raise exceptions.
        """
        match_target = channel_item['match_target']
        sec = self.url_data.url_sec[match_target] # type: ignore

        security_groups_ctx = channel_item.get('security_groups_ctx')

        if sec.sec_def != ZATO_NONE:

            if _needs_details:
                logger.info('*' * 60)

                logger.info('Channel item: `%s`', channel_item)
                logger.info('Path info: `%s`', meta.path_info)

                logger.info('Payload: `%s`', payload)
                logger.info('POST data: `%s`', post_data)

                for key, value in sorted(wsgi_environ.items()):
                    logger.info('WSGI key=`%s` value=`%s`', key, value)

            # .. this will raise an exception if the sec_def check fails ..
            _ = self.url_data.check_security(
                sec,
                cid,
                channel_item,
                meta.path_info,
                payload,
                wsgi_environ,
                post_data,
                worker_store,
                enforce_auth=True
            )

        if security_groups_ctx:
            if security_groups_ctx.has_members():

                # .. this will raise an exception if the group check fails ..
                self.check_security_via_groups(cid, channel_item['name'], security_groups_ctx, wsgi_environ)

# ################################################################################################################################

    def _invoke_service(
        self,
        cid:'str',
        meta:'_RequestMeta',
        url_match:'str',
        channel_item:'anydict',
        wsgi_environ:'stranydict',
        payload:'bytes',
        post_data:'anydict',
        worker_store:'WorkerStore',
        zato_response_headers_container:'anydict',
    ) -> 'any_':
        """ Builds channel params and calls request_handler.handle.
        """
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

        out = self.request_handler.handle(cid, url_match, channel_item, wsgi_environ,
            payload, worker_store, self.simple_io_config, post_data, meta.path_info, channel_params,
            zato_response_headers_container)

        return out

# ################################################################################################################################

    def _format_response(self, channel_item:'anydict', wsgi_environ:'stranydict', response:'any_') -> 'any_':
        """ Sets response headers, applies gzip if needed, and unwraps CySimpleIO.
        """
        wsgi_environ['zato.http.response.headers']['Content-Type'] = response.content_type
        wsgi_environ['zato.http.response.headers'].update(response.headers)
        wsgi_environ['zato.http.response.status'] = status_response[response.status_code]

        # SSE streaming responses bypass gzip and serialization entirely ..
        if response.content_type == _content_type_sse:
            out = response.payload
            return out

        if channel_item['content_encoding'] == 'gzip':

            s = StringIO()
            with GzipFile(fileobj=s, mode='w') as f: # type: ignore
                _ = f.write(response.payload)
            response.payload = s.getvalue()
            s.close()

            wsgi_environ['zato.http.response.headers']['Content-Encoding'] = 'gzip'

        if isinstance(response.payload, CySimpleIOPayload):
            out = response.payload.getvalue()
            if isinstance(out, dict):
                if 'response' in out:
                    out = out['response']
                    out = dumps(out)
        else:
            out = response.payload

        return out

# ################################################################################################################################

    def _authenticate_and_invoke(
        self,
        cid:'str',
        meta:'_RequestMeta',
        url_match:'str',
        channel_item:'anydict',
        wsgi_environ:'stranydict',
        payload:'bytes',
        worker_store:'WorkerStore',
        zato_response_headers_container:'anydict',
        remote_addr:'str',
        now_us:'int',
    ) -> 'any_':
        """ Checks security, builds channel params and invokes the service.
        """
        if not channel_item['is_active']:
            logger.warning('url_data:`%s` is not active, raising NotFound', url_match)
            raise NotFound(cid, 'Channel inactive')

        post_data = self._extract_post_data(channel_item, wsgi_environ)

        # .. this will raise an exception if credentials are invalid ..
        self._check_security(cid, meta, channel_item, wsgi_environ, payload, post_data, worker_store)

        # .. now that auth succeeded, check sec_def rate limiting first ..
        sec_def_rate_limit_result = self._check_sec_def_rate_limiting(wsgi_environ, remote_addr, now_us)

        if sec_def_rate_limit_result:
            if not sec_def_rate_limit_result.is_allowed:
                out = self._handle_rate_limit_result(
                    cid, sec_def_rate_limit_result, wsgi_environ, remote_addr, channel_item)
                return out

        # .. then check channel rate limiting ..
        channel_id = channel_item['id']
        rate_limit_key_prefix = f'rest{channel_id}:'
        channel_rate_limit_result = self.server.rate_limiting_manager.check(
            channel_id, remote_addr, now_us, rate_limit_key_prefix)

        if channel_rate_limit_result:
            if not channel_rate_limit_result.is_allowed:
                out = self._handle_rate_limit_result(
                    cid, channel_rate_limit_result, wsgi_environ, remote_addr, channel_item)
                return out

        # .. invoke the service ..
        response = self._invoke_service(
            cid, meta, url_match, channel_item, wsgi_environ,
            payload, post_data, worker_store, zato_response_headers_container)

        out = self._format_response(channel_item, wsgi_environ, response)

        return out

# ################################################################################################################################

    def _classify_error(
        self,
        cid:'str',
        e:'Exception',
        channel_item:'anydict',
        wsgi_environ:'stranydict',
    ) -> '_ErrorClassification':
        """ Determines HTTP status and response body based on exception type.
        """
        headers = wsgi_environ['zato.http.response.headers']

        if isinstance(e, (ClientHTTPError, ModelValidationError)):

            response = e.msg
            status_code = e.status
            status = status_response[status_code]

            if isinstance(e, Unauthorized):
                if e.challenge:
                    headers['WWW-Authenticate'] = e.challenge

            elif isinstance(e, _bad_request_types):
                if channel_item['name'] != _default_admin_channel:
                    needs_msg = e.needs_msg
                    response = e.msg if needs_msg else 'Bad request'

        else:

            status_code = INTERNAL_SERVER_ERROR
            status = _status_internal_server_error

            if channel_item['name'] == _default_admin_channel:
                headers['X-Zato-Message'] = str(e.args)
                response = pretty_format_exception(e, cid)
            else:
                response = e.args if self.return_tracebacks else self.default_error_message

        out = _ErrorClassification(
            status=status,
            response=response,
            status_code=status_code,
        )

        return out

# ################################################################################################################################

    def _log_dispatch_error(
        self,
        cid:'str',
        e:'Exception',
        status_code:'int',
        _exc_formatted:'str',
    ) -> 'None':
        """ Logs the exception traceback unless it is a ServiceMissingException.
        """
        if isinstance(e, ServiceMissingException):
            return

        _exc_string = stack_format(e, style='color', show_vals='like_source', truncate_vals=5000,
            add_summary=True, source_lines=20) if stack_format else _exc_formatted # type: str

        logger.info('Caught an exception, cid:`%s`, status_code:`%s`, `%s`', cid, status_code, _exc_string)

# ################################################################################################################################

    def _wrap_error_response(
        self,
        cid:'str',
        response:'any_',
        channel_item:'anydict',
    ) -> 'any_':
        """ Wraps the error response using the appropriate client error wrapper.
        """
        try:
            error_wrapper = get_client_error_wrapper(channel_item['transport'], channel_item['data_format'])
        except KeyError:
            if logger.isEnabledFor(TRACE1):
                msg = 'No client error wrapper for transport:`{}`, data_format:`{}`'.format(
                    channel_item.get('transport'), channel_item.get('data_format'))
                logger.log(TRACE1, msg)
        else:
            response = error_wrapper(cid, response)

        out = response
        return out

# ################################################################################################################################

    def _handle_dispatch_error(
        self,
        cid:'str',
        e:'Exception',
        channel_item:'anydict',
        wsgi_environ:'stranydict',
    ) -> 'any_':
        """ Handles all exceptions raised during _authenticate_and_invoke.
        Determines the HTTP status, formats the response, and sets response headers.
        """
        _exc_formatted = format_exc()
        headers = wsgi_environ['zato.http.response.headers']

        err = self._classify_error(cid, e, channel_item, wsgi_environ)

        if channel_item['data_format'] == DATA_FORMAT.JSON:
            headers['Content-Type'] = _content_type_json

        self._log_dispatch_error(cid, e, err.status_code, _exc_formatted)

        response = self._wrap_error_response(cid, err.response, channel_item)

        wsgi_environ['zato.http.response.status'] = err.status

        out = response
        return out

# ################################################################################################################################

    def _match_url(self, meta:'_RequestMeta', wsgi_environ:'stranydict') -> '_URLMatchResult':
        """ Matches the request URL, reads the raw payload and stores preliminary data in wsgi_environ.
        """
        url_match, channel_item = self.url_data.match(meta.path_info, meta.http_method, meta.http_accept) # type: ignore

        url_match = cast_('str', url_match)
        channel_item = cast_('anydict', channel_item)

        # .. the item itself may be None in case it is a 404 ..
        if channel_item:
            channel_name = channel_item['name']
        else:
            channel_name = '(None)'

        # .. this is needed by the request handler ..
        wsgi_environ['zato.channel_item'] = channel_item

        # .. read the raw data ..
        payload = wsgi_environ['zato.http.raw_request']

        out = _URLMatchResult(
            url_match=url_match,
            channel_item=channel_item,
            channel_name=channel_name,
            payload=payload,
        )

        return out

# ################################################################################################################################

    def dispatch(
        self,
        cid:'str',
        req_timestamp:'str',
        wsgi_environ:'stranydict',
        worker_store:'WorkerStore',
        user_agent:'str',
        remote_addr:'str',
    ) -> 'any_':

        # Reusable
        _has_log_info = _logger_is_enabled_for(_logging_info)

        # Extract core request metadata from the WSGI environment
        meta = self._extract_request_meta(wsgi_environ)

        # Immediately reject the request if it is not a support HTTP method, no matter what channel
        # it would have otherwise matched.
        if meta.http_method not in self.http_methods_allowed:
            wsgi_environ['zato.http.response.status'] = _status_method_not_allowed
            return client_json_error(cid, 'Unsupported HTTP method')

        # Match the URL, read the raw payload and store preliminary data in wsgi_environ
        url_match_result = self._match_url(meta, wsgi_environ)
        url_match = url_match_result.url_match
        channel_item = url_match_result.channel_item
        channel_name = url_match_result.channel_name
        payload = url_match_result.payload

        # This dictionary may be populated by a service with HTTP headers,
        # which the headers will be still in the dictionary even if the service
        # raises an exception. In this way we can return both the headers
        # and a non-200 response to the caller.
        zato_response_headers_container = {}

        # .. before proceeding, log what we have learned so far about the request ..
        if _has_log_info:
            self._log_incoming_request(cid, meta, channel_item, channel_name, payload, user_agent, remote_addr)

        # .. we have a match and we can possibly handle the incoming request ..
        if url_match not in ModuleCtx.No_URL_Match: # type: ignore

            now_us = current_time_us()

            try:

                # .. this will raise an exception on auth error ..
                out = self._authenticate_and_invoke(
                    cid, meta, url_match, channel_item, wsgi_environ,
                    payload, worker_store, zato_response_headers_container,
                    remote_addr, now_us,
                )

                return out

            except Exception as e:
                out = self._handle_dispatch_error(cid, e, channel_item, wsgi_environ)
                return out

            finally:
                if zato_response_headers_container:
                    wsgi_environ['zato.http.response.headers'].update(zato_response_headers_container)

        # This is 404, no such URL path.
        else:

            # Indicate HTTP 404
            wsgi_environ['zato.http.response.status'] = _status_not_found

            # This is returned to the caller - note that it does not echo back the URL requested ..
            response = response_404.format(cid)

            # .. this goes to logs and it includes the URL sent by the client.
            logger.warning(response_404_log, meta.path_info, meta.http_method, meta.http_accept, cid)

            # This is the payload for the caller
            return response

# ################################################################################################################################

    def _check_sec_def_rate_limiting(
        self,
        wsgi_environ:'stranydict',
        remote_addr:'str',
        now_us:'int',
    ) -> 'SlottedCheckResult | None':
        """ Checks rate limiting for the security definition that authenticated this request.
        Returns the check result if rate limiting applies, or None if no sec_def or no rules configured.
        """

        # Check if a security definition was resolved during authentication ..
        sec_def_info = wsgi_environ.get('zato.sec_def')

        if not sec_def_info:
            return None

        # .. extract the sec_def type and ID ..
        sec_def_type = sec_def_info['type']
        sec_def_id = sec_def_info['id']

        # .. look up the key prefix template for this sec_def type ..
        prefix_template = _sec_def_key_prefix_map.get(sec_def_type)

        if not prefix_template:
            return None

        # .. build the key prefix ..
        key_prefix = prefix_template.format(sec_def_id)

        # .. log the known sec_def IDs before the check ..
        known_ids = list(self.server.rate_limiting_manager._sec_def_matchers.keys())

        # .. and check rate limiting.
        out = self.server.rate_limiting_manager.check_sec_def(sec_def_id, remote_addr, now_us, key_prefix)

        return out

# ################################################################################################################################

    def _handle_rate_limit_result(
        self,
        cid:'str',
        rate_limit_result:'SlottedCheckResult',
        wsgi_environ:'stranydict',
        remote_addr:'str',
        channel_item:'stranydict',
    ) -> 'any_':
        """ Handles rate limiting outcomes - either a silent TCP drop for disallowed traffic
        or an HTTP 429 for rate-limited traffic. Called from dispatch when the check result
        indicates the request should not proceed.
        """

        channel_name = channel_item['name']

        # Disallowed traffic - silent TCP drop, as if a firewall discarded the packet ..
        if rate_limit_result.is_disallowed:

            fd = wsgi_environ['zato.socket_fd']
            raw_socket = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.setsockopt(_socket_SOL_SOCKET, _socket_SO_LINGER, _so_linger_on)
            raw_socket.close()
            os.close(fd)

            # Tell the caller to skip all response processing
            wsgi_environ['zato.http.rate_limit.dropped'] = True

            out = b''

            return out

        # .. otherwise this is rate-limited traffic - return HTTP 429.
        retry_after_us = rate_limit_result.retry_after_us
        retry_after_seconds = retry_after_us // _microseconds_per_second

        # Round up if there is any remainder
        if retry_after_us % _microseconds_per_second:
            retry_after_seconds += 1

        now = _datetime_utcnow()
        retry_at = now + _timedelta(seconds=retry_after_seconds)
        retry_after_date = _format_datetime(retry_at, usegmt=True)

        logger.info('Rate limiting 429; cid:%s, channel:%s, remote_addr:%s, retry_after:%s',
            cid, channel_name, remote_addr, retry_after_date)

        wsgi_environ['zato.http.response.status'] = _status_too_many_requests
        wsgi_environ['zato.http.response.headers']['Retry-After'] = retry_after_date

        out = client_json_error(cid, 'Too many requests')

        return out

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

    def _get_flattened(self, params:'bytes') -> 'anydict':
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
        raw_request:'bytes',
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
        raw_request:'bytes',
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
        raw_request:'bytes',
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
            cast_('ConfigDispatcher', worker_store.config_dispatcher),
            worker_store, cid, simple_io_config, wsgi_environ=wsgi_environ,
            url_match=url_match, channel_item=channel_item, channel_params=channel_params,
            merge_channel_params=channel_item.merge_url_params_req,
            params_priority=channel_item.params_pri,
            zato_response_headers_container=zato_response_headers_container)

        # Cache the response if needed (cache_key was already created on return from get_response_from_cache),
        # .. but streaming responses must not be cached because they are iterators, not serializable.
        if channel_item['cache_type']:
            if not wsgi_environ.get(_streaming_flag):
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
                                if isinstance(value, dict):
                                    value = dumps(value)
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
