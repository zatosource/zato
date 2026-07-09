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
    'snowflake': {
        'ping_query': 'SELECT 1',
    }
}

# Keep connection timeouts short so negative tests fail fast.
_timeouts = 'login_timeout=4;network_timeout=4'

# ################################################################################################################################
# ################################################################################################################################

def _get_pool(server:'any_', extra:'str', password:'str'='') -> 'SQLConnectionPool':
    """ Builds a real SQL connection pool pointing at a test server.
    """
    if not password:
        password = server.password

    config:'strdict' = {
        'engine': 'snowflake',
        'username': server.user,
        'password': password,
        'host': server.account,
        'port': '',
        'db_name': 'testdb',
        'pool_size': 1,
        'extra': extra,
    }

    out = SQLConnectionPool('test.snowflake', config, config)
    return out

# ################################################################################################################################

def _tls_extra(server:'any_') -> 'str':
    """ The extra options that point the connector at an HTTPS test server.
    OCSP checks are off because no OCSP responder exists for a test CA,
    while the certificate chain validation itself stays on.
    """
    out = f'host={server.host};port={server.port};disable_ocsp_checks=True;{_timeouts};' \
        'warehouse=COMPUTE_WH;role=ANALYST;schema=PUBLIC'
    return out

# ################################################################################################################################

def _http_extra(server:'any_') -> 'str':
    """ The extra options that point the connector at a plain-HTTP test server.
    """
    out = f'protocol=http;host={server.host};port={server.port};{_timeouts};warehouse=COMPUTE_WH;schema=PUBLIC'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSnowflakeConnection:

    def test_engine_creation_and_ping(self, snowflake_server:'any_') -> 'None':
        """ A pool built for a Snowflake connection pings the server through the real dialect and driver.
        """
        snowflake_server.clear_requests()
        pool = _get_pool(snowflake_server, _tls_extra(snowflake_server))

        assert pool.engine is not None

        response_time = pool.ping(_fs_sql_config)
        assert response_time > 0

        # The login request carried the configured credentials and account.
        login_requests = []
        for request in snowflake_server.recorded_requests:
            if request['path'] == '/session/v1/login-request':
                login_requests.append(request)

        assert len(login_requests) == 1

        login_data = login_requests[0]['body']['data']
        assert login_data['LOGIN_NAME'].lower() == snowflake_server.user
        assert login_data['ACCOUNT_NAME'].lower() == snowflake_server.account

        pool.engine.dispose()

# ################################################################################################################################

    def test_select_rows(self, snowflake_server:'any_') -> 'None':
        """ Rows come back through the real dialect with their types preserved.
        """
        snowflake_server.add_result(
            r'select id, flight_number from flights',
            columns=[('ID', 'fixed'), ('FLIGHT_NUMBER', 'text')],
            rows=[[1, 'ZA-101'], [2, 'ZA-102']],
        )

        pool = _get_pool(snowflake_server, _tls_extra(snowflake_server))

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

        pool.engine.dispose()

# ################################################################################################################################

    def test_wrong_password(self, snowflake_server:'any_') -> 'None':
        """ A login with the wrong password is rejected by the server.
        """
        wrong_password = 'password.wrong.for.test'
        pool = _get_pool(snowflake_server, _tls_extra(snowflake_server), password=wrong_password)

        with pytest.raises(Exception, match='Incorrect username or password'):
            with pool.engine.connect() as connection:
                _ = connection.execute(text('SELECT 1'))

        pool.engine.dispose()

# ################################################################################################################################

    def test_error_propagation(self, snowflake_server:'any_') -> 'None':
        """ A configured Snowflake error response surfaces as a driver-level exception.
        """
        snowflake_server.add_error(
            r'select name from missing_table',
            message='SQL compilation error: Object MISSING_TABLE does not exist or not authorized.',
            code='002003',
            sqlstate='42S02',
        )

        pool = _get_pool(snowflake_server, _tls_extra(snowflake_server))

        with pytest.raises(DBAPIError, match='MISSING_TABLE does not exist'):
            with pool.engine.connect() as connection:
                _ = connection.execute(text('select name from missing_table'))

        pool.engine.dispose()

# ################################################################################################################################

    def test_tls_untrusted_certificate(self, snowflake_server:'any_', snowflake_untrusted_server:'any_') -> 'None':
        """ A TLS handshake against a server whose CA the trust store does not know about fails.
        The trusted server fixture is requested too so the trust store is pinned to its CA.
        """
        pool = _get_pool(snowflake_untrusted_server, _tls_extra(snowflake_untrusted_server))

        # The handshake fails with a certificate verification error which the connector retries on
        # and then reports as being unable to connect at all.
        with pytest.raises(Exception, match='Could not connect to Snowflake backend'):
            with pool.engine.connect() as connection:
                _ = connection.execute(text('SELECT 1'))

        pool.engine.dispose()

# ################################################################################################################################

    def test_plain_http(self, snowflake_http_server:'any_') -> 'None':
        """ The plain-HTTP profile serves pure protocol tests without any TLS in the way.
        """
        pool = _get_pool(snowflake_http_server, _http_extra(snowflake_http_server))

        with pool.engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            value = result.scalar()

        assert value == 1

        pool.engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
