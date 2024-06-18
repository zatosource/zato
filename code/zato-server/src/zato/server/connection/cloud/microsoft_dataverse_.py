# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class AuthType:
    Cookie = 'Cookie'
    Bearer_Token = 'BearerToken'

# ################################################################################################################################
# ################################################################################################################################

class DataverseClient:
    base_url: 'str'
    auth_type: 'str'
    cookie: 'str'
    bearer_token: 'str'

    @staticmethod
    def from_config(config:'strdict') -> 'DataverseClient':

        # Local variables
        base_url:'str' = config['base_url']
        if base_url.endswith('/'):
            base_url = base_url[:-1]

        out = DataverseClient()
        out.base_url = base_url
        out.auth_type = config['auth_type']

        if out.auth_type == AuthType.Cookie:
            out.cookie = config['cookie']

        return out

# ################################################################################################################################

    def _get_headers(self) -> 'strdict':

        # Our response to produce
        out = {}

        # Populate the headers
        out['Content-Type'] = 'application/json'
        out['OData-MaxVersion'] = '4.0'
        out['OData-Version'] = '4.0'

        if self.auth_type == AuthType.Cookie:
            out['Cookie'] = self.cookie
        else:
            out['Authorization'] = f'Bearer {self.bearer_token}'

        # Finally, we can return it to our caller
        return out

# ################################################################################################################################

    def _get_full_address(self, path:'str') -> 'str':
        return f'{self.base_url}{path}'

# ################################################################################################################################

    def _impl_get(self, path:'str') -> 'any_':

        # Base headers that are sent with each request
        headers = self._get_headers()

        # The address we're connecting to
        address = self._get_full_address(path)

        # Do send it now ..
        response = requests.get(address, headers=headers)

        # .. extract the response ..
        respose = response.text

        print()
        print(111, response)
        print(222, address)
        print(333, path)
        print()

        # .. convert it to a Python object ..
        respose = loads(respose)

        # .. and return it to our caller.
        return respose

# ################################################################################################################################

    def ping(self):
        _ = self._impl_get('/WhoAmI')

# ################################################################################################################################

    def get_by_id(self, table:'str', object_id:'str') -> 'strdict':

        # Local variables
        path = f'/{table}({object_id})'

        # Invoke the endpoint ..
        respose = self._impl_get(path)

        # .. and return its response to our caller.
        return respose

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import os

    # Local variables
    test_account_id = os.environ['Zato_Dataverse_Test_Account_ID']

    config = {}
    config['auth_type'] = AuthType.Cookie
    config['base_url'] = os.environ['Zato_Dataverse_Base_URL']
    config['cookie'] = os.environ['Zato_Dataverse_Cookie']

    client = DataverseClient.from_config(config)
    client.ping()

    response = client.get_by_id('accounts', test_account_id)

    print()
    print(444, response)
    print()

# ################################################################################################################################
# ################################################################################################################################
