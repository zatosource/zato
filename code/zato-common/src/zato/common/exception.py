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
from zato.common.http_ import HTTP_RESPONSES

# ################################################################################################################################
# ################################################################################################################################

# https://tools.ietf.org/html/rfc6585
TOO_MANY_REQUESTS = 429

# ################################################################################################################################
# ################################################################################################################################

class ZatoException(Exception):
    """ Base class for all Zato custom exceptions.
    """
    def __init__(self, cid=None, msg=None):
        super(ZatoException, self).__init__(msg)
        self.cid = cid
        self.msg = msg

    def __repr__(self):
        return '<{} at {} cid:`{}`, msg:`{}`>'.format(
            self.__class__.__name__, hex(id(self)), self.cid, self.msg)

    __str__ = __repr__

# ################################################################################################################################

class ClientSecurityException(ZatoException):
    """ An exception for signalling errors stemming from security problems
    on the client side, such as invalid username or password.
    """

# ################################################################################################################################

class ConnectionException(ZatoException):
    """ Encountered a problem with an external connections, such as to AMQP brokers.
    """

# ################################################################################################################################

class TimeoutException(ConnectionException):
    pass

# ################################################################################################################################

class StatusAwareException(ZatoException):
    """ Raised when the underlying error condition can be easily expressed
    as one of the HTTP status codes.
    """
    def __init__(self, cid, msg, status):
        super(StatusAwareException, self).__init__(cid, msg)
        self.status = status
        self.reason = HTTP_RESPONSES[status]

    def __repr__(self):
        return '<{} at {} cid:`{}`, status:`{}`, msg:`{}`>'.format(
            self.__class__.__name__, hex(id(self)), self.cid, self.status, self.msg)

# ################################################################################################################################

class HTTPException(StatusAwareException):
    pass

# ################################################################################################################################

class ParsingException(ZatoException):
    """ Raised when the error is to do with parsing of documents, such as an input
    XML document.
    """

# ################################################################################################################################

class NoDistributionFound(ZatoException):
    """ Raised when an attempt is made to import services from a Distutils2 archive
    or directory but they don't contain a proper Distutils2 distribution.
    """
    def __init__(self, path):
        super(NoDistributionFound, self).__init__(None, 'No Disutils distribution in path:[{}]'.format(path))

# ################################################################################################################################

class Inactive(ZatoException):
    """ Raised when an attempt was made to use an inactive resource, such
    as an outgoing connection or a channel.
    """
    def __init__(self, name):
        super(Inactive, self).__init__(None, '`{}` is inactive'.format(name))

# ################################################################################################################################
# ################################################################################################################################

# Below are HTTP exceptions

class Reportable(HTTPException):
    def __init__(self, cid, msg, status):
        super(ClientHTTPError, self).__init__(cid, msg, status)

# Backward compatibility with pre 3.0
ClientHTTPError = Reportable

# ################################################################################################################################

class BadRequest(Reportable):
    def __init__(self, cid, msg='Received a bad request'):
        super(BadRequest, self).__init__(cid, msg, BAD_REQUEST)

# ################################################################################################################################

class Conflict(Reportable):
    def __init__(self, cid, msg):
        super(Conflict, self).__init__(cid, msg, CONFLICT)

# ################################################################################################################################

class Forbidden(Reportable):
    def __init__(self, cid, msg='You are not allowed to access this resource', *ignored_args, **ignored_kwargs):
        super(Forbidden, self).__init__(cid, msg, FORBIDDEN)

# ################################################################################################################################

class MethodNotAllowed(Reportable):
    def __init__(self, cid, msg):
        super(MethodNotAllowed, self).__init__(cid, msg, METHOD_NOT_ALLOWED)

# ################################################################################################################################

class NotFound(Reportable):
    def __init__(self, cid, msg):
        super(NotFound, self).__init__(cid, msg, NOT_FOUND)

# ################################################################################################################################

class Unauthorized(Reportable):
    def __init__(self, cid, msg, challenge):
        super(Unauthorized, self).__init__(cid, msg, UNAUTHORIZED)
        self.challenge = challenge

# ################################################################################################################################

class TooManyRequests(Reportable):
    def __init__(self, cid, msg):
        super(TooManyRequests, self).__init__(cid, msg, TOO_MANY_REQUESTS)

# ################################################################################################################################

class InternalServerError(Reportable):
    def __init__(self, cid, msg='Internal server error'):
        super(InternalServerError, self).__init__(cid, msg, INTERNAL_SERVER_ERROR)

# ################################################################################################################################

class ServiceUnavailable(Reportable):
    def __init__(self, cid, msg):
        super(ServiceUnavailable, self).__init__(cid, msg, SERVICE_UNAVAILABLE)

# ################################################################################################################################

class PubSubSubscriptionExists(BadRequest):
    pass

# ################################################################################################################################

class ConnectorClosedException(Exception):
    def __init__(self, exc, message):
        self.inner_exc = exc
        super().__init__(message)

# ################################################################################################################################

class IBMMQException(Exception):
    pass

# ################################################################################################################################
