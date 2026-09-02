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
    from sqlalchemy.orm.session import Session as SASession

    # Add dummy assignments to satisfy type checkers
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

# The only password hash algorithm the Dashboard's Django users are stored with.
_django_hash_algorithm = 'pbkdf2_sha256'

# The digest the algorithm above derives its hashes with.
_pbkdf2_digest = 'sha256'

# The Dashboard keeps its users in the same database the server uses, in Django's own table.
_dashboard_user_query = 'select password from auth_user where username = :username and is_active = :is_active'

# ################################################################################################################################
# ################################################################################################################################

def verify_django_password(password:'str', encoded:'str') -> 'bool':
    """ Checks a password against a hash in Django's storage format - algorithm$iterations$salt$hash.
    """

    # Our response to produce
    out = False

    # A stored value without the expected format means the account has no local password
    if '$' in encoded:

        algorithm, iterations, salt, stored_hash = encoded.split('$', 3)

        # Only the one algorithm the Dashboard uses is supported.
        if algorithm == _django_hash_algorithm:

            # Derive the hash from the incoming password the same way Django does ..
            password_bytes = password.encode('utf8')
            salt_bytes = salt.encode('utf8')
            iteration_count = int(iterations)

            derived_hash = pbkdf2_hmac(_pbkdf2_digest, password_bytes, salt_bytes, iteration_count)

            # .. and compare in constant time.
            stored_hash_bytes = b64decode(stored_hash)
            out = compare_digest(derived_hash, stored_hash_bytes)

    return out

# ################################################################################################################################

def is_dashboard_admin(session_or_engine:'SASession | Engine', username:'str', password:'str') -> 'bool':
    """ Checks the credentials against the Dashboard's own users.
    """

    # Our response to produce
    out = False

    query = text(_dashboard_user_query)
    query_parameters = {'username':username, 'is_active':True}

    # An engine opens its own short-lived connection, a session executes directly ..
    if isinstance(session_or_engine, Engine):
        with session_or_engine.connect() as connection:
            result = connection.execute(query, query_parameters)
            row = result.fetchone()
    else:
        result = session_or_engine.execute(query, query_parameters)
        row = result.fetchone()

    # .. and if the user exists at all, the password decides.
    if row is not None:
        stored_password = row[0]
        out = verify_django_password(password, stored_password)

    return out

# ################################################################################################################################
# ################################################################################################################################
