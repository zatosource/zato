from typing import Any, TYPE_CHECKING

from http.client import BAD_REQUEST, CONFLICT, FORBIDDEN, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_FOUND, SERVICE_UNAVAILABLE, UNAUTHORIZED
from zato.common.http_ import HTTP_RESPONSES

ClientHTTPError = Reportable

class ZatoException(Exception):
    __str__: Any
    cid: Any
    msg: Any
    def __init__(self: Any, cid: Any = ..., msg: Any = ...) -> None: ...
    def __repr__(self: Any) -> None: ...

class ServiceMissingException(ZatoException):
    ...

class RuntimeInvocationError(ZatoException):
    ...

class ClientSecurityException(ZatoException):
    ...

class ConnectionException(ZatoException):
    ...

class TimeoutException(ConnectionException):
    ...

class StatusAwareException(ZatoException):
    status: Any
    reason: Any
    needs_msg: Any
    def __init__(self: Any, cid: Any, msg: Any, status: Any, needs_msg: Any = ...) -> None: ...
    def __repr__(self: Any) -> None: ...

class HTTPException(StatusAwareException):
    ...

class ParsingException(ZatoException):
    ...

class NoDistributionFound(ZatoException):
    def __init__(self: Any, path: Any) -> None: ...

class Inactive(ZatoException):
    def __init__(self: Any, name: Any) -> None: ...

class Reportable(HTTPException):
    def __init__(self: Any, cid: Any, msg: Any, status: Any, needs_msg: Any = ...) -> None: ...

class BackendInvocationError(Reportable):
    def __init__(self: Any, cid: Any, msg: Any = ..., needs_msg: Any = ...) -> None: ...

class BadRequest(Reportable):
    def __init__(self: Any, cid: Any, msg: Any = ..., needs_msg: Any = ...) -> None: ...

class Conflict(Reportable):
    def __init__(self: Any, cid: Any, msg: Any) -> None: ...

class Forbidden(Reportable):
    def __init__(self: Any, cid: Any, msg: Any = ..., *ignored_args: Any, **ignored_kwargs: Any) -> None: ...

class MethodNotAllowed(Reportable):
    def __init__(self: Any, cid: Any, msg: Any) -> None: ...

class NotFound(Reportable):
    def __init__(self: Any, cid: Any, msg: Any) -> None: ...

class Unauthorized(Reportable):
    challenge: Any
    def __init__(self: Any, cid: Any, msg: Any, challenge: Any) -> None: ...

class TooManyRequests(Reportable):
    def __init__(self: Any, cid: Any, msg: Any) -> None: ...

class InternalServerError(Reportable):
    def __init__(self: Any, cid: Any, msg: Any = ...) -> None: ...

class ServiceUnavailable(Reportable):
    def __init__(self: Any, cid: Any, msg: Any) -> None: ...

class ConnectorClosedException(Exception):
    inner_exc: Any
    def __init__(self: Any, exc: Any, message: Any) -> None: ...
