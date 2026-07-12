# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ZatoClient:
    """ HTTP client for invoking Zato server services during tests.
    """

    def __init__(self, host:'str', port:'int', password:'str') -> 'None':

        # Build the Basic auth header ..
        credentials = f'admin.invoke:{password}'
        credentials_bytes = credentials.encode()
        encoded = b64encode(credentials_bytes)

        # .. store instance state.
        self.host = host
        self.port = port
        self._auth = encoded.decode()
        self.base_url = f'http://{host}:{port}/zato/api/invoke'

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'anydict | None' = None) -> 'anydict':
        """ Invokes a Zato service by name and returns the parsed response.
        """

        # Build the request ..
        url = f'{self.base_url}/{service_name}'

        if payload:
            payload_json = json.dumps(payload)
            body = payload_json.encode()
        else:
            body = b'{}'

        logger.info('[DIAG] ZatoClient.invoke client_id=%s url=%r body=%s', hex(id(self)), url, body.decode())

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        # .. send it and read the response ..
        try:
            with urlopen(request) as response:
                raw = response.read()

        except HTTPError as exception:
            error_body = exception.read()
            error_text = error_body.decode('utf-8', errors='replace')
            logger.error('<- %s HTTP %s: %s', service_name, exception.code, error_text)
            raise Exception(f'{service_name} returned HTTP {exception.code}: {error_text}')

        # .. handle an empty response ..
        if not raw:
            logger.info('<- %s (empty)', service_name)
            return {}

        # .. parse the JSON ..
        result = json.loads(raw)

        # .. check for server-side failure ..
        if 'is_success' in result:
            if not result['is_success']:
                details = result['info']
                logger.error('<- %s FAILED: %s', service_name, details)
                raise Exception(f'{service_name} failed on server side:\n{details}')

        raw_decoded = raw.decode()
        preview = raw_decoded[:200]
        logger.info('<- %s %s', service_name, preview)

        return result

# ################################################################################################################################

    def get_list(self, service_name:'str', **parameters:'anydict') -> 'tuple':
        """ Invokes a list service and returns a (data, meta) tuple.
        Pagination metadata comes from HTTP response headers, not the body.
        """

        response = self.invoke(service_name, parameters or None)

        if isinstance(response, list):
            out = response, {}
            return out

        out = response, {}
        return out

# ################################################################################################################################

    def create(self, service_name:'str', **parameters:'anydict') -> 'anydict':
        """ Creates an object via a Zato service.
        """
        out = self.invoke(service_name, parameters)
        return out

# ################################################################################################################################

    def edit(self, service_name:'str', **parameters:'anydict') -> 'anydict':
        """ Edits an object via a Zato service.
        """
        out = self.invoke(service_name, parameters)
        return out

# ################################################################################################################################

    def delete(self, service_name:'str', **parameters:'anydict') -> 'anydict':
        """ Deletes an object via a Zato service.
        """
        out = self.invoke(service_name, parameters)
        return out

# ################################################################################################################################
# ################################################################################################################################
