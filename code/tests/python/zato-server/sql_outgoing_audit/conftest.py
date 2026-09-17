# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The scenario helpers live next to the tests and are imported flat, and the container
# helpers are shared with the zato-common suites.
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from live_sql.containers import start_mssql, start_mysql, start_oracle, start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.containers import DatabaseServer

    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Host ports the containers listen on - distinct from the other suites'
    # so they can all run alongside each other.
    MSSQL_Port      = 21435
    MySQL_Port      = 23346
    Oracle_Port     = 21522
    PostgreSQL_Port = 25464

    # Names of the containers so stale ones can be removed
    MSSQL_Container      = 'zato-sql-audit-test-mssql'
    MySQL_Container      = 'zato-sql-audit-test-mysql'
    Oracle_Container     = 'zato-sql-audit-test-oracle'
    PostgreSQL_Container = 'zato-sql-audit-test-postgresql'

    # Database credentials shared by the MySQL and PostgreSQL containers
    Username = 'zato_sql_audit'
    Password = 'test-sql-audit-password'
    DB_Name  = 'zato_sql_audit'

    # MS SQL has a password complexity policy of its own to satisfy
    MSSQL_Password = 'Test-sql-audit-password-1'

    # The Oracle application user's password, in the shape the Oracle suite uses too
    Oracle_Password = 'test.sql.audit.password'

    # Oracle DB connection pools are enabled by the license key variable -
    # this is the value the suite supplies when the variable is not already set.
    License_Key_Name  = 'Zato_License_Key'
    License_Key_Value = 'test.license.key'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mysql_server() -> 'servergen':
    """ A MySQL server started on demand in a container.
    """
    server = start_mysql(
        container_name=ModuleCtx.MySQL_Container,
        port=ModuleCtx.MySQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def postgresql_server() -> 'servergen':
    """ A PostgreSQL server started on demand in a container.
    """
    server = start_postgresql(
        container_name=ModuleCtx.PostgreSQL_Container,
        port=ModuleCtx.PostgreSQL_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Password,
        db_name=ModuleCtx.DB_Name,
        needs_ssl=False,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def mssql_server() -> 'servergen':
    """ An MS SQL server started on demand in a container.
    """
    server = start_mssql(
        container_name=ModuleCtx.MSSQL_Container,
        port=ModuleCtx.MSSQL_Port,
        password=ModuleCtx.MSSQL_Password,
        db_name=ModuleCtx.DB_Name,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def oracle_server() -> 'servergen':
    """ An Oracle Database server started on demand in a container. The pool store builds
    Oracle connections only with the license key variable present, so it is set here.
    """
    if not os.environ.get(ModuleCtx.License_Key_Name):
        os.environ[ModuleCtx.License_Key_Name] = ModuleCtx.License_Key_Value

    server = start_oracle(
        container_name=ModuleCtx.Oracle_Container,
        port=ModuleCtx.Oracle_Port,
        username=ModuleCtx.Username,
        password=ModuleCtx.Oracle_Password,
    )
    yield server

    stop_container(server.container_name)

# ################################################################################################################################
# ################################################################################################################################
