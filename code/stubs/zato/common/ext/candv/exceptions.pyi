from typing import Any, TYPE_CHECKING

from _utils import export


class CandvException(Exception):
    ...

class CandvTypeError(TypeError, CandvException):
    ...

class CandvInvalidGroupMemberError(CandvTypeError):
    ...

class CandvInvalidConstantClass(CandvTypeError):
    ...

class CandvContainerMisusedError(CandvTypeError):
    ...

class CandvConstantAlreadyBoundError(ValueError, CandvException):
    ...

class CandvMissingConstantError(KeyError, CandvException):
    ...

class CandvValueNotFoundError(ValueError, CandvException):
    ...
