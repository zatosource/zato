# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import json

from enum import Enum
from typing import Generic, Protocol, TypeVar, overload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases following the zato.common.typing_ naming convention
any_               = 'Any'
intnone            = 'Optional[int]'
strnone            = 'Optional[str]'
strlist            = list[str]
strlistlist        = list[list[str]]
anylist            = list['Any']
stranydict         = dict[str, 'Any']
strtypedict        = dict[str, type]
message_class_dict = dict[str, type['EDIMessage']]

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

# ################################################################################################################################
# ################################################################################################################################

_composite_classes:'strtypedict' = {}

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

        out = getattr(self[0], name)
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

# ################################################################################################################################
# ################################################################################################################################

class EDIComposite:
    """ Base class for composite data element definitions - an element made of components.
    """
    _raw_components:'strlist' = []  # noqa: RUF012

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

# ################################################################################################################################
# ################################################################################################################################

class EDISegment:
    """ Base class for all typed segment definitions, independent of any one EDI dialect.
    The dialect layer binds the three class-level hooks below to its own raw-segment
    machinery - this module never imports a concrete raw segment class.
    """
    _segment_tag:'str' = ''
    _raw_segment:'any_' = None

    # The concrete raw-segment class of the dialect, satisfying EDIRawSegment
    _raw_segment_class:'any_' = None

    # The dialect's wire serializer - a staticmethod taking (raw_segment, separators)
    _serialize_segment:'any_' = None

    # The dialect's default service characters
    _default_separators:'any_' = None

# ################################################################################################################################

    def __init__(self, **kwargs:'any_') -> 'None':
        self._raw_segment = None

        for key, value in kwargs.items():
            setattr(self, key, value)

# ################################################################################################################################

    @classmethod
    def from_raw(cls, raw_segment:'EDIRawSegment') -> 'EDISegment':
        """ Wraps a raw segment in a typed segment instance.
        """
        segment = cls.__new__(cls)
        segment._raw_segment = raw_segment

        out = segment
        return out

# ################################################################################################################################

    def _element_descriptors(self) -> 'anylist':
        """ Returns all element descriptors of this class, sorted by position.
        """
        descriptors:'anylist' = []

        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            if isinstance(attribute, EDIElement):
                descriptors.append(attribute)

        descriptors.sort(key=_sort_by_position)

        out = descriptors
        return out

# ################################################################################################################################

    def to_raw(self) -> 'EDIRawSegment':
        """ Builds a raw segment from this segment's current values.
        A segment parsed from wire data returns its original raw form with any
        explicitly assigned values merged in, so a round trip stays byte-exact.
        """

        # A parsed segment starts from its wire data ..
        if self._raw_segment is not None:
            raw_segment = self._raw_segment
        else:
            raw_segment = self._raw_segment_class(self._segment_tag, [], [])

        # .. and each explicitly assigned descriptor value overrides the raw element.
        elements:'strlistlist' = []

        for existing in raw_segment.elements:
            elements.append(list(existing))

        for descriptor in self._element_descriptors():
            if descriptor.attr_name not in self.__dict__:
                continue

            value = self.__dict__[descriptor.attr_name]

            if isinstance(value, EDIComposite):
                components = value.to_components()
            elif value is None:
                components = ['']
            else:
                components = [value]

            index = descriptor.position - 1

            # Missing intermediate elements are padded with empty strings.
            while len(elements) <= index:
                elements.append([''])

            elements[index] = components

        # Empty trailing elements are trimmed from the end, but only the padding this method
        # added itself - elements that were present on the wire are never dropped.
        raw_element_count = len(raw_segment.elements)
        last_assigned = raw_element_count

        for element_index, components in enumerate(elements):
            if element_index < raw_element_count:
                continue
            for component_value in components:
                if component_value:
                    last_assigned = element_index + 1
                    break

        elements = elements[:last_assigned]

        out = self._raw_segment_class(raw_segment.tag, raw_segment.counters, elements)
        return out

# ################################################################################################################################

    def serialize(self, separators:'any_'=None) -> 'str':
        """ Serializes this segment to its wire form.
        """
        # Without explicit separators, the dialect's defaults apply.
        if separators is None:
            separators = self._default_separators

        raw_segment = self.to_raw()

        out = self._serialize_segment(raw_segment, separators)
        return out

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this segment to a dictionary representation.
        """

        # Our response to produce
        out:'stranydict' = {'_segment_tag': self._segment_tag}

        raw_segment = self._raw_segment
        if raw_segment is not None:
            if raw_segment.counters:
                out['_counters'] = raw_segment.counters

        for descriptor in self._element_descriptors():
            value = getattr(self, descriptor.attr_name)

            # Empty elements are included only when requested ..
            if value is None:
                if include_empty:
                    out[descriptor.attr_name] = None
                continue

            # .. composites are converted recursively ..
            if isinstance(value, EDIComposite):
                out[descriptor.attr_name] = value.to_dict(include_empty=include_empty)

            # .. and scalars are stored directly.
            else:
                out[descriptor.attr_name] = value

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone'=None, include_empty:'bool'=True) -> 'str':
        """ Converts this segment to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################
