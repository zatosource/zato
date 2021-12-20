# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps, loads
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# Requests
import requests

# Zato
from zato.common.test.config import TestConfig as Config
from zato.sso import status_code

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, callable_, optional

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RESTClientTestCase(TestCase):
    def __init__(self, *args, **kwargs) -> 'None': # type: ignore
        super().__init__(*args, **kwargs)
        self.rest_client = _RESTClient()

# ################################################################################################################################

    def get(self, *args, **kwargs): # type: ignore
        return self.rest_client.get(*args, **kwargs)

# ################################################################################################################################

    def post(self, *args, **kwargs): # type: ignore
        return self.rest_client.post(*args, **kwargs)

# ################################################################################################################################

    def patch(self, *args, **kwargs): # type: ignore
        return self.rest_client.patch(*args, **kwargs)

# ################################################################################################################################

    def delete(self, *args, **kwargs): # type: ignore
        return self.rest_client.delete(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class _RESTClient:

    def _invoke(
        self,
        func,      # type: callable_
        func_name, # type: str
        url_path,  # type: str
        request,   # type: any_
        expect_ok, # type: bool
        auth=None, # type: optional[anytuple]
        _unexpected=object() # type: any_
        ) -> 'Bunch':

        address = Config.server_address.format(url_path)
        request['current_app'] = Config.current_app
        data = dumps(request)

        logger.info('Invoking %s %s with %s', func_name, address, data)
        response = func(address, data=data, auth=auth)

        logger.info('Response received %s %s', response.status_code, response.text)

        data = loads(response.text)
        data = bunchify(data)

        # Most SSO tests require status OK and CID
        if expect_ok:
            cid = data.get('cid', _unexpected)
            if cid is _unexpected:
                raise Exception('Unexpected CID found in request `{}`'.format(response.text))
            if data.status != status_code.ok:
                raise Exception('Unexpected status found in request `{}` ({})'.format(response.text, data.status))

        return data

# ################################################################################################################################

    def get(self, url_path:'str', request:'str', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.get, 'GET', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def post(self, url_path:'str', request:'str', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.post, 'POST', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def patch(self, url_path:'str', request:'str', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.patch, 'PATCH', url_path, request, expect_ok, auth)

# ################################################################################################################################

    def delete(self, url_path:'str', request:'str', expect_ok:'bool'=True, auth:'any_'=None) -> 'Bunch':
        return self._invoke(requests.delete, 'DELETE', url_path, request, expect_ok, auth)

# ################################################################################################################################
# ################################################################################################################################
