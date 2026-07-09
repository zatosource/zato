# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import UNAUTHORIZED
from json import dumps
from logging import getLogger

# requests
import requests

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.odata.auth import AuthHandler, CSRFHandler
from zato.common.odata.batch import build_json, build_multipart, parse_json, parse_multipart
from zato.common.odata.common import Accept_Header, Content_Type_JSON, ODataError, ODataSyntaxError, ODataVersion, \
    extract_entity, extract_items, extract_next_link, parse_error
from zato.common.odata.metadata import parse_metadata
from zato.common.odata.query import build_query, encode_params, format_function_params, format_key, format_literal
from zato.common.typing_ import generator_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odata.batch import batch_request_list, batch_response_list
    from zato.common.odata.metadata import ServiceMetadata
    from zato.common.odata.query import Query
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strdict, strstrdict
    batch_request_list = batch_request_list
    batch_response_list = batch_response_list
    Query = Query
    ServiceMetadata = ServiceMetadata

# ################################################################################################################################
# ################################################################################################################################

anydict_gen = generator_['anydict', None, None]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# How many pages iter walks before stopping, unless configured otherwise.
_default_max_pages = 1000

# The batch formats a client can send.
_batch_multipart = 'multipart'
_batch_json = 'json'

# ################################################################################################################################
# ################################################################################################################################

class ODataClient:
    """ A reusable OData client - one connection's worth of configuration in, plain dicts out.
    It speaks both OData 2.0 and 4.0 over JSON, formats keys and query options per version,
    injects whatever authentication and CSRF tokens the configuration calls for, follows
    server-driven paging, and parses error payloads of either version into one exception type.
    """
    def __init__(self, config:'stranydict') -> 'None':
        self.config = config

        # The service root always ends with a slash so paths can be appended directly.
        self.address = config['address'].rstrip('/') + '/'

        self.odata_version = config.get('odata_version') or ODataVersion.V4
        self.timeout = float(config.get('timeout') or 0) or None
        self.page_size = config.get('page_size') or 0
        self.max_pages = config.get('max_pages') or _default_max_pages

        # Per-system extras ride on every request - headers and query parameters alike.
        self.custom_headers = config.get('custom_headers') or {}
        self.custom_query_params = config.get('custom_query_params') or {}

        self.session = requests.Session()

        self.auth = AuthHandler(config, self.session)

        # SAP systems demand a CSRF token on writes - other systems skip this entirely.
        self.needs_csrf_token = config.get('needs_csrf_token') or False
        self.csrf = CSRFHandler(self.session, self.address)

        # An owning connection wrapper may plug the client into the audit log here -
        # standalone clients, e.g. in tests, run without one.
        self.audit_callback = None

# ################################################################################################################################

    def _verify(self) -> 'any_':
        """ Returns what to pass to requests as its TLS verification - True to verify against
        the system trust store, False to skip it, or a path to a CA bundle to verify against.
        """
        out = self.config.get('validate_tls', True)
        return out

# ################################################################################################################################

    def _client_cert(self) -> 'any_':
        """ Returns what to pass to requests as the client certificate - a single PEM path holding
        both the certificate and its key, a (certificate, key) path pair, or None.
        """
        client_cert = self.config.get('tls_client_cert')

        if not client_cert:
            return None

        if client_key := self.config.get('tls_client_key'):
            out = (client_cert, client_key)
        else:
            out = client_cert

        return out

# ################################################################################################################################

    def _base_headers(self) -> 'strstrdict':
        """ Returns the headers every request starts from - the version-appropriate Accept,
        the V4 version headers, and whatever custom headers the configuration adds.
        """
        headers = {'Accept': Accept_Header[self.odata_version]}

        # V4 requests announce the protocol version both ways the specification describes.
        if self.odata_version == ODataVersion.V4:
            headers['OData-Version'] = ODataVersion.V4
            headers['OData-MaxVersion'] = ODataVersion.V4

        headers.update(self.custom_headers)

        return headers

# ################################################################################################################################

    def _url(self, path:'str', params:'strdict | None'=None) -> 'str':
        """ Builds a full URL out of a path relative to the service root and query parameters,
        merging in the custom parameters the configuration attaches to every request.
        """
        all_params:'strdict' = {}
        all_params.update(self.custom_query_params)

        if params:
            all_params.update(params)

        out = self.address + path

        if all_params:
            out = out + '?' + encode_params(all_params)

        return out

