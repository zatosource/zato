# type: ignore
# flake8: noqa

from ._utils import export


@export
class CandvException(Exception):
  """
  Base exception

  .. versionadded:: 1.4.0

  """


@export
class CandvTypeError(TypeError, CandvException):
  """
  .. versionadded:: 1.4.0
  """


@export
class CandvInvalidGroupMemberError(CandvTypeError):
  """
  .. versionadded:: 1.4.0
  """


@export
class CandvInvalidConstantClass(CandvTypeError):
  """
  .. versionadded:: 1.4.0
  """


@export
class CandvContainerMisusedError(CandvTypeError):
  """
  .. versionadded:: 1.4.0
  """


@export
class CandvConstantAlreadyBoundError(ValueError, CandvException):
  """
  .. versionadded:: 1.4.0
  """


@export
class CandvMissingConstantError(KeyError, CandvException):
  """
  .. versionadded:: 1.4.0
  """


@export
class CandvValueNotFoundError(ValueError, CandvException):
  """
  .. versionadded:: 1.4.0
  """
