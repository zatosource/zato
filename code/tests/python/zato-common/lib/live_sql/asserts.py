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
    with engine.connect() as connection:
        row = connection.execute(text("show session status like 'Ssl_cipher'")).fetchone()

    cipher = row[1]
    assert cipher, 'Expected a non-empty SSL cipher for the MySQL session'

# ################################################################################################################################

def assert_postgresql_connection_encrypted(engine:'Engine') -> 'None':
    """ Confirms that sessions of this PostgreSQL engine really are encrypted.
    """
    with engine.connect() as connection:
        is_ssl = connection.execute(text('select ssl from pg_stat_ssl where pid = pg_backend_pid()')).scalar()

    assert is_ssl is True, 'Expected the PostgreSQL session to use SSL'

# ################################################################################################################################
# ################################################################################################################################
