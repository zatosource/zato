# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

class ZatoClient:

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self._auth = b64encode(f'admin.invoke:{password}'.encode()).decode()

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'dict | None'=None) -> 'dict':
        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode() if payload else b'{}'

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {self._auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################
