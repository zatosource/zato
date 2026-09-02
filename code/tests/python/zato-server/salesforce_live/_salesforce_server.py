# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
from http.client import BAD_REQUEST, CREATED, NO_CONTENT, NOT_FOUND, OK, UNAUTHORIZED
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from urllib.parse import parse_qs, urlparse

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, strnone, strset

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestHandler(BaseHTTPRequestHandler):
    """ Simulates the Salesforce REST paths the connection uses - the OAuth2 token endpoint,
    the resource listing that answers pings, sObject creation, reads, updates, deletes
    and upserts by external ID, and SOQL queries with pagination.
    """

    # Credentials the token endpoint expects
    expected_username:'strnone' = None
    expected_password:'strnone' = None
    expected_consumer_key:'strnone' = None
    expected_consumer_secret:'strnone' = None

    # The REST API version the instance serves
    api_version:'strnone' = None

    # Tokens issued so far - every API request must carry one of them
    valid_tokens:'strset' = set()

    # How many tokens were issued so far
    issued_token_count = 0

    # The state of the simulated instance
    campaigns:'anydict' = {}

    # How many campaigns were created so far, used to build new IDs
    campaign_counter = 0

    # How many records a single query response carries - larger result sets are paginated
    query_page_size = 2

    # Query locators for pagination - maps each locator to the records it still holds
    query_locators:'anydict' = {}

    def log_message(self, format:'any_', *args:'any_') -> 'None':
        pass

# ################################################################################################################################

    def _send_json(self, status:'int', data:'any_') -> 'None':
        text = dumps(data)
        body = text.encode('utf8')

        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        _ = self.wfile.write(body)

# ################################################################################################################################

    def _send_no_content(self) -> 'None':
        self.send_response(NO_CONTENT)
        self.end_headers()

# ################################################################################################################################

    def _read_json_body(self) -> 'anydict':
        content_length_header = self.headers['Content-Length']
        content_length = int(content_length_header)
        body = self.rfile.read(content_length)

        out = loads(body.decode('utf8'))
        return out

# ################################################################################################################################

    def _reject_token_request(self) -> 'None':
        self._send_json(BAD_REQUEST, {
            'error': 'invalid_grant',
            'error_description': 'authentication failure',
        })

# ################################################################################################################################

    def _handle_token_request(self, params:'anydict') -> 'None':
        """ POST /services/oauth2/token - the credentials arrive as query parameters
        and a valid set of them is answered with a fresh access token.
        """

        # What each credential parameter has to carry for the request to be accepted.
        expected_credentials = {
            'username': self.expected_username,
            'password': self.expected_password,
            'client_id': self.expected_consumer_key,
            'client_secret': self.expected_consumer_secret,
        }

        for param_name, expected_value in expected_credentials.items():

            # Each credential arrives as a single-element list of query parameter values
            # and a request may omit it entirely ..
            if not (values := params.get(param_name)):
                self._reject_token_request()
                return

            # .. and a present one still has to match.
            if values[0] != expected_value:
                self._reject_token_request()
                return

        # Issue a new token and remember it so API requests can present it later
        token = 'token.' + CryptoManager.generate_hex_string()
        SalesforceTestHandler.valid_tokens.add(token)
        SalesforceTestHandler.issued_token_count += 1

        self._send_json(OK, {
            'access_token': token,
            'token_type': 'Bearer',
            'instance_url': 'http://127.0.0.1',
        })

# ################################################################################################################################

    def _check_bearer_token(self) -> 'bool':
        """ Every API request must carry one of the tokens the token endpoint issued.
        """

        if not (authorization := self.headers.get('Authorization')):
            return False

        if not authorization.startswith('Bearer '):
            return False

        token = authorization[len('Bearer '):]

        out = token in self.valid_tokens
        return out

# ################################################################################################################################

    def _handle_resource_listing(self) -> 'None':
        """ GET /services/data/v{version}/ - the resources the API version serves,
        which is what answers pings.
        """
        self._send_json(OK, {
            'sobjects': f'/services/data/v{self.api_version}/sobjects',
            'query': f'/services/data/v{self.api_version}/query',
        })

# ################################################################################################################################

    def _store_new_campaign(self, request_data:'anydict') -> 'str':
        SalesforceTestHandler.campaign_counter += 1
        campaign_id = '701{:015d}'.format(self.campaign_counter)

        campaign = dict(request_data)
        campaign['Id'] = campaign_id

        SalesforceTestHandler.campaigns[campaign_id] = campaign

        out = campaign_id
        return out