# ################################################################################################################################

    def _send(self, method:'str', url:'str', headers:'strstrdict', body:'any_') -> 'any_':
        """ Sends one request and returns the raw requests response.
        """
        out = self.session.request(
            method,
            url,
            data=body,
            headers=headers,
            verify=self._verify(),
            cert=self._client_cert(),
            timeout=self.timeout,
        )

        return out

# ################################################################################################################################

    def _audited_send(self, method:'str', url:'str', headers:'strstrdict', body:'any_', cid:'str') -> 'any_':
        """ Sends one request through the audit log - the outgoing body, a transport-level
        failure and the raw response are each recorded before the caller parses anything,
        so error payloads are captured too. Returns the raw requests response.
        """
        endpoint = f'{method} {url}'

        # The request goes out exactly as recorded here ..
        if self.audit_callback:
            self.audit_callback(cid, AuditEvent.Request_Sent, endpoint, AuditOutcome.OK, body or b'')

        try:
            out = self._send(method, url, headers, body)
        except Exception as e:

            # .. a transport-level failure means no response ever arrived ..
            if self.audit_callback:
                self.audit_callback(cid, AuditEvent.Response_Received, endpoint, AuditOutcome.Error, str(e))

            # .. which the caller still needs to see.
            raise

        # .. an error payload arrives with an HTTP error status, hence the outcome from response.ok.
        if self.audit_callback:
            outcome = AuditOutcome.OK if out.ok else AuditOutcome.Error
            self.audit_callback(cid, AuditEvent.Response_Received, endpoint, outcome, out.content)

        return out

# ################################################################################################################################

    def _invoke(
        self,
        method:'str',
        url:'str',
        *,
        data:'anydict | None'=None,
        extra_headers:'strstrdict | None'=None,
        raw_body:'bytes | None'=None,
        cid:'str'='',
        ) -> 'any_':
        """ Sends one request with authentication and CSRF handling applied, retrying once
        when a stale OAuth2 token or CSRF token is the reason for a rejection, and raises
        an ODataError for whatever error status remains. Returns the raw requests response.
        """
        headers = self._base_headers()

        if extra_headers:
            headers.update(extra_headers)

        # A JSON body travels serialized, a raw one exactly as given.
        if data is not None:
            body = dumps(data)
            headers['Content-Type'] = Content_Type_JSON
        else:
            body = raw_body

        is_write = method != 'GET'

        self.auth.apply(headers)

        # Writes to SAP systems carry the CSRF token obtained from the service root.
        if is_write:
            if self.needs_csrf_token:
                self.csrf.apply(headers, self.timeout, self._verify(), self._client_cert())

        logger.info('OData out -> %s %s', method, url)

        response = self._audited_send(method, url, headers, body, cid)

        # A stale OAuth2 token gets refreshed and the request goes out once more.
        if response.status_code == UNAUTHORIZED:
            if self.auth.can_retry_on_unauthorized:
                self.auth.invalidate()
                self.auth.apply(headers)
                response = self._audited_send(method, url, headers, body, cid)

        # A stale CSRF token gets refetched and the request goes out once more.
        if is_write:
            if self.needs_csrf_token:
                if self.csrf.is_csrf_rejection(response):
                    self.csrf.invalidate()
                    self.csrf.apply(headers, self.timeout, self._verify(), self._client_cert())
                    response = self._audited_send(method, url, headers, body, cid)

        logger.info('OData out <- %s %s; len=%d', response.status_code, url, len(response.content))

        if not response.ok:
            self._raise_for_error(response)

        return response

# ################################################################################################################################

    def _raise_for_error(self, response:'any_') -> 'None':
        """ Raises the ODataError a rejection carries - parsed from the JSON error payload
        when there is one, built from the raw response otherwise.
        """
        try:
            data = response.json()
        except ValueError:
            data = None

        if data:
            if 'error' in data:
                raise parse_error(response.status_code, data)

        raise ODataError(response.status_code, '', response.text, [])

