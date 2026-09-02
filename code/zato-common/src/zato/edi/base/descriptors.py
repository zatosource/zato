# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
from collections.abc import Sequence
from enum import Enum
from typing import Generic, Protocol, TypeVar, overload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist, strnone
    any_ = any_
    anylist = anylist
    stranydict = stranydict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases following the zato.common.typing_ naming convention
strlistlist = list[list[str]]
strtypedict = dict[str, type]

T = TypeVar('T')

# ################################################################################################################################
# ################################################################################################################################

class EDIRawSegment(Protocol):
    """ The raw-segment protocol every EDI dialect satisfies - a tag, the optional
    repeat counters attached to the tag and the data elements, each element being
    a list of already unescaped component strings.
    """
    tag:'str'
    counters:'strlist'
    elements:'strlistlist'

# ################################################################################################################################
# ################################################################################################################################

raw_segment_list = list[EDIRawSegment]

# A covariant view of raw segments - what parsing entry points accept, so that
# the concrete segment lists of each dialect are assignable without a copy.
raw_segment_seq = Sequence[EDIRawSegment]

# ################################################################################################################################
# ################################################################################################################################

_composite_classes:'strtypedict' = {}

# ################################################################################################################################

def get_composite_class(name:'str') -> 'type | None':
    """ Returns the composite class registered under the given name - None when there is none.
    """
    out = _composite_classes.get(name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class EDIValidationError(Exception):
    """ Raised when a parsed message fails validation, e.g. a required element is empty.
    """

# ################################################################################################################################
# ################################################################################################################################

class Usage(str, Enum):
    """ EDI element usage indicator - required (verplicht), optional (conditioneel)
    or conditionally required (onder bepaalde condities verplicht).
    """
    REQUIRED = 'V'
    OPTIONAL = 'C'
    CONDITIONAL = 'CV'

# ################################################################################################################################
# ################################################################################################################################

class EDIRepeatableList(list):
    """ List subclass that delegates attribute access to the first element.
    """

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':
        if not self:
            raise AttributeError(f'Empty list has no attribute {name!r}')

        first = self[0]

        out = getattr(first, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _sort_by_position(descriptor:'any_') -> 'int':
    """ Sort key for descriptors by their position.
    """
    out = descriptor.position
    return out

# ################################################################################################################################
# ################################################################################################################################

class EDIComponent(Generic[T]):
    """ Descriptor for a single component within a composite data element.
    """

    def __init__(self, position:'int', usage:'Usage'=Usage.OPTIONAL, format:'str'='') -> 'None':
        self.position = position
        self.usage = usage
        self.format = format
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    @overload
    def __get__(self, instance:'None', owner:'type') -> 'EDIComponent[T]': ...

    @overload
    def __get__(self, instance:'any_', owner:'type') -> 'T | None': ...

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        # Values assigned explicitly win ..
        if self.attr_name in instance.__dict__:

            out = instance.__dict__[self.attr_name]
            return out

        # .. otherwise read from the raw component list, if there is one.
        raw = instance._raw_components
        index = self.position - 1
        raw_count = len(raw)

        if index >= raw_count:
            return None

        value = raw[index]
        if value:
            return value

        return None

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'T | str | None') -> 'None':
        instance.__dict__[self.attr_name] = value

        # An assignment marks the composite as modified for re-serialization.
        instance.__dict__['_is_modified'] = True

# ################################################################################################################################
# ################################################################################################################################

class EDIComposite:
    """ Base class for composite data element definitions - an element made of components.
    """
    _raw_components:'strlist' = []  # noqa: RUF012

    # Becomes True the moment any component is assigned to.
    _is_modified:'bool' = False

# ################################################################################################################################

    def __init_subclass__(cls, **kwargs:'any_') -> 'None':
        super().__init_subclass__(**kwargs)
        _composite_classes[cls.__name__] = cls

# ################################################################################################################################

    def __init__(self, **kwargs:'any_') -> 'None':
        self._raw_components = []

        for key, value in kwargs.items():
            setattr(self, key, value)

# ################################################################################################################################

    def _component_descriptors(self) -> 'anylist':
        """ Returns all component descriptors of this class, sorted by position.
        """
        descriptors:'anylist' = []

        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            if isinstance(attribute, EDIComponent):
                descriptors.append(attribute)

        descriptors.sort(key=_sort_by_position)

        out = descriptors
        return out

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this composite to a dictionary representation.
        """

        # Our response to produce
        out:'stranydict' = {}

        for descriptor in self._component_descriptors():
            value = getattr(self, descriptor.attr_name)

            # Empty components are included only when requested ..
            if value is None:
                if include_empty:
                    out[descriptor.attr_name] = None
                continue

            # .. everything else is a plain string.
            out[descriptor.attr_name] = value

        return out

# ################################################################################################################################

    def to_components(self) -> 'strlist':
        """ Builds the component string list for serialization, trimming unset trailing components.
        """

        # Our response to produce
        out:'strlist' = []

        last_assigned = 0

        for descriptor in self._component_descriptors():
            value = getattr(self, descriptor.attr_name)

            if value is None:
                out.append('')
            else:
                out.append(value)
                last_assigned = len(out)

        out = out[:last_assigned]
        return out

# ################################################################################################################################
# ################################################################################################################################

class EDIElement(Generic[T]):
    """ Descriptor for a single data element within a segment.
    """

    def __init__(
        self,
        position:'int',
        usage:'Usage',
        composite:'strnone' = None,
        format:'str' = '',
        ) -> 'None':
        self.position = position
        self.usage = usage
        self.composite = composite
        self.format = format
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    @overload
    def __get__(self, instance:'None', owner:'type') -> 'EDIElement[T]': ...

    @overload
    def __get__(self, instance:'any_', owner:'type') -> 'T': ...

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        cache = instance.__dict__

        # Values resolved or assigned earlier win ..
        if self.attr_name in cache:

            out = cache[self.attr_name]
            return out

        # .. otherwise resolve from the raw segment ..
        raw_segment = instance._raw_segment
        if raw_segment is None:

            # .. and with no raw segment either, a composite element yields an empty
            # .. instance that the caller can fill in while building a message.
            if self.composite:
                composite_class = _composite_classes[self.composite]
                composite = composite_class()
                cache[self.attr_name] = composite

                return composite

            return None

        index = self.position - 1
        element_count = len(raw_segment.elements)

        if index >= element_count:
            return None

        components = raw_segment.elements[index]

        out = self._build_value(components)
        cache[self.attr_name] = out

        return out

# ################################################################################################################################

    def _build_value(self, components:'strlist') -> 'any_':
        """ Builds a typed value from raw component data - a composite instance
        when the element declares one, otherwise a scalar string.
        """

        if not components:
            return None

        # A composite element wraps all its components ..
        if self.composite:
            composite_class = _composite_classes[self.composite]
            composite = composite_class()
            composite._raw_components = components

            return composite

        # .. a simple element is its first component ..
        first_component = components[0]
        if first_component:
            return first_component

        # .. and an element that is present but empty is None.
        return None

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'T') -> 'None':
        instance.__dict__[self.attr_name] = value

        # An assignment marks the segment as modified for re-serialization.
        instance.__dict__['_is_modified'] = True

# ################################################################################################################################
# ################################################################################################################################
