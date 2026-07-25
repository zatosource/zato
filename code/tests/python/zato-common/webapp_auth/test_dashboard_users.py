# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The credential check that all the standalone applications share: they accept the people
# who can sign in to the Dashboard, reading Django's own auth_user table directly, so the
# hash format and the active flag are all that stand between a caller and an admin session.

# stdlib
import os
from base64 import b64encode
from hashlib import pbkdf2_hmac

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.webapp.auth.dashboard_users import is_dashboard_admin, verify_django_password

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_admin_username = 'dashboard.admin'
_admin_password = 'Correct.Horse.Battery.Staple'
_disabled_username = 'former.admin'
_unknown_username = 'never.existed'

# How many rounds the test hashes are built with - the count travels inside the hash itself,
# so a low one keeps the suite quick without changing what is being tested.
_test_iterations = 1000

# The one algorithm the Dashboard stores its passwords with
_hash_algorithm = 'pbkdf2_sha256'

# How many characters the salt of a test hash has, which is what generate_hex_string returns by default
_salt_length = 16

# The table the Dashboard keeps its users in, with only the columns the check reads
_auth_user_ddl = """
create table auth_user (
    id integer primary key,
    username varchar(150) not null unique,
    password varchar(128) not null,
    is_active bool not null
)
"""

_insert_user = 'insert into auth_user (username, password, is_active) values (:username, :password, :is_active)'

# ################################################################################################################################
# ################################################################################################################################

def _django_hash(password:'str', algorithm:'str'=_hash_algorithm) -> 'str':
    """ Builds one password hash in Django's storage format - algorithm$iterations$salt$hash.
    """
    salt = CryptoManager.generate_hex_string()

    derived = pbkdf2_hmac('sha256', password.encode('utf8'), salt.encode('utf8'), _test_iterations)
    encoded = b64encode(derived).decode('utf8')

    out = f'{algorithm}${_test_iterations}${salt}${encoded}'
    return out

# ################################################################################################################################

@pytest.fixture
def engine(tmp_path:'any_') -> 'Engine':
    """ An engine over a database holding the Dashboard's users - one able to sign in, one disabled.

    The database is a file rather than an in-memory one because the check may open a connection
    of its own, which for SQLite in memory would be a different, empty database.
    """
    database_path = os.path.join(tmp_path, 'dashboard.db')
    out = create_engine(f'sqlite:///{database_path}')

    admin_hash = _django_hash(_admin_password)
    disabled_hash = _django_hash(_admin_password)

    with out.begin() as connection:
        _ = connection.execute(text(_auth_user_ddl))
        _ = connection.execute(text(_insert_user), {'username':_admin_username, 'password':admin_hash, 'is_active':True})
        _ = connection.execute(text(_insert_user), {'username':_disabled_username, 'password':disabled_hash, 'is_active':False})

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_engine_accepts_the_right_password(engine:'Engine') -> 'None':

    is_admin = is_dashboard_admin(engine, _admin_username, _admin_password)
    assert is_admin is True

# ################################################################################################################################

def test_engine_rejects_a_wrong_password(engine:'Engine') -> 'None':

    is_admin = is_dashboard_admin(engine, _admin_username, 'Almost.The.Right.One')
    assert is_admin is False

# ################################################################################################################################

def test_a_user_that_does_not_exist_is_rejected(engine:'Engine') -> 'None':

    is_admin = is_dashboard_admin(engine, _unknown_username, _admin_password)
    assert is_admin is False

# ################################################################################################################################

def test_a_disabled_user_is_rejected_even_with_the_right_password(engine:'Engine') -> 'None':

    is_admin = is_dashboard_admin(engine, _disabled_username, _admin_password)
    assert is_admin is False

# ################################################################################################################################

def test_a_session_accepts_the_right_password(engine:'Engine') -> 'None':
    """ The server calls this with an ODB session rather than with an engine of its own.
    """
    session_class = sessionmaker(bind=engine)
    session = session_class()

    try:
        is_admin = is_dashboard_admin(session, _admin_username, _admin_password)
        assert is_admin is True

        is_admin = is_dashboard_admin(session, _admin_username, 'Almost.The.Right.One')
        assert is_admin is False

    finally:
        session.close()

# ################################################################################################################################

def test_a_hash_in_another_algorithm_is_rejected() -> 'None':
    """ Only pbkdf2 hashes are read, so a password stored under any other scheme never signs in.
    """
    encoded = _django_hash(_admin_password, algorithm='argon2')

    is_valid = verify_django_password(_admin_password, encoded)
    assert is_valid is False

# ################################################################################################################################

def test_the_pbkdf2_hash_the_dashboard_writes_is_read_back() -> 'None':
    """ The format itself - algorithm, iteration count, salt and hash, in that order.
    """
    encoded = _django_hash(_admin_password)

    algorithm, iterations, salt, stored_hash = encoded.split('$', 3)
    salt_length = len(salt)

    assert algorithm == _hash_algorithm
    assert iterations == str(_test_iterations)
    assert salt_length == _salt_length
    assert stored_hash

    is_valid = verify_django_password(_admin_password, encoded)
    assert is_valid is True

# ################################################################################################################################
# ################################################################################################################################
