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

# pytest
import pytest

# Zato
from _hr_data import Department_Engineering, Department_Sales, get_all_employees, get_department_head_counts, \
    get_employees_by_department, Proc_Get_Department_Summary, Proc_Get_Employees, Proc_Get_Employees_By_Department, \
    Table_Name
from live_sql.containers import connect_mssql

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strdictnone, strlist

# ################################################################################################################################
# ################################################################################################################################

# The outgoing connection the enmasse template defines
_connection_name = 'test.mssql.db'

# The statement the execute test runs - the same procedure as callproc, invoked as a T-SQL statement
_exec_statement = f'exec {Proc_Get_Employees}'

# The columns every query below selects, in the order the seed rows have them
_columns = 'employee_id, first_name, last_name, department, salary'

# The queries the tests run
_select_all           = f'select {_columns} from {Table_Name} order by employee_id'
_select_by_department = f'select {_columns} from {Table_Name} where department = :department order by employee_id'
_select_by_id         = f'select {_columns} from {Table_Name} where employee_id = :employee_id'

# A literal percent sign next to a bound marker
_select_j_names_in_department = \
    f"select {_columns} from {Table_Name} where first_name like 'J%' and department = :department order by employee_id"

# The statements the write tests run
_insert_employee = f"""
    insert into {Table_Name} ({_columns})
    values (:employee_id, :first_name, :last_name, :department, :salary)
"""
_update_salary   = f'update {Table_Name} set salary = :salary where employee_id = :employee_id'
_delete_employee = f'delete from {Table_Name} where employee_id = :employee_id'

# The row the write tests add - its id is above every seed row's so the procedures never see it
_new_employee:'stranydict' = {
    'employee_id': 101,
    'first_name': 'Robert',
    'last_name': 'Williams',
    'department': Department_Sales,
    'salary': 87000,
}

_new_salary = 91000

# An id no row has
_unknown_employee_id = 999

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

def _query(client:'_AdminClient', service_name:'str', query:'str', params:'strdictnone') -> 'any_':
    """ Runs a query through one of the query services - execute, one or one_or_none.
    """
    out = client.invoke(service_name, {
        'conn_name': _connection_name,
        'query': query,
        'params': params,
    })

    return out

# ################################################################################################################################

def _write(client:'_AdminClient', statement:'str', params:'stranydict') -> 'anydict':
    """ Runs a write statement through the write service and reads the row it concerns back through the same connection.
    """
    out = client.invoke('test.mssql.db.write', {
        'conn_name': _connection_name,
        'statement': statement,
        'params': params,
        'query': _select_by_id,
        'query_params': {'employee_id': params['employee_id']},
    })

    return out

# ################################################################################################################################

def _read_directly(mssql_server:'DatabaseServer', employee_id:'int') -> 'anylist':
    """ Reads a row through a brand-new pytds connection of the test's own, outside of any pool,
    which is what shows a write was committed.
    """
    details = mssql_server.details
    port = int(details['port'])

    connection = connect_mssql(port, details['password'], details['name'], False)

    out:'anylist' = []

    with connection.cursor() as cursor:
        cursor.execute(f'select {_columns} from {Table_Name} where employee_id = %s', (employee_id,))

        # Rows arrive as tuples here, so they are keyed by column name the way the pool returns them
        column_names:'strlist' = []

        for column in cursor.description:
            column_names.append(column[0])

        for row in cursor.fetchall():
            out.append(dict(zip(column_names, row)))

    connection.close()

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

    def test_conn_callproc_returns_the_same_result_sets(self, zato_server:'anydict') -> 'None':
        """ Calling a procedure straight through the connection gives the same result sets as calling it through a session.
        """
        client = _get_client(zato_server)

        through_conn = _callproc(client, 'test.mssql.db.conn-callproc', Proc_Get_Department_Summary, [])
        through_session = _callproc(client, 'test.mssql.db.callproc', Proc_Get_Department_Summary, [])

        assert len(through_conn) == 2
        assert through_conn == through_session

        head_counts, employees = through_conn

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
        """ A procedure invoked as an exec statement through conn.execute returns its rows as dicts.
        """
        client = _get_client(zato_server)
        employees = _query(client, 'test.mssql.db.query', _exec_statement, None)

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

