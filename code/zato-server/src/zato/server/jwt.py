# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import uuid
from contextlib import closing
from datetime import datetime
from logging import getLogger

# Bunch
from bunch import bunchify, Bunch

# Cryptography
from cryptography.fernet import Fernet

# JWT
import jwt

# Zato
from zato.common.odb.model import JWT as JWT_
from zato.server.cache import RobustCache

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class JWT(object):
    """ JWT authentication backend.
    """
    ALGORITHM = 'HS256'

# ################################################################################################################################

    def __init__(self, kvdb, odb, secret):
        self.odb = odb
        self.cache = RobustCache(kvdb, odb)

        self.secret = secret
        self.fernet = Fernet(self.secret)

# ################################################################################################################################

    def _lookup_jwt(self, username, password):
        with closing(self.odb.session()) as session:
            return session.query(JWT_).filter_by(username=username, password=password).first()

# ################################################################################################################################

    def _create_token(self, **data):
        token_data = {
            'session_id': uuid.uuid4().hex,
            'creation_time': datetime.utcnow().isoformat()
        }
        token_data.update(data)

        token = jwt.encode(token_data, self.secret, algorithm=self.ALGORITHM)
        return self.fernet.encrypt(token.encode('utf-8'))

# ################################################################################################################################

    def authenticate(self, username, password):
        """ Validate cretentials and generate a new token if valid.

        1. Validate cretentials against ODB
        2.a: If not valid, return nothing
        2.b: If valid:
            3. Create a new token
            4. Cache the new token synchronously (we wait for it to be truly stored).
            5. Return the token
        """
        sec_def = self._lookup_jwt(username, password)
        if sec_def:
            token = self._create_token(username=username, ttl=sec_def.ttl)
            self.cache.put(token, token, sec_def.ttl, async=False)
            suffix = 's' if sec_def.ttl > 1 else ''
            logger.info('New token generated for user `%s` with a TTL of `%i` second{}'.format(suffix), username, sec_def.ttl)

            return token

# ################################################################################################################################

    def validate(self, expected_username, token):
        """ Check if the given token is (still) valid.

        1. Look for the token in Cache without decrypting/decoding it.
        2.a If not found, return "Invalid"
        2.b If found:
            3. decrypt
            4. decode
            5. renew the cache expiration asyncronouysly (do not wait for the update confirmation).
            5. return "valid" + the token contents
        """
        if self.cache.get(token):
            decrypted = self.fernet.decrypt(token)
            token_data = bunchify(jwt.decode(decrypted, self.secret))

            if token_data.username == expected_username:

                # Renew the token expiration
                self.cache.put(token, token, token_data.ttl, async=True)
                return Bunch(valid=True, token=token_data)

            else:
                return Bunch(valid=False, message='Unexpected user for token found')

        else:
            return Bunch(valid=False, message='Invalid token')

# ################################################################################################################################

    def delete(self, token):
        """ Deletes a token in both KVDB and ODB.
        """
        self.cache.delete(token)

# ################################################################################################################################