# ################################################################################################################################

    def _send_campaign_not_found(self, campaign_id:'str') -> 'None':
        self._send_json(NOT_FOUND, [{
            'errorCode': 'NOT_FOUND',
            'message': f'The requested resource does not exist: {campaign_id}',
        }])

# ################################################################################################################################

    def _handle_campaign_create(self) -> 'None':
        """ POST /services/data/v{version}/sobjects/Campaign/ - a new campaign record.
        """

        request_data = self._read_json_body()
        campaign_id = self._store_new_campaign(request_data)

        self._send_json(OK, {
            'id': campaign_id,
            'success': True,
            'errors': [],
        })

# ################################################################################################################################

    def _handle_campaign_get(self, campaign_id:'str') -> 'None':
        """ GET /services/data/v{version}/sobjects/Campaign/{id} - a single campaign record.
        """

        if campaign_id not in self.campaigns:
            self._send_campaign_not_found(campaign_id)
            return

        self._send_json(OK, self.campaigns[campaign_id])

# ################################################################################################################################

    def _handle_campaign_update(self, campaign_id:'str') -> 'None':
        """ PATCH /services/data/v{version}/sobjects/Campaign/{id} - updates the fields
        the request carries, answered with 204 No Content the way Salesforce answers updates.
        """

        if campaign_id not in self.campaigns:
            self._send_campaign_not_found(campaign_id)
            return

        request_data = self._read_json_body()

        campaign = self.campaigns[campaign_id]
        campaign.update(request_data)

        self._send_no_content()

# ################################################################################################################################

    def _handle_campaign_delete(self, campaign_id:'str') -> 'None':
        """ DELETE /services/data/v{version}/sobjects/Campaign/{id} - removes the record,
        answered with 204 No Content the way Salesforce answers deletes.
        """

        if campaign_id not in self.campaigns:
            self._send_campaign_not_found(campaign_id)
            return

        del SalesforceTestHandler.campaigns[campaign_id]

        self._send_no_content()

# ################################################################################################################################

    def _handle_campaign_upsert(self, external_id_field:'str', external_id_value:'str') -> 'None':
        """ PATCH /services/data/v{version}/sobjects/Campaign/{field}/{value} - updates
        the record whose external ID matches or creates a new one, the way a Salesforce upsert works.
        """

        request_data = self._read_json_body()

        # Update the matching record if there is one ..
        for campaign in self.campaigns.values():

            # A record may have been created without this external ID field at all.
            if campaign.get(external_id_field) == external_id_value:
                campaign.update(request_data)
                self._send_no_content()
                return

        # .. otherwise, create a new record that carries the external ID.
        campaign_data = dict(request_data)
        campaign_data[external_id_field] = external_id_value

        campaign_id = self._store_new_campaign(campaign_data)

        self._send_json(CREATED, {
            'id': campaign_id,
            'success': True,
            'errors': [],
            'created': True,
        })

# ################################################################################################################################

    def _send_query_page(self, records:'anylist', total_size:'int') -> 'None':
        """ Sends one page of query results, with a locator to the next page when more records remain.
        """

        page_size = self.query_page_size

        page = records[:page_size]
        remaining = records[page_size:]
        is_done = not remaining

        response:'anydict' = {
            'totalSize': total_size,
            'done': is_done,
            'records': page,
        }

        # More records remain, so store them under a locator the client can follow.
        if remaining:
            locator = '01g' + CryptoManager.generate_hex_string()
            SalesforceTestHandler.query_locators[locator] = {
                'records': remaining,
                'total_size': total_size,
            }
            response['nextRecordsUrl'] = f'/services/data/v{self.api_version}/query/{locator}'

        self._send_json(OK, response)

# ################################################################################################################################

    def _handle_query(self, params:'anydict') -> 'None':
        """ GET /services/data/v{version}/query/ - a SOQL query, answered with every
        campaign record the instance holds, paginated the way Salesforce paginates queries.
        """

        if not params.get('q'):
            self._send_json(BAD_REQUEST, [{
                'errorCode': 'MALFORMED_QUERY',
                'message': 'The q parameter is required',
            }])
            return

        records = []

        for campaign in self.campaigns.values():
            record = dict(campaign)
            record['attributes'] = {'type': 'Campaign'}
            records.append(record)

        total_size = len(records)
        self._send_query_page(records, total_size)

