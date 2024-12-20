"""
Defines base constant and base container for constants.

"""

# type: ignore
# flake8: noqa

import types

from collections import OrderedDict as odict

from .exceptions import CandvConstantAlreadyBoundError
from .exceptions import CandvContainerMisusedError
from .exceptions import CandvInvalidConstantClass
from .exceptions import CandvInvalidGroupMemberError
from .exceptions import CandvMissingConstantError

from ._utils import export


UNBOUND_CONSTANT_CONTAINER_NAME = "__UNBOUND__"


@export
class SimpleConstant:
  """
  Base class for all constants.

  :ivar str name:
    constant's name: set up automatically and is equal to the name of the
    container's attribute

  """

  def __init__(self):
    self.name = None
    self.container = None

  def _post_init(self, name, container=None):
    """
    Called automatically by the container after container's class construction.

    """
    self.name = name
    self.container = container

  def to_group(self, group_class, **group_members):
    """
    Convert a constant into a constants group.

    :param class group_class:
      a class of group container which will be created

    :param group_members:
      unpacked dict which defines group members

    :returns:
      a lazy constants group which will be evaluated by the container.
      Method :meth:`merge_into_group` will be called during evaluation of the
      group

    **Example**:

    .. code-block:: python

      from candv import Constants
      from candv import SimpleConstant


      class FOO(Constants):
        A = SimpleConstant()
        B = SimpleConstant().to_group(Constants,

          B2 = SimpleConstant(),
          B0 = SimpleConstant(),
          B1 = SimpleConstant(),
        )

    """
    return _LazyConstantsGroup(self, group_class, **group_members)

  def merge_into_group(self, group):
    """
    Called automatically by the container after group construction.

    .. note::

      Redefine this method in all derived classes. Attach all custom attributes
      and methods to the group here.

    :param group:
      an instance of :class:`Constants` or of its subclass into which
      this constant will be merged

    :returns: ``None``

    """

  @property
  def full_name(self):
    prefix = (
      self.container.full_name
      if self.container
      else UNBOUND_CONSTANT_CONTAINER_NAME
    )
    return f"{prefix}.{self.name}"

  def to_primitive(self, *args, **kwargs):
    """
    Represent the constant via Python's primitive data structures.

    .. versionchanged:: 1.5.0
       The ``context`` param is replaced by ``*args`` and ``**kwargs``.

    .. versionadded:: 1.3.0

    """
    return {
      'name': self.name,
    }

  def __repr__(self):
    """
    Produce a text identifying the constant.

    """
    return f"<constant '{self.full_name}'>"

  def __hash__(self):
    """
    .. versionadded:: 1.3.1
    """
    return hash(self.full_name)

  def __eq__(self, other):
    """
    .. versionadded:: 1.3.1
    """
    return (
      isinstance(other, SimpleConstant)
      and (self.full_name == other.full_name)
    )

  def __ne__(self, other):
    """
    .. versionadded:: 1.3.1
    """
    return not (self == other)


class _LazyConstantsGroup:

  def __init__(self, constant, group_class, **group_members):
    self._validate_group_members(group_members)
    self.constant = constant
    self.group_class = group_class
    self.group_members = group_members

  @staticmethod
  def _validate_group_members(group_members):
    for name, obj in group_members.items():
      if not isinstance(obj, (SimpleConstant, _LazyConstantsGroup)):
        raise CandvInvalidGroupMemberError(
          f'invalid group member "{obj}": only instances of "{SimpleConstant}" '
          f'or other groups are allowed'
        )

  def _evaluate(self, parent, name):
    full_name = f"{parent.full_name}.{name}"
    group_bases = (self.group_class, )
    self.group_members.update({
      'name': name,
      'full_name': full_name,
      'container': parent,
      '__repr': f"<constants group '{full_name}'>",
    })

    group = type(full_name, group_bases, self.group_members)
    group.to_primitive = self._make_to_primitive(group, self.constant)
    self.constant.merge_into_group(group)

    del self.constant
    del self.group_class
    del self.group_members

    return group

  @staticmethod
  def _make_to_primitive(group, constant):
    # define aliases to avoid shadowing and infinite recursion
    constant_primitive = constant.to_primitive
    group_primitive = group.to_primitive

    def to_primitive(self, *args, **kwargs):
      primitive = constant_primitive(*args, **kwargs)
      primitive.update(group_primitive(*args, **kwargs))
      return primitive

    return types.MethodType(to_primitive, group)


