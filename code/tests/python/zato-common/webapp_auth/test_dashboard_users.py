# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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

    # Add dummy assignments to satisfy type checkers
    Engine = Engine
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_admin_username    = 'dashboard.admin'
_admin_password    = 'Dashboard.Admin.Password.1'
_disabled_username = 'former.admin'
_unknown_username  = 'never.existed'
_external_username = 'external.user@example.com'

# A stored value that is not in the pbkdf2 format.
_unusable_password_marker = '!' + CryptoManager.generate_hex_string(32)

# The iteration count the test hashes carry.
_test_iterations = 1000

# The one algorithm the Dashboard stores its passwords with.
_hash_algorithm = 'pbkdf2_sha256'

# How many characters the salt of a test hash has.
_salt_length = 16

# The table the Dashboard keeps its users in, with only the columns the check reads.
_auth_user_create_table = """
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

    # Build the salt ..
    salt = CryptoManager.generate_hex_string()

    # .. derive the key ..
    derived = pbkdf2_hmac('sha256', password.encode('utf8'), salt.encode('utf8'), _test_iterations)
    encoded = b64encode(derived).decode('utf8')

    # .. and assemble the stored format.
    out = f'{algorithm}${_test_iterations}${salt}${encoded}'
    return out

# ################################################################################################################################

@pytest.fixture
def engine(tmp_path:'any_') -> 'Engine':
    """ An engine over a database holding the Dashboard's users - one able to sign in, one disabled.
    """

    # The database is a file because the check opens a connection of its own.
    database_path = os.path.join(tmp_path, 'dashboard.db')

    # Build the hashes the rows carry ..
    admin_hash    = _django_hash(_admin_password)
    disabled_hash = _django_hash(_admin_password)

    # .. the rows themselves ..
    insert_statement = text(_insert_user)

    admin_row    = {'username':_admin_username, 'password':admin_hash, 'is_active':True}
    disabled_row = {'username':_disabled_username, 'password':disabled_hash, 'is_active':False}
    external_row = {'username':_external_username, 'password':_unusable_password_marker, 'is_active':True}

    # .. and seed the database with them.
    engine = create_engine(f'sqlite:///{database_path}')

    with engine.begin() as connection:
        _ = connection.execute(text(_auth_user_create_table))
        _ = connection.execute(insert_statement, admin_row)
        _ = connection.execute(insert_statement, disabled_row)
        _ = connection.execute(insert_statement, external_row)

    out = engine
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

def test_an_account_without_a_local_password_is_rejected(engine:'Engine') -> 'None':
    """ A stored value that is not a pbkdf2 hash never signs in.
    """
    is_admin = is_dashboard_admin(engine, _external_username, _admin_password)
    assert is_admin is False

# ################################################################################################################################

def test_a_stored_value_without_the_expected_format_means_no_local_password() -> 'None':

    is_valid = verify_django_password(_admin_password, _unusable_password_marker)
    assert is_valid is False

# ################################################################################################################################

def test_a_hash_in_another_algorithm_is_rejected() -> 'None':
    """ Only pbkdf2 hashes are read.
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
