# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import json

from typing import Self

# Zato
from zato.edi.base.descriptors import EDIComposite
from zato.edi.base.segments import EDIGroup, EDISegment, _attrs_to_dict, _declared_attr_descriptors

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intnone, stranydict, strlist
    from zato.edi.base.descriptors import raw_segment_seq
    any_ = any_
    anylist = anylist
    intnone = intnone
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases following the zato.common.typing_ naming convention
message_class_dict = dict[str, type['EDIMessage']]

# Maps id(raw_segment) to the typed segment holding assignments for it.
segment_override_dict = dict[int, 'EDISegment']

# ################################################################################################################################
# ################################################################################################################################

def _is_segment_modified(segment:'EDISegment') -> 'bool':
    """ Tells whether a segment holds any assignment - directly on one of its elements,
    or inside one of the composite instances its reads have cached.
    """

    # Our response to produce
    out = segment._is_modified

    # Without a direct assignment, a cached composite with one of its own
    # still makes the whole segment modified.
    if not out:
        for value in segment.__dict__.values():
            if isinstance(value, EDIComposite):
                if value._is_modified:
                    out = True
                    break

    return out

# ################################################################################################################################

def _collect_modified_segments(container:'any_', out:'segment_override_dict') -> 'None':
    """ Maps the identity of each modified segment's raw wire segment to the typed instance
    that holds the assignments. The container is a message or a group, and groups nest,
    so the walk recurses through repeatable lists.
    """
    for value in container.__dict__.values():

        # A typed segment wrapping wire data carries assignments to merge in.
        if isinstance(value, EDISegment):
            if value._raw_segment is not None:
                if _is_segment_modified(value):
                    raw_segment_id = id(value._raw_segment)
                    out[raw_segment_id] = value

        # A repeatable list holds segments or groups.
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, EDISegment):
                    if item._raw_segment is not None:
                        if _is_segment_modified(item):
                            raw_segment_id = id(item._raw_segment)
                            out[raw_segment_id] = item
                elif isinstance(item, EDIGroup):
                    _collect_modified_segments(item, out)

        # A nested group has cached segments of its own.
        elif isinstance(value, EDIGroup):
            _collect_modified_segments(value, out)

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
                type_and_version = f'{cls._message_type}:{cls._message_version}'
                EDIMessage._registry[type_and_version] = cls

            if cls._message_type not in EDIMessage._registry:
                EDIMessage._registry[cls._message_type] = cls

# ################################################################################################################################

    def __init__(self, **kwargs:'any_') -> 'None':
        self._raw_segments = None

        for key, value in kwargs.items():
            setattr(self, key, value)

# ################################################################################################################################

    @classmethod
    def from_raw(cls, raw_segments:'raw_segment_seq', separators:'any_') -> 'Self':
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

        # A parsed message serializes its raw segments, with the segments
        # the caller assigned to re-serialized from their typed values ..
        raw_segments = self._raw_segments
        if raw_segments is not None:

            overrides:'segment_override_dict' = {}
            _collect_modified_segments(self, overrides)

            for raw_segment in raw_segments:

                # A modified segment merges its assignments over the wire data.
                raw_segment_id = id(raw_segment)

                if override := overrides.get(raw_segment_id):
                    raw_segment = override.to_raw()

                line = self._serialize_segment(raw_segment, separators)
                lines.append(line)

            out = '\n'.join(lines)
            return out

        # .. a built message walks its declared attributes in declaration order.
        message_class = type(self)

        for descriptor in _declared_attr_descriptors(message_class):
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
