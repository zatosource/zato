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

# Zato
from _hr_data import Department_Engineering, get_all_employees, get_department_head_counts, get_employees_by_department, \
    Proc_Get_Department_Summary, Proc_Get_Employees, Proc_Get_Employees_By_Department

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The outgoing connection the enmasse template defines
_connection_name = 'test.mssql.db'

# The statement the execute test runs - the same procedure as callproc, invoked as a T-SQL statement
_exec_statement = f'exec {Proc_Get_Employees}'

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'any_':

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
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

def _get_client(zato_server:'anydict') -> '_AdminClient':
    out = _AdminClient(zato_server['base_url'], zato_server['invoke_password'])
    return out

# ################################################################################################################################

def _callproc(client:'_AdminClient', service_name:'str', proc_name:'str', params:'anylist') -> 'anylist':
    """ Calls a stored procedure through one of the callproc services and returns its result sets.
    """
    out = client.invoke(service_name, {
        'conn_name': _connection_name,
        'proc_name': proc_name,
        'params': params,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMSSQLStoredProcedures:

    def test_callproc_returns_all_employees(self, zato_server:'anydict') -> 'None':
        """ A procedure without parameters returns one result set with all the HR rows as dicts.
        """
        client = _get_client(zato_server)
        result_sets = _callproc(client, 'test.mssql.db.callproc', Proc_Get_Employees, [])

        assert len(result_sets) == 1

        employees = result_sets[0]
        assert employees == get_all_employees()

# ################################################################################################################################

    def test_callproc_with_parameter_filters_by_department(self, zato_server:'anydict') -> 'None':
        """ A procedure with an input parameter returns only the rows the parameter selects.
        """
        client = _get_client(zato_server)
        result_sets = _callproc(client, 'test.mssql.db.callproc', Proc_Get_Employees_By_Department, [Department_Engineering])

        assert len(result_sets) == 1

        employees = result_sets[0]
        expected = get_employees_by_department(Department_Engineering)

        assert employees == expected
        assert len(employees) == 2

# ################################################################################################################################

    def test_callproc_returns_multiple_result_sets(self, zato_server:'anydict') -> 'None':
        """ A procedure with two selects returns two result sets, in the order the procedure produced them.
        """
        client = _get_client(zato_server)
        result_sets = _callproc(client, 'test.mssql.db.callproc', Proc_Get_Department_Summary, [])

        assert len(result_sets) == 2

        head_counts, employees = result_sets

        assert head_counts == get_department_head_counts()
        assert employees == get_all_employees()

# ################################################################################################################################

    def test_callproc_with_yield_returns_the_same_rows(self, zato_server:'anydict') -> 'None':
        """ Consuming the result sets one by one gives the same rows as receiving them all at once.
        """
        client = _get_client(zato_server)
        result_sets = _callproc(client, 'test.mssql.db.callproc-yield', Proc_Get_Department_Summary, [])

        assert len(result_sets) == 2

        head_counts, employees = result_sets

        assert head_counts == get_department_head_counts()
        assert employees == get_all_employees()

# ################################################################################################################################

    def test_execute_exec_statement(self, zato_server:'anydict') -> 'None':
        """ A procedure invoked as an exec statement through execute returns its rows as dicts.
        """
        client = _get_client(zato_server)
        employees = client.invoke('test.mssql.db.execute', {
            'conn_name': _connection_name,
            'query': _exec_statement,
        })

        assert employees == get_all_employees()

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ A ping through the MS SQL connection completes and reports its response time.
        """
        client = _get_client(zato_server)
        result = client.invoke('test.mssql.db.ping', {
            'conn_name': _connection_name,
        })

        assert result['response_time'] > 0

# ################################################################################################################################
# ################################################################################################################################
