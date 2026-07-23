# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from hashlib import pbkdf2_hmac
from hmac import compare_digest

# SQLAlchemy
from sqlalchemy import text
from sqlalchemy.engine import Engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The only password hash algorithm the Dashboard's Django users are stored with
_django_hash_algorithm = 'pbkdf2_sha256'

# The Dashboard keeps its users in the same database the server uses, in Django's own table
_dashboard_user_query = 'select password from auth_user where username = :username and is_active = :is_active'

# ################################################################################################################################
# ################################################################################################################################

def verify_django_password(password:'str', encoded:'str') -> 'bool':
    """ Checks a password against a hash in Django's storage format - algorithm$iterations$salt$hash.
    """
    algorithm, iterations, salt, stored_hash = encoded.split('$', 3)

    # Only the one algorithm the Dashboard uses is supported
    if algorithm != _django_hash_algorithm:
        return False

    # Derive the hash from the incoming password the same way Django does ..
    derived = pbkdf2_hmac('sha256', password.encode('utf8'), salt.encode('utf8'), int(iterations))

    # .. and compare in constant time.
    out = compare_digest(derived, b64decode(stored_hash))

    return out

# ################################################################################################################################

def is_dashboard_admin(session_or_engine:'any_', username:'str', password:'str') -> 'bool':
    """ Checks the credentials against the Dashboard's own users - anyone who can sign in
    to the Dashboard is an admin of the applications that share its credentials.
    Accepts either an SQLAlchemy session or an engine, so both the server's ODB sessions
    and the standalone dashboards' plain engines can call this one implementation.
    """
    params = {'username':username, 'is_active':True}

    # An engine opens its own short-lived connection, a session executes directly ..
    if isinstance(session_or_engine, Engine):
        with session_or_engine.connect() as connection:
            row = connection.execute(text(_dashboard_user_query), params).fetchone()
    else:
        row = session_or_engine.execute(text(_dashboard_user_query), params).fetchone()

    # .. no such Dashboard user ..
    if row is None:
        return False

    # .. and the password decides.
    out = verify_django_password(password, row[0])

    return out

# ################################################################################################################################
# ################################################################################################################################
