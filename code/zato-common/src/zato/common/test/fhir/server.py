# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import socket
import threading
from base64 import b64encode
from logging import getLogger
from time import sleep

# Zato
from zato.common.test.fhir.common import FHIRHTTPServer, OAuthTokenIssuer, auth_type_basic, auth_type_oauth, token_path
from zato.common.test.fhir.handler import FHIRRequestHandler
from zato.common.test.fhir.store import FHIRStore
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the server to start accepting connections, in seconds
_start_timeout = 10.0

# How long to sleep between connection attempts while waiting for the server, in seconds
_start_sleep_time = 0.1

# ################################################################################################################################
# ################################################################################################################################

class FHIRTestServer:
    """ An in-memory FHIR R4 server for use in tests, listening on the loopback interface only.
    It implements the spec's RESTful API - capabilities, create, read, vread, update, patch, delete, search
    and the transaction and batch interactions with urn:uuid reference resolution -
    with resource versioning, searchset Bundles and OperationOutcome errors. Authentication is optional
    and matches what the FHIR outgoing connection supports - Basic Auth, or OAuth bearer tokens issued
    by the server's own RFC 6749 token endpoint, with the credentials acting as client_id and client_secret.
    """
    def __init__(self, username:'str'='', password:'str'='', auth_type:'str'='') -> 'None':

        # Connection details for clients
        self.host = '127.0.0.1'
        self.port = get_free_port()

        # Optional credentials - empty means the server is open. With Basic Auth they are
        # the username and password, with OAuth they are the client ID and client secret.
        self.username = username
        self.password = password

        # Credentials without an explicit auth type mean Basic Auth
        if username:
            if not auth_type:
                auth_type = auth_type_basic

        self.auth_type = auth_type

        # The store that holds all the resources
        self.store = FHIRStore()

        # The HTTP server and its thread, populated in .start
        self._server:'FHIRHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ The base URL clients connect to.
        """
        out = f'http://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    @property
    def token_endpoint(self) -> 'str':
        """ The URL OAuth tokens are issued at - this is what a Bearer token security definition
        points its auth_server_url to.
        """
        out = f'{self.address}{token_path}'
        return out

# ################################################################################################################################

    def _build_auth_header(self) -> 'strnone':
        """ Builds the exact Authorization header the server expects for Basic Auth, or None otherwise.
        """
        if self.auth_type != auth_type_basic:
            return None

        credentials = f'{self.username}:{self.password}'
        credentials = credentials.encode('ascii')
        credentials = b64encode(credentials)
        credentials = credentials.decode('ascii')

        out = f'Basic {credentials}'
        return out

# ################################################################################################################################

    def _build_token_issuer(self) -> 'OAuthTokenIssuer | None':
        """ Builds the OAuth token issuer, or None if the server does not use OAuth.
        """
        if self.auth_type != auth_type_oauth:
            return None

        out = OAuthTokenIssuer(self.username, self.password)
        return out

# ################################################################################################################################

    def _wait_until_accepting_connections(self) -> 'None':

        # Keep trying until the server accepts connections or we run out of time
        attempts = int(_start_timeout / _start_sleep_time)

        for _ in range(attempts):
            try:
                with socket.create_connection((self.host, self.port), timeout=1.0):
                    return
            except OSError:
                sleep(_start_sleep_time)

        # If we are here, the server never came up
        raise Exception(f'FHIR test server did not start within {_start_timeout}s on {self.host}:{self.port}')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the HTTP server in a daemon thread and waits until it accepts connections.
        """
        auth_header = self._build_auth_header()
        token_issuer = self._build_token_issuer()

        address = (self.host, self.port)
        server = FHIRHTTPServer(
            address, FHIRRequestHandler, self.store, self.address, self.auth_type, auth_header, token_issuer)

        self._server = server

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._thread = thread

        self._wait_until_accepting_connections()

        logger.info('FHIR test server started on %s', self.address)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Shuts down the HTTP server.
        """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._thread = None

            logger.info('FHIR test server stopped on %s', self.address)

# ################################################################################################################################

    def import_resource(self, resource:'stranydict') -> 'str':
        """ Stores a single resource, keeping its own ID if it has one. Returns the ID used.
        """
        out = self.store.import_resource(resource)
        return out

# ################################################################################################################################

    def import_directory(self, directory:'str') -> 'int':
        """ Recursively imports all FHIR resources found in JSON files under a directory,
        e.g. the StructureDefinitions, ValueSets and CodeSystems of an implementation guide.
        Returns how many resources were imported.
        """
        count = 0

        for root, _, file_names in os.walk(directory):

            for file_name in sorted(file_names):

                if not file_name.endswith('.json'):
                    continue

                file_path = os.path.join(root, file_name)

                with open(file_path, encoding='utf8') as json_file:
                    data = json_file.read()

                # Skip files that are not JSON despite their extension ..
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError:
                    continue

                # .. and files whose JSON is not a FHIR resource.
                if not isinstance(parsed, dict):
                    continue

                if 'resourceType' not in parsed:
                    continue

                _ = self.store.import_resource(parsed)
                count += 1

        logger.info('Imported %d resources from %s', count, directory)

        out = count
        return out

# ################################################################################################################################
# ################################################################################################################################
