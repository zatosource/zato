# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# requests
import requests

# Zato
from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response

# ################################################################################################################################
# ################################################################################################################################

_Timeout = 15

_CRM_URL      = 'https://zato.io/tutorial/api/get-user'
_CRM_Request  = {'UserName': 'Mike'}
_CRM_Expected = {'UserType': 'RGV', 'AccountNumber': '123456'}

_Billing_URL      = 'https://zato.io/tutorial/api/balance/get'
_Billing_Params   = {'USER': 'Mike'}
_Billing_Expected = {'ACC_BALANCE': '357.9'}

# ################################################################################################################################
# ################################################################################################################################

def check_response(name:'str', response:'Response', expected:'stranydict') -> 'None':
    """ Confirms that a tutorial endpoint replied with the expected status code and JSON payload.
    """
    # Make sure the endpoint replied successfully ..
    if response.status_code != OK:
        raise Exception(f'{name}: unexpected status code {response.status_code} from {response.url}')

    # .. extract the payload ..
    data = response.json()

    # .. and confirm it is exactly what the tutorial documents.
    if data != expected:
        raise Exception(f'{name}: unexpected response {data}, expected {expected}')

    print(f'{name}: OK')

# ################################################################################################################################

def main() -> 'None':
    """ Invokes the tutorial endpoints documented at zato.io and validates their responses.
    """
    # Invoke the CRM endpoint ..
    crm_response = requests.get(_CRM_URL, json=_CRM_Request, timeout=_Timeout)
    check_response('CRM', crm_response, _CRM_Expected)

    # .. and the Billing one.
    billing_response = requests.post(_Billing_URL, params=_Billing_Params, timeout=_Timeout)
    check_response('Billing', billing_response, _Billing_Expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
