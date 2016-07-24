# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import time
import uuid
from contextlib import closing
from logging import getLogger

import jwt
from anyjson import dumps
from cryptography.fernet import Fernet

# Bunch
from bunch import bunchify, Bunch

# Zato
from zato.common.odb.model import JWT as JWT_
from zato.server.cache import RobustCache


logger = getLogger('zato_singleton')


class JWT(object):
    """JWT authentication."""

    ALGORITHM = 'HS256'

    def __init__(self, kvdb, odb, secret):
        self.odb = odb
        self.cache = RobustCache(kvdb, odb)

        self.secret = secret
        self.fernet = Fernet(secret)

    def _lookup_jwt(self, username, password):
        with closing(self.odb.session()) as session:
            return session.query(JWT_).filter_by(username=username, password=password).first()

    def _create_token(self, **data):
        session_id = str(uuid.uuid4())
        token_data = {
            "session_id": session_id,
            "creation_time": time.time()
        }
        token_data.update(data)

        token = jwt.encode(dumps(token_data), self.secret, algorithm=self.ALGORITHM)
        return self.fernet.encrypt(token.encode('utf-8'))

    def authenticate(self, username, password, ttl):
        """Validate cretentials and generate a new token if valid.

        1. Validate cretentials against ODB
        2.a: If not valid, return nothing
        2.b: If valid:
            3. create a new token
            4. Cache the new token synchronously (we wait for it to be truly stored).
            5. Return the token
        """
        if self._lookup_jwt(username, password):
            token = self._create_token(username=username, ttl=ttl)
            self.cache.put(token, token, ttl, async=False)
            logger.info("New token generated for user %s with %is TTL", username, ttl)

            return token

    def validate(self, token):
        """Check if the given token is (still) valid.

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

            # renew the token expiration
            self.cache.put(token, token, token_data.ttl, async=True)

            return Bunch(valid=True, token=token_data)
        else:
            return Bunch(valid=False, message='Invalid Token')