# ################################################################################################################################

class EDISegmentAttr(Generic[T]):
    """ Descriptor for a segment reference within a message or group. The segment class
    is passed in directly because the same tag can mean different segments in different
    dialects (e.g. the Dutch Medeur PID is not the UN standard NAD).
    """

    def __init__(
        self,
        segment_class:'type[EDISegment]',
        optional:'bool' = False,
        repeatable:'bool' = False,
        ) -> 'None':
        self.segment_class = segment_class
        self.tag = segment_class._segment_tag
        self.optional = optional
        self.repeatable = repeatable
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    @overload
    def __get__(self, instance:'None', owner:'type') -> 'EDISegmentAttr[T]': ...

    @overload
    def __get__(self, instance:'any_', owner:'type') -> 'T': ...

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        cache = instance.__dict__

        if self.attr_name in cache:

            out = cache[self.attr_name]
            return out

        segment_class = self.segment_class
        raw_segments = instance._raw_segments

        # With no raw data we are building from scratch - hand out an empty segment to fill in ..
        if raw_segments is None:
            segment = segment_class()
            cache[self.attr_name] = segment

            return segment

        # .. with raw data, repeatable references collect every matching segment ..
        if self.repeatable:
            out = EDIRepeatableList()

            for raw_segment in raw_segments:
                if raw_segment.tag == self.tag:
                    segment = segment_class.from_raw(raw_segment)
                    out.append(segment)

            cache[self.attr_name] = out

            return out

        # .. and non-repeatable ones resolve to the first match.
        for raw_segment in raw_segments:
            if raw_segment.tag == self.tag:
                segment = segment_class.from_raw(raw_segment)
                cache[self.attr_name] = segment

                return segment

        return None

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'T | list[T]') -> 'None':
        instance.__dict__[self.attr_name] = value

# ################################################################################################################################
# ################################################################################################################################

class EDIGroup:
    """ Base class for repeating segment groups. A group is identified by its leader tag -
    each occurrence of the leader on the wire starts a new instance of the group.
    Subclasses declare EDISegmentAttr and EDIGroupAttr members like messages do.
    """
    _leader_tag:'str' = ''
    _raw_segments:'any_' = None

# ################################################################################################################################

    def __init__(self, **kwargs:'any_') -> 'None':
        self._raw_segments = None

        for key, value in kwargs.items():
            setattr(self, key, value)