class _ConstantsContainerMeta(type):
  """
  Metaclass for creating container classes for constants.

  """
  def __new__(self, class_name, bases, attributes):
    self._ensure_attribute(attributes, "name", class_name)
    self._ensure_attribute(attributes, "full_name", class_name)

    cls = super().__new__(self, class_name, bases, attributes)

    # set before validations to get correct repr
    cls.__repr = self._get_or_make_repr_value(attributes)

    self._validate_constant_class(cls)

    cls._members = self._make_members_from_attributes(cls, attributes)

    return cls

  @staticmethod
  def _ensure_attribute(attributes, attribute_name, default_value):
    if attribute_name not in attributes:
      attributes[attribute_name] = default_value

  @staticmethod
  def _validate_constant_class(target_cls):
    constant_class = getattr(target_cls, "constant_class", None)

    if not issubclass(constant_class, SimpleConstant):
      raise CandvInvalidConstantClass(
        f'invalid "constant_class" for "{target_cls}": must be derived from '
        f'"{SimpleConstant}", but got "{constant_class}"'
      )

  @staticmethod
  def _get_or_make_repr_value(attributes):
    value = attributes.pop("__repr", None)

    if not value:
      name = attributes["name"]
      value = f"<constants container '{name}'>"

    return value

  @classmethod
  def _make_members_from_attributes(cls, target_cls, attributes):
    members = []

    for name, the_object in attributes.items():
      if isinstance(the_object, _LazyConstantsGroup):
        group = the_object._evaluate(target_cls, name)
        setattr(target_cls, name, group)
        members.append((name, group))

      elif isinstance(the_object, target_cls.constant_class):
        cls._validate_constant_is_not_bound(target_cls, name, the_object)
        the_object._post_init(name=name, container=target_cls)
        members.append((name, the_object))

      elif isinstance(the_object, SimpleConstant):
        # init but do not append constants which are more generic
        # than ``constant_class``
        the_object._post_init(name=name)

    return odict(members)

  @staticmethod
  def _validate_constant_is_not_bound(target_cls, attribute_name, the_object):
    if the_object.container is not None:
      raise CandvConstantAlreadyBoundError(
        f'cannot use "{the_object}" as value for "{attribute_name}" attribute '
        f'of "{target_cls}" container: already bound to "{the_object.container}"'
      )

  def __repr__(self):
    return self.__repr

  def __getitem__(self, name):
    """
    Try to get constant by its name.

    :param str name: name of constant to search for

    :returns: a constant
    :rtype: an instance of :class:`SimpleConstant` or its subclass

    :raises CandvMissingConstantError:
      if constant with name ``name`` is not present in container

    **Example**:

    .. code-block:: python

      from candv import Constants
      from candv import SimpleConstant


      class FOO(Constants):
        foo = SimpleConstant()
        bar = SimpleConstant()

    .. code-block:: python

      >>> FOO['foo']
      <constant 'FOO.foo'>

    """
    try:
      return self._members[name]
    except KeyError:
      raise CandvMissingConstantError(
        f'constant "{name}" is not present in "{self}"'
      )

  def __contains__(self, name):
    return name in self._members

  def __len__(self):
    return len(self._members)

  def __iter__(self):
    return self.iternames()

  def get(self, name, default=None):
    """
    Try to get a constant by its name or fallback to a default.

    :param str name:
      name of constant to search

    :param default:
      an object returned by default if constant with a given name is not present
      in the container

    :returns: a constant or a default value
    :rtype: an instance of :class:`SimpleConstant` or its subclass, or `default` value

    **Example**:

    .. code-block:: python

      from candv import Constants
      from candv import SimpleConstant


      class FOO(Constants):
        foo = SimpleConstant()
        bar = SimpleConstant()

    .. code-block:: python

      >>> FOO.get('foo')
      <constant 'FOO.foo'>

      >>> FOO.get('xxx')
      None

      >>> FOO.get('xxx', default=123)
      123

    """
    return self._members.get(name, default)

  def has_name(self, name):
    """
    Check if the container has a constant with a given name.

    :param str name: a constant's name to check

    :returns: ``True`` if given name belongs to container, ``False`` otherwise
    :rtype: :class:`bool`

    """
    return name in self

  def names(self):
    """
    List all names of constants within the container.

    :returns: a list of constant names in order constants were defined
    :rtype: :class:`list` of strings

    **Example**:

    .. code-block:: python

      from candv import Constants
      from candv import SimpleConstant


      class FOO(Constants):
        foo = SimpleConstant()
        bar = SimpleConstant()

    .. code-block:: python

      >>> FOO.names()
      ['foo', 'bar']

    """
    return list(self._members.keys())

  def iternames(self):
    """
    Get an iterator over constants names.

    Same as :meth:`names`, but returns an interator.

    """
    return iter(self._members.keys())

  def constants(self):
    """
    List all constants in the container.

    :returns: list of constants in order they were defined
    :rtype: :class:`list`

    **Example**:

    .. code-block:: python

      from candv import Constants
      from candv import SimpleConstant


      class FOO(Constants):
        foo = SimpleConstant()
        bar = SimpleConstant()

    .. code-block:: python

      >>> [x.name for x in FOO.constants()]
      ['foo', 'bar']

    """
    return list(self._members.values())

  def iterconstants(self):
    """
    Get an iterator over constants.

    Same as :meth:`constants`, but returns an interator

    """
    return iter(self._members.values())

  def items(self):
    """
    Get list of constants names along with constants themselves.

    :returns:
      list of constants with their names in order they were defined.
      Each element in the list is a :class:`tuple` in format ``(name, constant)``.
    :rtype: :class:`list`

    **Example**:

    .. code-block:: python

      from candv import Constants
      from candv import SimpleConstant

      class FOO(Constants):
        foo = SimpleConstant()
        bar = SimpleConstant()

    .. code-block:: python

      >>> FOO.items()
      [('foo', <constant 'FOO.foo'>), ('bar', <constant 'FOO.bar'>)]

    """
    return list(self._members.items())

  def iteritems(self):
    """
    Get an iterator over constants names along with constants themselves.

    Same as :meth:`items`, but returns an interator

    """
    return iter(self._members.items())

  #: .. versionadded:: 1.1.2
  #:
  #: Alias for :meth:`constants`.
  #: Added for consistency with dictionaries. Use :class:`~candv.Values` and
  #: :meth:`~candv.Values.values` if you need to have constants with real
  #: values.
  values = constants

  #: .. versionadded:: 1.1.2
  #:
  #: Alias for :meth:`iterconstants`.
  #: Added for consistency with dictionaries. Use :class:`~candv.Values` and
  #: :meth:`~candv.Values.itervalues` if you need to have constants with real
  #: values.
  itervalues = iterconstants

  def to_primitive(self, *args, **kwargs):
    """
    .. versionchanged:: 1.5.0
       The ``context`` param is replaced by ``*args`` and ``**kwargs``.

    .. versionadded:: 1.3.0

    """
    items = [
      x.to_primitive(*args, **kwargs)
      for x in self.iterconstants()
    ]
    return {
      'name': self.name,
      'items': items,
    }


