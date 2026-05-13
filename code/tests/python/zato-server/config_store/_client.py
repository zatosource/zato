# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ZatoClient:

    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self._auth = b64encode(f'admin.invoke:{password}'.encode()).decode()
        self.base_url = f'http://{host}:{port}/zato/api/invoke'

# ################################################################################################################################

    def invoke(self, service_name, payload=None):
        url = f'{self.base_url}/{service_name}'
        body = json.dumps(payload).encode() if payload else b'{}'

        logger.info('-> %s %s', service_name, body.decode())

        req = Request(url, data=body, method='POST')
        req.add_header('Authorization', f'Basic {self._auth}')
        req.add_header('Content-Type', 'application/json')

        try:
            with urlopen(req) as resp:
                raw = resp.read()
        except HTTPError as e:
            raw = e.read()
            logger.error('<- %s HTTP %s: %s', service_name, e.code, raw.decode('utf-8', errors='replace'))
            raise Exception(f'{service_name} returned HTTP {e.code}: {raw.decode("utf-8", errors="replace")}')

        if not raw:
            logger.info('<- %s (empty)', service_name)
            return {}

        result = json.loads(raw)

        if isinstance(result, dict) and result.get('is_success') is False:
            info = result.get('info', '(no details)')
            logger.error('<- %s FAILED: %s', service_name, info)
            raise Exception(f'{service_name} failed on server side:\n{info}')

        logger.info('<- %s %s', service_name, raw.decode()[:200])

        return result

# ################################################################################################################################

    def get_list(self, service_name, **params):
        response = self.invoke(service_name, params or None)
        if isinstance(response, dict) and 'data' in response:
            return response['data'], response.get('_meta', {})
        if isinstance(response, list):
            return response, {}
        return response, {}

# ################################################################################################################################

    def create(self, service_name, **params):
        return self.invoke(service_name, params)

# ################################################################################################################################

    def edit(self, service_name, **params):
        return self.invoke(service_name, params)

# ################################################################################################################################

    def delete(self, service_name, **params):
        return self.invoke(service_name, params)

# ################################################################################################################################

    def ping(self, service_name, **params):
        return self.invoke(service_name, params)

# ################################################################################################################################
# ################################################################################################################################
