# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.odb.api import SQLConnectionPool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Real-account tests only run when the environment provides the credentials -
# regular test runs never enter them.
_snowflake_account = os.environ.get('Zato_Test_Snowflake_Account', '')
_redshift_host = os.environ.get('Zato_Test_Redshift_Host', '')

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.skipif(not _snowflake_account, reason='Zato_Test_Snowflake_Account is not set')
class TestSnowflakeRealAccount:

    def _get_pool(self) -> 'SQLConnectionPool':

        extra_parts = []

        if warehouse := os.environ.get('Zato_Test_Snowflake_Warehouse'):
            extra_parts.append(f'warehouse={warehouse}')

        if role := os.environ.get('Zato_Test_Snowflake_Role'):
            extra_parts.append(f'role={role}')

        if schema := os.environ.get('Zato_Test_Snowflake_Schema'):
            extra_parts.append(f'schema={schema}')

        config:'strdict' = {
            'engine': 'snowflake',
            'username': os.environ['Zato_Test_Snowflake_User'],
            'password': os.environ['Zato_Test_Snowflake_Password'],
            'host': _snowflake_account,
            'port': '',
            'db_name': os.environ['Zato_Test_Snowflake_Database'],
            'pool_size': 1,
            'extra': ';'.join(extra_parts),
        }

        out = SQLConnectionPool('test.snowflake.real', config, config)
        return out

# ################################################################################################################################

    def test_ping(self) -> 'None':
        """ The real Snowflake account answers a ping.
        """
        pool = self._get_pool()

        response_time = pool.ping({'snowflake': {'ping_query': 'SELECT 1'}})
        assert response_time > 0

        pool.engine.dispose()

# ################################################################################################################################

    def test_select(self) -> 'None':
        """ The real Snowflake account answers a query.
        """
        pool = self._get_pool()

        with pool.engine.connect() as connection:
            result = connection.execute(text('select current_version()'))
            version = result.scalar()

        assert version

        pool.engine.dispose()

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.skipif(not _redshift_host, reason='Zato_Test_Redshift_Host is not set')
class TestRedshiftRealAccount:

    def _get_pool(self) -> 'SQLConnectionPool':

        port = os.environ.get('Zato_Test_Redshift_Port')
        if not port:
            port = '5439'

        config:'strdict' = {
            'engine': 'redshift+redshift_connector',
            'username': os.environ['Zato_Test_Redshift_User'],
            'password': os.environ['Zato_Test_Redshift_Password'],
            'host': _redshift_host,
            'port': port,
            'db_name': os.environ['Zato_Test_Redshift_Database'],
            'pool_size': 1,
            'extra': 'ssl=True;sslmode=verify-ca',
        }

        out = SQLConnectionPool('test.redshift.real', config, config)
        return out

# ################################################################################################################################

    def test_ping(self) -> 'None':
        """ The real Redshift cluster answers a ping.
        """
        pool = self._get_pool()

        response_time = pool.ping({'redshift+redshift_connector': {'ping_query': 'SELECT 1'}})
        assert response_time > 0

        pool.engine.dispose()

# ################################################################################################################################

    def test_select(self) -> 'None':
        """ The real Redshift cluster answers a query.
        """
        pool = self._get_pool()

        with pool.engine.connect() as connection:
            result = connection.execute(text('select version()'))
            version = result.scalar()

        assert version

        pool.engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
