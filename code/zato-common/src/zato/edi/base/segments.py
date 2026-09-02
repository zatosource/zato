# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import json

from typing import Generic, Self, TypeVar, overload

# Zato
from zato.edi.base.descriptors import EDIComponent, EDIComposite, EDIElement, EDIRepeatableList, _sort_by_position

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intnone, stranydict, strlist
    from zato.edi.base.descriptors import EDIRawSegment, raw_segment_seq, strlistlist
    EDIComponent = EDIComponent
    any_ = any_
    anylist = anylist
    intnone = intnone
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases following the zato.common.typing_ naming convention
segment_class_type = type['EDISegment']
group_class_type   = type['EDIGroup']

T = TypeVar('T')

# ################################################################################################################################
# ################################################################################################################################

class EDISegment:
    """ Base class for all typed segment definitions, independent of any one EDI dialect.
    The dialect layer binds the three class-level hooks below to its own raw-segment
    machinery - this module never imports a concrete raw segment class.
    """
    _segment_tag:'str' = ''
    _raw_segment:'any_' = None

    # Becomes True the moment any element is assigned to.
    _is_modified:'bool' = False

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
    def from_raw(cls, raw_segment:'EDIRawSegment') -> 'Self':
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
        segment_class:'segment_class_type',
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
    def from_raw(cls, raw_segments:'raw_segment_seq') -> 'Self':
        """ Wraps a slice of raw segments in a typed group instance.
        """
        group = cls.__new__(cls)
        group._raw_segments = raw_segments

        out = group
        return out

# ################################################################################################################################

    def serialize(self, separators:'any_'=None) -> 'str':
        """ Serializes a built group by walking its declared attributes in declaration order,
        one segment per line. Groups parsed from wire data are serialized by their enclosing message.
        """
        lines:'strlist' = []

        group_class = type(self)

        for descriptor in _declared_attr_descriptors(group_class):
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
        group_class:'group_class_type',
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

    instance_class = type(instance)

    for name in dir(instance_class):
        attribute = getattr(instance_class, name)
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
                item_dict = item.to_dict(include_empty=include_empty)
                items.append(item_dict)

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
