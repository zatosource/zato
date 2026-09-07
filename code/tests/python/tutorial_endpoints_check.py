# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# requests
import requests

# SQLAlchemy
from sqlalchemy import create_engine, text

# Zato
from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response

# ################################################################################################################################
# ################################################################################################################################

_Timeout = 15

_User_Name = 'Mike Johnson'

_CRM_URL      = 'https://zato.io/tutorial/api/get-user'
_CRM_Request  = {'UserName': _User_Name}
_CRM_Expected = {'UserType': 'RGV', 'AccountNumber': '123456'}

_Billing_URL      = 'https://zato.io/tutorial/api/balance/get'
_Billing_Params   = {'USER': _User_Name}
_Billing_Expected = {'ACC_BALANCE': '357.9'}

# The SQL connection exactly as the tutorial has the reader configure it in Dashboard,
# and the query exactly as the tutorial's service runs it.
_Billing_SQL_Engine   = 'postgresql+pg8000'
_Billing_SQL_Host     = 'zato.io'
_Billing_SQL_Port     = 35432
_Billing_SQL_DB_Name  = 'billing'
_Billing_SQL_Username = 'tutorial'
_Billing_SQL_Password = 'demo'
_Billing_SQL_Query    = 'SELECT account_balance FROM balance WHERE user_name = :name'
_Billing_SQL_Params   = {'name': _User_Name}
_Billing_SQL_Expected = {'account_balance': '357.9'}

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

def check_billing_sql() -> 'None':
    """ Connects to the tutorial's Billing database and confirms that the tutorial's query returns the documented row.
    """
    url = '{}://{}:{}@{}:{}/{}'.format(
        _Billing_SQL_Engine, _Billing_SQL_Username, _Billing_SQL_Password, _Billing_SQL_Host, _Billing_SQL_Port,
        _Billing_SQL_DB_Name)

    # A fresh engine, the same way a reader's first query goes out ..
    engine = create_engine(url, connect_args={'timeout': _Timeout})

    try:

        # .. run the tutorial's query with its named parameter ..
        with engine.connect() as conn:
            result = conn.execute(text(_Billing_SQL_Query), _Billing_SQL_Params)
            column_names = result.keys()
            rows = [dict(zip(column_names, row)) for row in result]

        # .. exactly one row is expected, as the tutorial's service calls .one() ..
        if len(rows) != 1:
            raise Exception(f'Billing SQL: expected one row, got {len(rows)}: {rows}')

        # .. and it must carry the balance the tutorial documents.
        row = rows[0]
        if row != _Billing_SQL_Expected:
            raise Exception(f'Billing SQL: unexpected row {row}, expected {_Billing_SQL_Expected}')

    finally:
        engine.dispose()

    print('Billing SQL: OK')

# ################################################################################################################################

def main() -> 'None':
    """ Invokes the tutorial endpoints documented at zato.io and validates their responses.
    """
    # Invoke the CRM endpoint ..
    crm_response = requests.get(_CRM_URL, json=_CRM_Request, timeout=_Timeout)
    check_response('CRM', crm_response, _CRM_Expected)

    # .. the Billing REST one ..
    billing_response = requests.post(_Billing_URL, params=_Billing_Params, timeout=_Timeout)
    check_response('Billing', billing_response, _Billing_Expected)

    # .. and the Billing database itself, the way the tutorial's service queries it.
    check_billing_sql()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