# ################################################################################################################################

    def _parse_json(self, response:'any_') -> 'anydict':
        """ Parses a response body as JSON, surfacing anything else as a syntax error.
        """
        try:
            out = response.json()
        except ValueError:
            raise ODataSyntaxError(f'Could not parse a response as JSON -> `{response.text}`')

        return out

# ################################################################################################################################

    def _entity_path(self, entity_set:'str', key:'any_') -> 'str':
        """ Returns the resource path of one entity - the set's name with the formatted
        key predicate appended, e.g. Customers('ALFKI') or SalesOrders(OrderID=1,Line=2).
        """
        formatted = format_key(key, self.odata_version)

        out = f'{entity_set}({formatted})'
        return out

# ################################################################################################################################

    def read(self, entity_set:'str', query:'Query | None'=None, cid:'str'='', **options:'any_') -> 'anylist':
        """ Reads entities from a set with optional query options and returns them as a list -
        one request's worth, use iter to walk all pages.
        """
        built = build_query(query, **options)
        params = built.to_params(self.odata_version)

        url = self._url(entity_set, params)

        response = self._invoke('GET', url, cid=cid)
        data = self._parse_json(response)

        out = extract_items(data, self.odata_version)
        return out

# ################################################################################################################################

    def iter(self, entity_set:'str', query:'Query | None'=None, cid:'str'='', **options:'any_') -> 'anydict_gen':
        """ Iterates over all entities in a set, transparently following the server's
        next-page links - '@odata.nextLink' in V4, '__next' in V2 - up to max_pages pages.
        """
        built = build_query(query, **options)
        params = built.to_params(self.odata_version)

        url = self._url(entity_set, params)

        # An optional page size is a preference V4 servers understand.
        extra_headers = {}
        if self.page_size:
            if self.odata_version == ODataVersion.V4:
                extra_headers['Prefer'] = f'odata.maxpagesize={self.page_size}'

        pages_read = 0

        while url:
            response = self._invoke('GET', url, extra_headers=extra_headers, cid=cid)
            data = self._parse_json(response)

            for item in extract_items(data, self.odata_version):
                yield item

            pages_read += 1
            if pages_read >= self.max_pages:
                break

            # The next link is absolute or relative to the service root, per the server's choice.
            next_link = extract_next_link(data, self.odata_version)

            if next_link:
                if next_link.startswith('http'):
                    url = next_link
                else:
                    url = self.address + next_link.lstrip('/')
            else:
                url = None

# ################################################################################################################################

    def get(self, entity_set:'str', key:'any_', query:'Query | None'=None, cid:'str'='', **options:'any_') -> 'anydict':
        """ Reads one entity by its key and returns it as a dict.
        """
        built = build_query(query, **options)
        params = built.to_params(self.odata_version)

        path = self._entity_path(entity_set, key)
        url = self._url(path, params)

        response = self._invoke('GET', url, cid=cid)
        data = self._parse_json(response)

        out = extract_entity(data, self.odata_version)
        return out

# ################################################################################################################################

    def create(self, entity_set:'str', data:'anydict', cid:'str'='') -> 'anydict':
        """ Creates an entity in a set and returns the server's representation of it -
        an empty dict when the server preferred to return nothing.
        """
        url = self._url(entity_set)

        response = self._invoke('POST', url, data=data, cid=cid)

        # A 204 means the server chose not to echo the entity back.
        if not response.content:
            return {}

        parsed = self._parse_json(response)

        out = extract_entity(parsed, self.odata_version)
        return out

# ################################################################################################################################

    def update(self, entity_set:'str', key:'any_', data:'anydict', etag:'str'='', cid:'str'='') -> 'anydict':
        """ Updates an entity by its key with a partial document - PATCH in V4, MERGE in V2.
        An ETag travels in If-Match when given, which servers that enforce optimistic
        concurrency require. Returns the updated entity when the server echoes it back.
        """
        path = self._entity_path(entity_set, key)
        url = self._url(path)

        # V2 predates PATCH, its partial updates are spelled MERGE.
        if self.odata_version == ODataVersion.V2:
            method = 'MERGE'
        else:
            method = 'PATCH'

        extra_headers = {}
        if etag:
            extra_headers['If-Match'] = etag

        response = self._invoke(method, url, data=data, extra_headers=extra_headers, cid=cid)

        if not response.content:
            return {}

        parsed = self._parse_json(response)

        out = extract_entity(parsed, self.odata_version)
        return out

