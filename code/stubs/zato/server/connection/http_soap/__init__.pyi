from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.common import exception

ClientHTTPError = exception.ClientHTTPError
BadRequest = exception.BadRequest
Conflict = exception.Conflict
Forbidden = exception.Forbidden
MethodNotAllowed = exception.MethodNotAllowed
NotFound = exception.NotFound
Unauthorized = exception.Unauthorized
TooManyRequests = exception.TooManyRequests