# ################################################################################################################################

    def _handle_query_next(self, locator:'str') -> 'None':
        """ GET /services/data/v{version}/query/{locator} - the next page of an earlier query.
        """

        # A locator can be followed once - each page consumes it and issues the next one.
        if not (entry := SalesforceTestHandler.query_locators.pop(locator, None)):
            self._send_json(NOT_FOUND, [{
                'errorCode': 'INVALID_QUERY_LOCATOR',
                'message': f'invalid query locator: {locator}',
            }])
            return

        records = entry['records']
        total_size = entry['total_size']

        self._send_query_page(records, total_size)

# ################################################################################################################################

    def _handle_request(self, method:'str') -> 'None':

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)

        # The token endpoint is the only path that carries no bearer token ..
        if path == '/services/oauth2/token':
            if method == 'POST':
                self._handle_token_request(params)
                return

        # .. every other path requires a token that the token endpoint issued.
        if not self._check_bearer_token():
            self._send_json(UNAUTHORIZED, [{
                'errorCode': 'INVALID_SESSION_ID',
                'message': 'Session expired or invalid',
            }])
            return

        api_base = f'/services/data/v{self.api_version}'

        # .. the resource listing, which is what answers pings ..
        if path == api_base + '/':
            if method == 'GET':
                self._handle_resource_listing()
                return

        campaign_prefix = api_base + '/sobjects/Campaign/'

        # .. campaign creation ..
        if path == campaign_prefix:
            if method == 'POST':
                self._handle_campaign_create()
                return

        # .. paths that address campaign records ..
        if path.startswith(campaign_prefix):

            remainder = path[len(campaign_prefix):]
            parts = remainder.split('/')
            part_count = len(parts)

            # .. a single campaign record ..
            if part_count == 1:
                campaign_id = parts[0]
                if method == 'GET':
                    self._handle_campaign_get(campaign_id)
                    return
                if method == 'PATCH':
                    self._handle_campaign_update(campaign_id)
                    return
                if method == 'DELETE':
                    self._handle_campaign_delete(campaign_id)
                    return

            # .. an upsert by external ID ..
            if part_count == 2:
                if method == 'PATCH':
                    external_id_field = parts[0]
                    external_id_value = parts[1]
                    self._handle_campaign_upsert(external_id_field, external_id_value)
                    return

        # .. a SOQL query ..
        query_prefix = api_base + '/query/'

        if path == query_prefix:
            if method == 'GET':
                self._handle_query(params)
                return

        # .. the next page of an earlier query.
        if path.startswith(query_prefix):
            locator = path[len(query_prefix):]
            if method == 'GET':
                self._handle_query_next(locator)
                return

        # No handler matched the path.
        self._send_json(NOT_FOUND, [{
            'errorCode': 'NOT_FOUND',
            'message': f'No such path: {method} {path}',
        }])

# ################################################################################################################################

    def do_GET(self) -> 'None':
        self._handle_request('GET')

# ################################################################################################################################

    def do_POST(self) -> 'None':
        self._handle_request('POST')

# ################################################################################################################################

    def do_PATCH(self) -> 'None':
        self._handle_request('PATCH')

# ################################################################################################################################

    def do_DELETE(self) -> 'None':
        self._handle_request('DELETE')

# ################################################################################################################################
# ################################################################################################################################

def start_salesforce_server(
    port:'int',
    username:'str',
    password:'str',
    consumer_key:'str',
    consumer_secret:'str',
    api_version:'str',
    ) -> 'anytuple':
    """ Starts the simulated Salesforce instance in a background thread. Returns (server, thread).
    """

    SalesforceTestHandler.expected_username = username
    SalesforceTestHandler.expected_password = password
    SalesforceTestHandler.expected_consumer_key = consumer_key
    SalesforceTestHandler.expected_consumer_secret = consumer_secret
    SalesforceTestHandler.api_version = api_version

    SalesforceTestHandler.valid_tokens = set()
    SalesforceTestHandler.issued_token_count = 0
    SalesforceTestHandler.campaigns = {}
    SalesforceTestHandler.campaign_counter = 0
    SalesforceTestHandler.query_locators = {}

    server = ThreadingHTTPServer(('127.0.0.1', port), SalesforceTestHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server, thread

# ################################################################################################################################
# ################################################################################################################################