class TestMSSQLQueries:

    def test_select_without_parameters(self, zato_server:'anydict') -> 'None':
        """ A query without parameters returns all the rows as dicts.
        """
        client = _get_client(zato_server)
        employees = _query(client, 'test.mssql.db.query', _select_all, None)

        assert employees == get_all_employees()

# ################################################################################################################################

    def test_select_with_bound_parameter(self, zato_server:'anydict') -> 'None':
        """ A :name marker is bound to its parameter and filters the rows.
        """
        client = _get_client(zato_server)
        employees = _query(client, 'test.mssql.db.query', _select_by_department, {'department': Department_Sales})

        assert employees == get_employees_by_department(Department_Sales)
        assert len(employees) == 2

# ################################################################################################################################

    def test_literal_percent_next_to_a_marker(self, zato_server:'anydict') -> 'None':
        """ A literal percent sign in the query text survives next to a bound marker.
        """
        client = _get_client(zato_server)
        employees = _query(client, 'test.mssql.db.query', _select_j_names_in_department, {'department': Department_Engineering})

        assert len(employees) == 1

        employee = employees[0]
        assert employee['first_name'] == 'John'
        assert employee['department'] == Department_Engineering

# ################################################################################################################################

    def test_one_returns_the_row(self, zato_server:'anydict') -> 'None':
        """ conn.one returns the single matching row directly.
        """
        client = _get_client(zato_server)
        employee = _query(client, 'test.mssql.db.one', _select_by_id, {'employee_id': 1})

        expected = get_all_employees()[0]
        assert employee == expected

# ################################################################################################################################

    def test_one_refuses_multiple_rows(self, zato_server:'anydict') -> 'None':
        """ conn.one raises when the query matches more than one row.
        """
        client = _get_client(zato_server)

        with pytest.raises(Exception) as error:
            _ = _query(client, 'test.mssql.db.one', _select_by_department, {'department': Department_Sales})

        assert 'multiple rows' in str(error.value)

# ################################################################################################################################

    def test_one_or_none_returns_none(self, zato_server:'anydict') -> 'None':
        """ conn.one_or_none returns None when no row matches.
        """
        client = _get_client(zato_server)
        employee = _query(client, 'test.mssql.db.one-or-none', _select_by_id, {'employee_id': _unknown_employee_id})

        assert employee is None

# ################################################################################################################################

    def test_marker_without_parameter_is_refused(self, zato_server:'anydict') -> 'None':
        """ A :name marker with no matching parameter is refused before anything reaches the database.
        """
        client = _get_client(zato_server)

        with pytest.raises(Exception) as error:
            _ = _query(client, 'test.mssql.db.query', _select_by_department, {'employee_id': 1})

        error_text = str(error.value)
        assert 'department' in error_text
        assert 'no matching parameters' in error_text

# ################################################################################################################################
# ################################################################################################################################

class TestMSSQLWrites:

    def test_insert_update_delete(self, zato_server:'anydict', mssql_server:'DatabaseServer') -> 'None':
        """ Writes through conn.execute are committed - each one is visible through a brand-new
        connection of the test's own, and each returns an empty list.
        """
        client = _get_client(zato_server)
        employee_id = _new_employee['employee_id']

        # Insert the row ..
        result = _write(client, _insert_employee, _new_employee)

        assert result['written'] == []
        assert result['rows'] == [_new_employee]

        rows = _read_directly(mssql_server, employee_id)
        assert rows == [_new_employee]

        # .. change its salary ..
        updated_employee = dict(_new_employee)
        updated_employee['salary'] = _new_salary

        result = _write(client, _update_salary, {'employee_id': employee_id, 'salary': _new_salary})

        assert result['written'] == []
        assert result['rows'] == [updated_employee]

        rows = _read_directly(mssql_server, employee_id)
        assert rows == [updated_employee]

        # .. and remove it again.
        result = _write(client, _delete_employee, {'employee_id': employee_id})

        assert result['written'] == []
        assert result['rows'] == []

        rows = _read_directly(mssql_server, employee_id)
        assert rows == []

        employee = _query(client, 'test.mssql.db.one-or-none', _select_by_id, {'employee_id': employee_id})
        assert employee is None

# ################################################################################################################################
# ################################################################################################################################
