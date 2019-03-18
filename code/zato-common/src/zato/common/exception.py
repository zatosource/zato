# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import BAD_REQUEST, CONFLICT, FORBIDDEN, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_FOUND, \
     SERVICE_UNAVAILABLE, UNAUTHORIZED

# Zato
from zato.common import TOO_MANY_REQUESTS, HTTPException

class Reportable(HTTPException):
    def __init__(self, cid, msg, status):
        super(ClientHTTPError, self).__init__(cid, msg, status)

# Backward compatibility with pre 3.0
ClientHTTPError = Reportable

class BadRequest(Reportable):
    def __init__(self, cid, msg='Received a bad request'):
        super(BadRequest, self).__init__(cid, msg, BAD_REQUEST)

class Conflict(Reportable):
    def __init__(self, cid, msg):
        super(Conflict, self).__init__(cid, msg, CONFLICT)

class Forbidden(Reportable):
    def __init__(self, cid, msg='You are not allowed to access this resource', *ignored_args, **ignored_kwargs):
        super(Forbidden, self).__init__(cid, msg, FORBIDDEN)

class MethodNotAllowed(Reportable):
    def __init__(self, cid, msg):
        super(MethodNotAllowed, self).__init__(cid, msg, METHOD_NOT_ALLOWED)

class NotFound(Reportable):
    def __init__(self, cid, msg):
        super(NotFound, self).__init__(cid, msg, NOT_FOUND)

class Unauthorized(Reportable):
    def __init__(self, cid, msg, challenge):
        super(Unauthorized, self).__init__(cid, msg, UNAUTHORIZED)
        self.challenge = challenge

class TooManyRequests(Reportable):
    def __init__(self, cid, msg):
        super(TooManyRequests, self).__init__(cid, msg, TOO_MANY_REQUESTS)

class InternalServerError(Reportable):
    def __init__(self, cid, msg='Internal server error'):
        super(InternalServerError, self).__init__(cid, msg, INTERNAL_SERVER_ERROR)

class ServiceUnavailable(Reportable):
    def __init__(self, cid, msg):
        super(ServiceUnavailable, self).__init__(cid, msg, SERVICE_UNAVAILABLE)

class PubSubSubscriptionExists(BadRequest):
    pass
