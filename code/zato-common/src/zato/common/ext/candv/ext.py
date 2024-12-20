"""
Provides extra ready-to-use classes for constructing custom constants.

"""
# type: ignore
# flake8: noqa

import operator

from .core import Constants
from .core import SimpleConstant

from .exceptions import CandvValueNotFoundError

from ._utils import export


@export
class VerboseMixin:
  """
  Adds ``verbose_name`` and ``help_text`` attributes to constants.

  Arguments must be passed as kwargs.

  :argument str verbose_name: optional verbose name
  :argument str help_text: optional description

  **Example**:

  .. code-block:: python

    class CustomConstant(object):

      def __init__(self, arg1, arg2, kwarg1=None):
        pass


    class VerboseCustomConstant(VerboseMixin, CustomConstant):

      def __init__(self, arg1, arg2, kwarg1=None, verbose_name=None, help_text=None):
        super().__init__(
          arg1,
          arg2,
          kwarg1=kwarg1,
          verbose_name=verbose_name,
          help_text=help_text,
        )

  """
  def __init__(self, *args, **kwargs):
    self.verbose_name = kwargs.pop('verbose_name', None)
    self.help_text = kwargs.pop('help_text', None)
    super().__init__(*args, **kwargs)

  def merge_into_group(self, group):
    """
    Overrides :meth:`~candv.base.Constant.merge_into_group` to add
    ``verbose_name`` with ``help_text`` attributes to the target group.

    """
    super().merge_into_group(group)
    group.verbose_name = self.verbose_name
    group.help_text = self.help_text

  def to_primitive(self, *args, **kwargs):
    """
    .. versionchanged:: 1.5.0
       The ``context`` param is replaced by ``*args`` and ``**kwargs``.

    .. versionadded:: 1.3.0

    """
    primitive = super().to_primitive(*args, **kwargs)
    primitive.update({
      'verbose_name': (
        str(self.verbose_name)
        if self.verbose_name is not None
        else None
      ),
      'help_text': (
        str(self.help_text)
        if self.help_text is not None
        else None
      ),
    })
    return primitive


@export
class VerboseConstant(VerboseMixin, SimpleConstant):
  """
  A constant with optional verbose name and optional help text.

  :argument str verbose_name: optional verbose name of the constant
  :argument str help_text: optional description of the constant

  :ivar str verbose_name: verbose name of the constant. Default: ``None``
  :ivar str help_text: verbose description of the constant. Default: ``None``

  """
  def __init__(self, verbose_name=None, help_text=None):
    super().__init__(verbose_name=verbose_name, help_text=help_text)


@export
class ValueConstant(SimpleConstant):
  """
  A constant with ability to hold arbitrary values.

  :argument value: a value to attach to constant
  :ivar value: constant's value

  """
  def __init__(self, value):
    super().__init__()
    self.value = value

  def merge_into_group(self, group):
    """
    Redefines :meth:`~candv.base.Constant.merge_into_group` and adds ``value``
    attribute to the target group.

    """
    super().merge_into_group(group)
    group.value = self.value

  def to_primitive(self, *args, **kwargs):
    """
    .. versionchanged:: 1.5.0
       The ``context`` param is replaced by ``*args`` and ``**kwargs``.

    .. versionadded:: 1.3.0

    """
    primitive = super().to_primitive(*args, **kwargs)
    value = self.value

    if hasattr(value, "isoformat"):
      value = value.isoformat()

    if hasattr(value, "to_primitive"):
      value = value.to_primitive(*args, **kwargs)

    elif callable(value):
      value = value()

    primitive['value'] = value
    return primitive


@export
class VerboseValueConstant(VerboseMixin, ValueConstant):
  """
  A constant which can have both verbose name, help text, and a value.

  :argument value: a value to attach to the constant
  :argument str verbose_name: an optional verbose name of the constant
  :argument str help_text: an optional description of the constant

  :ivar value: constant's value
  :ivar str verbose_name: verbose name of the constant. Default: ``None``
  :ivar str help_text: verbose description of the constant. Default: ``None``

  """
  def __init__(self, value, verbose_name=None, help_text=None):
    super().__init__(value, verbose_name=verbose_name, help_text=help_text)


@export
class Values(Constants):
  """
  A container for :class:`ValueConstant` and its derivatives.

  Supports getting and filtering constants by their values plus listing values
  of all constants in container.

  """
  constant_class = ValueConstant

  @classmethod
  def get_by_value(cls, value):
    """
    Get a constant by its value.

    :param value: value of the constant to look for

    :returns: first found constant with given value

    :raises CandvValueNotFoundError: if no constant in container has given value

    """
    for constant in cls.iterconstants():
      if constant.value == value:
        return constant

    raise CandvValueNotFoundError(
      "constant with value \"{0}\" is not present in \"{1}\""
      .format(value, cls)
    )

  @classmethod
  def filter_by_value(cls, value):
    """
    Get all constants which have given value.

    :param value: value of the constants to look for
    :returns: list of all found constants with given value

    """
    constants = []

    for constant in cls.iterconstants():
      if constant.value == value:
        constants.append(constant)

    return constants

  @classmethod
  def values(cls):
    """
    List values of all constants in the order they were defined.

    :returns: :class:`list` of values

    **Example**:

    .. code-block:: python

      from candv import Values
      from candv import ValueConstant


      class FOO(Values):
        TWO  = ValueConstant(2)
        ONE  = ValueConstant(1)
        SOME = ValueConstant("some string")

    .. code-block:: python

      >>> FOO.values()
      [2, 1, 'some string']

    .. note::

      Overrides :meth:`~candv.base.ConstantsContainer.values` since 1.1.2.

    """
    return [
      x.value
      for x in cls.iterconstants()
    ]

  @classmethod
  def itervalues(cls):
    """
    Get an iterator over values of all constants in the order they were defined.

    Same as :meth:`values` but returns an interator.

    .. note::

      Overrides :meth:`~candv.base.ConstantsContainer.itervalues` since 1.1.2.

    """
    return map(operator.attrgetter("value"), cls.iterconstants())
