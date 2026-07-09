# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.odb.api import SQLConnectionPool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The component-wide SQL configuration the ping call reads its query from.
_fs_sql_config = {
    'redshift+redshift_connector': {
        'ping_query': 'SELECT 1',
    }
}

# ################################################################################################################################
# ################################################################################################################################

def _get_pool(server:'any_', extra:'str', password:'str'='') -> 'SQLConnectionPool':
    """ Builds a real SQL connection pool pointing at a test server.
    """
    if not password:
        password = server.password

    config:'strdict' = {
        'engine': 'redshift+redshift_connector',
        'username': server.user,
        'password': password,
        'host': server.host,
        'port': server.port,
        'db_name': 'testdb',
        'pool_size': 1,
        'extra': extra,
    }

    out = SQLConnectionPool('test.redshift', config, config)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRedshiftConnection:

    def test_engine_creation_and_ping(self, redshift_server:'any_') -> 'None':
        """ A pool built for a Redshift connection pings the server through the real dialect and driver,
        with the TLS upgrade verified against the test CA.
        """
        redshift_server.clear_requests()
        pool = _get_pool(redshift_server, 'ssl=True;sslmode=verify-ca')

        assert pool.engine is not None

        response_time = pool.ping(_fs_sql_config)
        assert response_time > 0

        # The startup exchange carried the configured user and the protocol negotiation parameter.
        startup_requests = []
        for request in redshift_server.recorded_requests:
            if request['type'] == 'startup':
                startup_requests.append(request)

        assert len(startup_requests) >= 1

        startup_parameters = startup_requests[0]['parameters']
        assert startup_parameters['user'] == redshift_server.user
        assert 'client_protocol_version' in startup_parameters

        pool.engine.dispose()

# ################################################################################################################################

    def test_select_rows(self, redshift_server:'any_') -> 'None':
        """ Rows come back through the real dialect with their types preserved.
        """
        redshift_server.add_result(
            r'select id, flight_number from flights',
            columns=[('id', 'int'), ('flight_number', 'text')],
            rows=[[1, 'ZA-101'], [2, 'ZA-102']],
        )

        pool = _get_pool(redshift_server, 'ssl=True;sslmode=verify-ca')

        with pool.engine.connect() as connection:
            result = connection.execute(text('select id, flight_number from flights'))
            rows = result.fetchall()

        assert len(rows) == 2

        first_row = rows[0]
        assert first_row[0] == 1
        assert first_row[1] == 'ZA-101'

        second_row = rows[1]
        assert second_row[0] == 2
        assert second_row[1] == 'ZA-102'

        # The SQL travelled through the wire protocol and was recorded at Parse time.
        recorded_sql = []
        for request in redshift_server.recorded_requests:
            if request['type'] == 'parse':
                recorded_sql.append(request['sql'])

        assert 'select id, flight_number from flights' in recorded_sql

        pool.engine.dispose()

# ################################################################################################################################

    def test_wrong_password(self, redshift_server:'any_') -> 'None':
        """ A startup exchange with the wrong password is rejected during MD5 authentication.
        """
        wrong_password = 'password.wrong.for.test'
        pool = _get_pool(redshift_server, 'ssl=True;sslmode=verify-ca', password=wrong_password)

        with pytest.raises(Exception, match='password authentication failed'):
            with pool.engine.connect() as connection:
                _ = connection.execute(text('SELECT 1'))

        pool.engine.dispose()

# ################################################################################################################################

    def test_error_propagation(self, redshift_server:'any_') -> 'None':
        """ A configured ErrorResponse surfaces as a driver-level exception with its SQLSTATE details.
        """
        redshift_server.add_error(
            r'select name from missing_table',
            message='relation "missing_table" does not exist',
            sqlstate='42P01',
        )

        pool = _get_pool(redshift_server, 'ssl=True;sslmode=verify-ca')

        with pytest.raises(DBAPIError, match='missing_table.* does not exist'):
            with pool.engine.connect() as connection:
                _ = connection.execute(text('select name from missing_table'))

        pool.engine.dispose()

# ################################################################################################################################

    def test_tls_untrusted_certificate(self, redshift_server:'any_', redshift_untrusted_server:'any_') -> 'None':
        """ A TLS handshake against a server whose CA the trust path does not know about fails.
        The trusted server fixture is requested too so the trust path is pinned to its CA.
        """
        pool = _get_pool(redshift_untrusted_server, 'ssl=True;sslmode=verify-ca')

        with pytest.raises(Exception, match='certificate'):
            with pool.engine.connect() as connection:
                _ = connection.execute(text('SELECT 1'))

        pool.engine.dispose()

# ################################################################################################################################

    def test_plain_profile(self, redshift_plain_server:'any_') -> 'None':
        """ The plain profile with ssl=False serves pure protocol tests without any TLS in the way.
        """
        pool = _get_pool(redshift_plain_server, 'ssl=False')

        with pool.engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            value = result.scalar()

        assert value == 1

        pool.engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