# ################################################################################################################################

    @classmethod
    def from_raw(cls, raw_segments:'raw_segment_list') -> 'EDIGroup':
        """ Wraps a slice of raw segments in a typed group instance.
        """
        group = cls.__new__(cls)
        group._raw_segments = raw_segments

        out = group
        return out

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this group to a dictionary representation.
        """
        out = _attrs_to_dict(self, include_empty)
        return out

# ################################################################################################################################
# ################################################################################################################################

class EDIGroupAttr(Generic[T]):
    """ Descriptor for a repeating group reference within a message.
    """

    def __init__(
        self,
        group_class:'type[EDIGroup]',
        optional:'bool' = False,
        repeatable:'bool' = True,
        ) -> 'None':
        self.group_class = group_class
        self.optional = optional
        self.repeatable = repeatable
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    @overload
    def __get__(self, instance:'None', owner:'type') -> 'EDIGroupAttr[T]': ...

    @overload
    def __get__(self, instance:'any_', owner:'type') -> 'T': ...

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        cache = instance.__dict__

        if self.attr_name in cache:

            out = cache[self.attr_name]
            return out

        raw_segments = instance._raw_segments
        if raw_segments is None:
            out = EDIRepeatableList()
            cache[self.attr_name] = out

            return out

        # Each occurrence of the leader tag starts a new group instance and every segment
        # up to the next leader (or the end of the message) belongs to that instance.
        leader_tag = self.group_class._leader_tag
        out = EDIRepeatableList()

        slice_start:'intnone' = None

        for index, raw_segment in enumerate(raw_segments):
            if raw_segment.tag == leader_tag:
                if slice_start is not None:
                    group = self.group_class.from_raw(raw_segments[slice_start:index])
                    out.append(group)
                slice_start = index

        if slice_start is not None:
            group = self.group_class.from_raw(raw_segments[slice_start:])
            out.append(group)

        cache[self.attr_name] = out

        return out

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'T | list[T]') -> 'None':
        instance.__dict__[self.attr_name] = value

# ################################################################################################################################
# ################################################################################################################################

def _attrs_to_dict(instance:'any_', include_empty:'bool') -> 'stranydict':
    """ Converts the segment and group attributes of a message or group to a dictionary.
    """

    # Our response to produce
    out:'stranydict' = {}

    for name in dir(type(instance)):
        attribute = getattr(type(instance), name)
        is_segment_attr = isinstance(attribute, EDISegmentAttr)
        is_group_attr = isinstance(attribute, EDIGroupAttr)

        if not is_segment_attr:
            if not is_group_attr:
                continue

        value = getattr(instance, name)

        # Empty attributes are included only when requested ..
        if value is None:
            if include_empty:
                out[name] = None
            continue

        # .. lists convert each of their items ..
        if isinstance(value, list):
            items:'anylist' = []

            for item in value:
                items.append(item.to_dict(include_empty=include_empty))

            out[name] = items

        # .. and single values convert directly.
        else:
            out[name] = value.to_dict(include_empty=include_empty)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _declared_attr_descriptors(message_class:'type') -> 'anylist':
    """ Collects EDISegmentAttr and EDIGroupAttr descriptors in their declaration order,
    walking the class hierarchy in reverse MRO order so base-class descriptors come first.
    """

    # Our response to produce
    out:'anylist' = []

    seen:'strlist' = []

    for klass in reversed(message_class.__mro__):
        for name, class_attribute in vars(klass).items():
            if isinstance(class_attribute, (EDISegmentAttr, EDIGroupAttr)):
                if name not in seen:
                    seen.append(name)
                    out.append(class_attribute)

    return out

# ################################################################################################################################
# ################################################################################################################################

class EDIMessage:
    """ Base class for all typed message definitions, independent of any one EDI dialect.
    Message resolution from raw segments (e.g. EDIFACT's UNH lookup) belongs to the
    dialect layer, which also binds the class-level hooks below.
    """

    # The message type identifier, e.g. MEDLAB
    _message_type:'str' = ''

    # The message version identifier, e.g. 1 - empty means any version
    _message_version:'str' = ''

    # The association assigned code, e.g. MRPN32 or NHS003 - empty means none
    _association:'str' = ''

    _registry:'message_class_dict' = {}  # noqa: RUF012

    _raw_segments:'any_' = None
    _separators:'any_' = None

    # The dialect's wire serializer - a staticmethod taking (raw_segment, separators)
    _serialize_segment:'any_' = None

    # The dialect's segment class for tags without a Python class definition
    _generic_segment_class:'any_' = None

# ################################################################################################################################

    def __init_subclass__(cls, **kwargs:'any_') -> 'None':
        super().__init_subclass__(**kwargs)

        # A message registers under its association code when it has one,
        # under type:version when it declares a version, and under its bare type.
        if cls._association:
            EDIMessage._registry[cls._association] = cls

        if cls._message_type:
            if cls._message_version:
                EDIMessage._registry[f'{cls._message_type}:{cls._message_version}'] = cls

            if cls._message_type not in EDIMessage._registry:
                EDIMessage._registry[cls._message_type] = cls

# ################################################################################################################################

    def __init__(self, **kwargs:'any_') -> 'None':
        self._raw_segments = None

        for key, value in kwargs.items():
            setattr(self, key, value)

# ################################################################################################################################

    @classmethod
    def from_raw(cls, raw_segments:'raw_segment_list', separators:'any_') -> 'EDIMessage':
        """ Wraps the raw segments of one message in a typed message instance.
        """
        message = cls.__new__(cls)
        message._raw_segments = raw_segments
        message._separators = separators

        out = message
        return out

# ################################################################################################################################

    def segments(self, tag:'str') -> 'anylist':
        """ Returns all typed segments with the given tag, in wire order.
        Tags without a Python class definition come back as generic segments.
        """

        # Our response to produce
        out:'anylist' = []

        raw_segments = self._raw_segments
        if raw_segments is None:
            return out

        for raw_segment in raw_segments:
            if raw_segment.tag == tag:
                segment = self._generic_segment_class.from_raw(raw_segment)
                out.append(segment)

        return out

# ################################################################################################################################

    def serialize(self, separators:'any_'=None) -> 'str':
        """ Serializes this message to its wire form, one segment per line.
        """
        if separators is None:
            separators = self._separators

        lines:'strlist' = []

        # A parsed message serializes its raw segments to stay byte-faithful ..
        raw_segments = self._raw_segments
        if raw_segments is not None:
            for raw_segment in raw_segments:
                line = self._serialize_segment(raw_segment, separators)
                lines.append(line)

            out = '\n'.join(lines)
            return out

        # .. a built message walks its declared attributes in declaration order.
        for descriptor in _declared_attr_descriptors(type(self)):
            value = self.__dict__.get(descriptor.attr_name)
            if value is None:
                continue

            if isinstance(value, list):
                for item in value:
                    line = item.serialize(separators)
                    lines.append(line)
            else:
                line = value.serialize(separators)
                lines.append(line)

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    def to_dict(self, include_empty:'bool'=True) -> 'stranydict':
        """ Converts this message to a dictionary representation.
        """

        # Our response to produce
        out:'stranydict' = {'_message_type': self._message_type}

        attrs = _attrs_to_dict(self, include_empty)
        out.update(attrs)

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone'=None, include_empty:'bool'=True) -> 'str':
        """ Converts this message to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################
# ################################################################################################################################