# ################################################################################################################################

    def delete(self, entity_set:'str', key:'any_', etag:'str'='', cid:'str'='') -> 'None':
        """ Deletes an entity by its key, optionally with an ETag in If-Match.
        """
        path = self._entity_path(entity_set, key)
        url = self._url(path)

        extra_headers = {}
        if etag:
            extra_headers['If-Match'] = etag

        _ = self._invoke('DELETE', url, extra_headers=extra_headers, cid=cid)

# ################################################################################################################################

    def call_function(self, name:'str', params:'anydict | None'=None, cid:'str'='') -> 'any_':
        """ Calls a function - a GET whose parameters travel inline in the path in V4,
        e.g. GetNearestAirport(lat=33,lon=-118), and as query parameters in V2.
        """
        query_params:'strdict' = {}

        if params:

            # V4 functions take their parameters in parentheses, V2 in the query string.
            if self.odata_version == ODataVersion.V4:
                formatted = format_function_params(params, self.odata_version)
                path = f'{name}({formatted})'
            else:
                path = name
                for param_name, param_value in params.items():
                    query_params[param_name] = format_literal(param_value, self.odata_version)

        else:
            path = name

        url = self._url(path, query_params)

        response = self._invoke('GET', url, cid=cid)

        if not response.content:
            return None

        data = self._parse_json(response)

        out = extract_entity(data, self.odata_version)
        return out

# ################################################################################################################################

    def call_action(self, name:'str', data:'anydict | None'=None, cid:'str'='') -> 'any_':
        """ Calls an action - a POST whose parameters travel as a JSON body.
        """
        url = self._url(name)

        response = self._invoke('POST', url, data=data or {}, cid=cid)

        if not response.content:
            return None

        parsed = self._parse_json(response)

        out = extract_entity(parsed, self.odata_version)
        return out

# ################################################################################################################################

    def count(self, entity_set:'str', filter:'str'='', cid:'str'='') -> 'int': # noqa: A002
        """ Returns the number of entities in a set, optionally narrowed by a filter -
        the $count path segment both versions expose.
        """
        params:'strdict' = {}
        if filter:
            params['$filter'] = filter

        url = self._url(f'{entity_set}/$count', params)

        response = self._invoke('GET', url, cid=cid)

        out = int(response.text)
        return out

# ################################################################################################################################

    def batch(self, requests_:'batch_request_list', format:'str'=_batch_multipart, cid:'str'='') -> 'batch_response_list': # noqa: A002
        """ Sends a $batch of requests and returns their responses in order - multipart
        for either version, or the V4 JSON format when asked for.
        """
        url = self._url('$batch')

        if format == _batch_json:
            body_dict = build_json(requests_)
            response = self._invoke('POST', url, data=body_dict, cid=cid)

            parsed = self._parse_json(response)

            out = parse_json(parsed)

        else:
            body, content_type = build_multipart(requests_)
            extra_headers = {'Content-Type': content_type}

            response = self._invoke('POST', url, raw_body=body, extra_headers=extra_headers, cid=cid)

            out = parse_multipart(response.content, response.headers.get('Content-Type', ''))

        return out

# ################################################################################################################################

    def metadata(self, cid:'str'='') -> 'ServiceMetadata':
        """ Retrieves and parses the service's $metadata document.
        """
        url = self._url('$metadata')

        extra_headers = {'Accept': 'application/xml'}

        response = self._invoke('GET', url, extra_headers=extra_headers, cid=cid)

        out = parse_metadata(response.content)
        return out

# ################################################################################################################################

    def ping(self) -> 'int':
        """ Pings the service root and returns the HTTP status code.
        """
        headers = self._base_headers()
        self.auth.apply(headers)

        response = self.session.get(
            self.address,
            headers=headers,
            verify=self._verify(),
            cert=self._client_cert(),
            timeout=self.timeout,
        )

        out = response.status_code
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        """ Releases the underlying HTTP session.
        """
        self.session.close()

# ################################################################################################################################
# ################################################################################################################################
