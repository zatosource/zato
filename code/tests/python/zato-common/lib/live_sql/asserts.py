# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

def assert_mysql_connection_encrypted(engine:'Engine') -> 'None':
    """ Confirms that sessions of this MySQL engine really are encrypted.
    """
    status_query = text("show session status like 'Ssl_cipher'")

    with engine.connect() as connection:
        result = connection.execute(status_query)
        row = result.fetchone()

    assert row is not None, 'Expected a row from the MySQL SSL status query'
    cipher = row[1]
    assert cipher, 'Expected a non-empty SSL cipher for the MySQL session'

# ################################################################################################################################

def assert_postgresql_connection_encrypted(engine:'Engine') -> 'None':
    """ Confirms that sessions of this PostgreSQL engine really are encrypted.
    """
    ssl_query = text('select ssl from pg_stat_ssl where pid = pg_backend_pid()')

    with engine.connect() as connection:
        result = connection.execute(ssl_query)
        is_ssl = result.scalar()

    assert is_ssl is True, 'Expected the PostgreSQL session to use SSL'

# ################################################################################################################################
# ################################################################################################################################