@export
class Constants(metaclass=_ConstantsContainerMeta):
  """
  Base class for creating constants containers.

  Each constant defined within the container will remember its creation order.

  See an example in :meth:`constants`.

  :cvar constant_class:
    defines a class of constants which a container will store.
    This attribute **MUST** be set up manually when you define a new container
    type. Otherwise container will not be initialized. Default: ``None``

  :raises CandvContainerMisusedError:
    if you try to create an instance of container. Containers are singletons and
    they cannot be instantiated. Their attributes must be used directly.

  """

  #: Defines a top-level class of constants which can be stored by container
  constant_class = SimpleConstant

  def __new__(cls):
    raise CandvContainerMisusedError(
      f'"{cls}" cannot be instantiated: constant containers are not designed '
      f'for that'
    )


@export
def with_constant_class(the_class):
  """
  Create a mixin class with ``constant_class`` attribute.

  Allows to set a constant class for constants container outside container itself.
  This may help to create more readable container definition, e.g.:

  .. code-block:: python

    from candv import Constants
    from candv import SimpleConstant
    from candv import with_constant_class


    class CustomConstant(SimpleConstant):
      ...

    class FOO(with_constant_class(CustomConstant), Constants):
      A = CustomConstant()
      B = CustomConstant()

  .. code-block:: python

    >>> FOO.constant_class
    <class '__main__.CustomConstant'>

  """
  class ConstantsMixin:
    constant_class = the_class

  return ConstantsMixin
