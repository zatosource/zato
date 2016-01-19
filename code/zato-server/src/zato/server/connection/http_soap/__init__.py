# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import BAD_REQUEST, CONFLICT, FORBIDDEN, METHOD_NOT_ALLOWED, NOT_FOUND, UNAUTHORIZED

# Zato
from zato.common import TOO_MANY_REQUESTS, HTTPException

class ClientHTTPError(HTTPException):
    def __init__(self, cid, msg, status):
        super(ClientHTTPError, self).__init__(cid, msg, status)

class BadRequest(ClientHTTPError):
    def __init__(self, cid, msg):
        super(BadRequest, self).__init__(cid, msg, BAD_REQUEST)

class Conflict(ClientHTTPError):
    def __init__(self, cid, msg):
        super(Conflict, self).__init__(cid, msg, CONFLICT)

class Forbidden(ClientHTTPError):
    def __init__(self, cid, msg, *ignored_args, **ignored_kwargs):
        super(Forbidden, self).__init__(cid, msg, FORBIDDEN)

class MethodNotAllowed(ClientHTTPError):
    def __init__(self, cid, msg):
        super(MethodNotAllowed, self).__init__(cid, msg, METHOD_NOT_ALLOWED)

class NotFound(ClientHTTPError):
    def __init__(self, cid, msg):
        super(NotFound, self).__init__(cid, msg, NOT_FOUND)

class Unauthorized(ClientHTTPError):
    def __init__(self, cid, msg, challenge):
        super(Unauthorized, self).__init__(cid, msg, UNAUTHORIZED)
        self.challenge = challenge

class TooManyRequests(ClientHTTPError):
    def __init__(self, cid, msg):
        super(TooManyRequests, self).__init__(cid, msg, TOO_MANY_REQUESTS)
