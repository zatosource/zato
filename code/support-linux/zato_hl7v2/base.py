# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import json

from enum import Enum
from typing import NamedTuple

# Zato
from zato_hl7v2.registry import register_component, register_field, register_segment, resolve_component, resolve_field
from zato_hl7v2_rs import serialize as _rust_serialize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

_datatype_classes:'strtypedict' = {}
_segment_classes:'strtypedict'  = {}

# Deferred reference to zato_hl7v2.v2_9 module, populated on first use
# to avoid circular imports (v2_9 imports from base, base cannot import v2_9 at module level).
_v2_9_module:'any_' = None

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases following the zato.common.typing_ naming convention
any_          = 'Any'
intnone       = 'Optional[int]'
strnone       = 'Optional[str]'
strtypedict   = dict[str, type]
stranydict    = dict[str, 'Any']
intstrdict    = dict[int, str]
strlist       = list[str]
strlistlist   = list[list[str]]
anylist       = list['Any']

# ################################################################################################################################
# ################################################################################################################################

class ResolvedField(NamedTuple):
    """ Result of resolving a field reference to its position and datatype.
    """
    position:'intnone'
    datatype:'strnone'

# ################################################################################################################################
# ################################################################################################################################

def _sort_by_position(component:'HL7Component') -> 'int':
    """ Sort key for HL7Component instances by their position.
    """
    out = component.position
    return out

# ################################################################################################################################

def _get_v2_9_module() -> 'any_':
    """ Return the zato_hl7v2.v2_9 module, importing it on first call.
    """
    global _v2_9_module

    if _v2_9_module is None:
        import zato_hl7v2.v2_9 as module
        _v2_9_module = module

    out = _v2_9_module
    return out

# ################################################################################################################################

def _extract_single_value(data:'strlist') -> 'any_':
    """ Given a list of subcomponents, return the scalar if exactly one element, otherwise the list.
    """
    if data:
        element_count = len(data)
        if element_count == 1:
            return data[0]

    return data

# ################################################################################################################################
# ################################################################################################################################

def _flatten_raw_field(repetitions:'list') -> 'any_':
    """ Flatten a single raw field from the 4D Rust structure into a Python-friendly value.

    The Rust parser stores each field as repetitions -> components -> subcomponents.
    A simple scalar field like "ABC" is stored as [[["ABC"]]].
    A field with components like "A^B" is stored as [[["A"], ["B"]]].
    A repeating field like "A~B" is stored as [[["A"]], [["B"]]].
    This function collapses trivial nesting so that simple fields become plain strings.
    """

    # Build a flat value for each repetition ..
    rep_values:'anylist' = []

    for components in repetitions:

        # Each component is a list of subcomponents ..
        comp_values:'strlist' = []
        for subcomponents in components:
            flat_subcomp = _extract_single_value(subcomponents)
            comp_values.append(flat_subcomp)

        # .. a single-component field collapses to a string ..
        comp_count = len(comp_values)
        has_single_component = comp_count == 1
        if has_single_component:
            rep_values.append(comp_values[0])
        else:
            rep_values.append(comp_values)

    # A single-repetition field collapses to its value ..
    rep_count = len(rep_values)
    has_single_rep = rep_count == 1

    if has_single_rep:
        out = rep_values[0]
    else:
        out = rep_values

    return out

# ################################################################################################################################
# ################################################################################################################################

def _extra_segment_to_dict(raw_segment:'any_') -> 'stranydict':
    """ Convert a raw extra segment (Z-segment or unexpected trailing segment) to a dict.

    Extra segments have no Python class definition, so we build the dict
    from the raw field data using positional keys like zbe_1, zbe_2, etc.
    """
    segment_id = raw_segment.segment_id
    segment_id_lower = segment_id.lower()

    out:'stranydict' = {'_segment_id': segment_id}

    # Walk through each field and flatten its nested structure ..
    for field_index, field_reps in enumerate(raw_segment.fields):
        field_position = field_index + 1
        field_key = f'{segment_id_lower}_{field_position}'
        field_value = _flatten_raw_field(field_reps)
        out[field_key] = field_value

    return out

# ################################################################################################################################
# ################################################################################################################################

class Usage(str, Enum):
    """ HL7 field usage indicator - required or optional.
    """
    REQUIRED = 'R'
    OPTIONAL = 'O'

# ################################################################################################################################
# ################################################################################################################################

class HL7RepeatableList(list):
    """ List subclass that delegates attribute access to the first element.
    """

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':
        if not self:
            raise AttributeError(f'Empty list has no attribute {name!r}')

        out = getattr(self[0], name)
        return out

# ################################################################################################################################

    def __setattr__(self, name:'str', value:'any_') -> 'None':
        if not self:
            raise AttributeError(f'Empty list, cannot set {name!r}')
        setattr(self[0], name, value)

# ################################################################################################################################
# ################################################################################################################################

class HL7Component:
    """ Descriptor for a single component within an HL7 data type.
    """

    def __init__(self, position:'int') -> 'None':
        self.position = position
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    def _resolve_from_raw_message(self, instance:'any_', parent_message:'any_') -> 'any_':
        """ Walk into the raw Rust message to find this component's value.
        """
        segment_id = instance._parent_segment_id
        if not segment_id:
            return None

        field_index = instance._parent_field_index
        if field_index < 0:
            return None

        raw_message = parent_message._raw_message
        if raw_message is None:
            return None

        # Find the matching segment in the raw message ..
        raw_segment = None

        for item in raw_message.items:
            if hasattr(item, 'segment_id'):
                if item.segment_id == segment_id:
                    raw_segment = item
                    break

        if raw_segment is None:
            return None

        # .. check bounds on field, repetition, and component indices ..
        field_count = len(raw_segment.fields)
        if field_index >= field_count:
            return None

        field_data = raw_segment.fields[field_index]
        repetition_index = instance._parent_repetition_index
        repetition_count = len(field_data)

        if repetition_index >= repetition_count:
            return None

        repetition_data = field_data[repetition_index]
        component_index = self.position - 1
        component_count = len(repetition_data)

        if component_index >= component_count:
            return None

        # .. and return the component data.
        component_data = repetition_data[component_index]

        out = _extract_single_value(component_data)
        return out

# ################################################################################################################################

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        # Try to resolve the value from the parent message's raw data ..
        parent_message = instance._parent_message
        if parent_message is not None:

            out = self._resolve_from_raw_message(instance, parent_message)
            if out is not None:
                return out

        # .. or check the instance dict ..
        if self.attr_name in instance.__dict__:

            out = instance.__dict__[self.attr_name]
            return out

        # .. or use the raw components attached directly to the data type.
        raw = instance._raw_components
        if raw is None:
            return None

        index = self.position - 1
        raw_count = len(raw)
        if index >= raw_count:
            return None

        component_data = raw[index]

        out = _extract_single_value(component_data)
        return out

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'any_') -> 'None':

        instance.__dict__[self.attr_name] = value

        # Propagate the change to the underlying Rust raw message ..
        parent_message = instance._parent_message
        if parent_message is None:
            return

        segment_id = instance._parent_segment_id
        if not segment_id:
            return

        field_index = instance._parent_field_index
        if field_index < 0:
            return

        repetition_index = instance._parent_repetition_index
        component_index = self.position - 1
        raw_message = parent_message._raw_message
        if raw_message is None:
            return

        # .. converting the value to a string for the Rust layer.
        string_value = str(value) if value is not None else ''
        raw_message.set_segment_field(segment_id, field_index, repetition_index, component_index, 0, string_value)

# ################################################################################################################################
# ################################################################################################################################

class HL7Field:
    """ Descriptor for a single field within an HL7 segment.
    """

    def __init__(
        self,
        position:'int',
        datatype:'str',
        usage:'Usage',
        repeatable:'bool' = False,
        table:'strnone' = None,
        ) -> 'None':
        self.position = position
        self.datatype = datatype
        self.usage = usage
        self.repeatable = repeatable
        self.table = table
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name
        if hasattr(owner, '_segment_id'):
            register_field(owner._segment_id, name, self.position, self.datatype)

# ################################################################################################################################

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        cache = instance.__dict__

        # Return the cached value if we already resolved this field ..
        if self.attr_name in cache:

            out = cache[self.attr_name]
            return out

        # .. or try to resolve from the raw segment data ..
        raw_segment = instance._raw_segment
        if raw_segment is None:

            # .. if there is no raw segment, create an empty data type instance.
            datatype_class = _datatype_classes.get(self.datatype)
            if datatype_class is not None:
                datatype_instance = datatype_class()
                cache[self.attr_name] = datatype_instance

                return datatype_instance
            return None

        # MSH-1 is the field separator and is not stored in the Rust
        # parser's fields array, so MSH-2 lives at index 0.
        segment_id = instance._segment_id
        index = self.position - 2 if segment_id == 'MSH' else self.position - 1

        if index < 0:
            return None

        field_count = len(raw_segment.fields)
        if index >= field_count:
            return None

        field_data = raw_segment.fields[index]
        if not field_data:
            return None

        # .. handle repeatable fields as a list ..
        if self.repeatable:
            out = HL7RepeatableList()

            for repetition_index, repetition in enumerate(field_data):
                if repetition:
                    value = self._build_value(repetition, instance, repetition_index)
                    if value is not None:
                        out.append(value)

            cache[self.attr_name] = out

            return out

        # .. or return a single value.
        first_repetition = field_data[0]
        if first_repetition:
            value = self._build_value(first_repetition, instance, 0)
            cache[self.attr_name] = value

            return value

        return None

# ################################################################################################################################

    def _build_value(
        self,
        components:'strlistlist',
        instance:'any_' = None,
        repetition_index:'int' = 0,
        ) -> 'any_':
        """ Build a typed value from raw component data.
        """

        if not components:
            return None

        # A single simple value with one component and one subcomponent - return it directly ..
        first_component = components[0]
        component_count = len(components)
        subcomponent_count = len(first_component)
        has_single_component = component_count == 1
        has_single_subcomponent = subcomponent_count == 1

        if has_single_component:
            if has_single_subcomponent:
                first_subcomponent = first_component[0]
                if first_subcomponent:
                    return first_subcomponent
                return None

        # .. or build a full data type instance with all components ..
        datatype_class = _datatype_classes.get(self.datatype)
        if datatype_class is not None:
            datatype_instance = datatype_class.__new__(datatype_class)  # type: ignore[call-overload]
            datatype_instance._raw_components = components

            # .. wiring up the parent references so the descriptor protocol
            # can propagate reads and writes back to the Rust layer.
            if instance is not None:
                datatype_instance._parent_message = instance._parent_message
                datatype_instance._parent_segment_id = instance._segment_id

                is_msh = instance._segment_id == 'MSH'
                field_index = self.position - 2 if is_msh else self.position - 1
                datatype_instance._parent_field_index = field_index
                datatype_instance._parent_repetition_index = repetition_index

            return datatype_instance

        # .. or return the raw first subcomponent value.
        first_subcomponent = first_component[0]
        if first_subcomponent:
            return first_subcomponent

        return None

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'any_') -> 'None':

        if self.repeatable:
            if value is not None:
                if not isinstance(value, list):
                    value = HL7RepeatableList([value])

        instance.__dict__[self.attr_name] = value

# ################################################################################################################################
# ################################################################################################################################

class HL7SegmentAttr:
    """ Descriptor for a segment reference within a message or group.
    """

    def __init__(
        self,
        segment_id:'str',
        optional:'bool' = False,
        repeatable:'bool' = False,
        ) -> 'None':
        self.segment_id = segment_id
        self.optional = optional
        self.repeatable = repeatable
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        cache = instance.__dict__

        if self.attr_name in cache:

            out = cache[self.attr_name]
            return out

        raw_message = instance._raw_message
        segment_class = _segment_classes.get(self.segment_id)

        if segment_class is None:
            return None

        # No raw message means we are building a message from scratch ..
        if raw_message is None:
            segment = segment_class()
            segment._parent_message = instance
            cache[self.attr_name] = segment

            return segment

        # .. otherwise resolve from raw data.
        if self.repeatable:
            out = HL7RepeatableList()

            for item in raw_message.items:
                if hasattr(item, 'segment_id'):
                    if item.segment_id == self.segment_id:
                        segment = segment_class.__new__(segment_class)  # type: ignore[call-overload]
                        segment._raw_segment = item
                        segment._parent_message = instance
                        out.append(segment)

            cache[self.attr_name] = out

            return out

        for item in raw_message.items:
            if hasattr(item, 'segment_id'):
                if item.segment_id == self.segment_id:
                    segment = segment_class.__new__(segment_class)  # type: ignore[call-overload]
                    segment._raw_segment = item
                    segment._parent_message = instance
                    cache[self.attr_name] = segment

                    return segment

        return None

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'any_') -> 'None':
        instance.__dict__[self.attr_name] = value

# ################################################################################################################################
# ################################################################################################################################

class HL7GroupAttr:
    """ Descriptor for a group reference within a message.
    """

    def __init__(
        self,
        name:'str',
        optional:'bool' = False,
        repeatable:'bool' = False,
        ) -> 'None':
        self.name = name
        self.optional = optional
        self.repeatable = repeatable
        self.attr_name:'str' = ''

# ################################################################################################################################

    def __set_name__(self, owner:'type', name:'str') -> 'None':
        self.attr_name = name

# ################################################################################################################################

    def __get__(self, instance:'any_', owner:'type') -> 'any_':

        if instance is None:
            return self

        cache = instance.__dict__

        if self.attr_name in cache:

            out = cache[self.attr_name]
            return out

        raw_message = instance._raw_message
        if raw_message is None:
            return None

        # Resolve the group from the raw message items ..
        if self.repeatable:
            out = HL7RepeatableList()

            for item in raw_message.items:
                if hasattr(item, 'name'):
                    if item.name == self.name:
                        group = HL7Group()
                        group._raw_group = item
                        out.append(group)

            cache[self.attr_name] = out

            return out

        # .. or find the first matching group.
        for item in raw_message.items:
            if hasattr(item, 'name'):
                if item.name == self.name:
                    group = HL7Group()
                    group._raw_group = item
                    cache[self.attr_name] = group

                    return group

        return None

# ################################################################################################################################

    def __set__(self, instance:'any_', value:'any_') -> 'None':
        instance.__dict__[self.attr_name] = value

# ################################################################################################################################
# ################################################################################################################################

class HL7DataType:
    """ Base class for all HL7 data type definitions.
    """
    _raw_components:'strlistlist' = []  # noqa: RUF012
    _parent_message:'any_'   = None
    _parent_segment_id:'str' = ''
    _parent_field_index:'int' = -1
    _parent_repetition_index:'int' = 0

# ################################################################################################################################

    def __init_subclass__(cls, **kwargs:'any_') -> 'None':
        super().__init_subclass__(**kwargs)
        _datatype_classes[cls.__name__] = cls

        for name in dir(cls):
            attribute = getattr(cls, name, None)
            if isinstance(attribute, HL7Component):
                register_component(cls.__name__, name, attribute.position)

# ################################################################################################################################

    def __init__(self, raw:'strnone' = None, **kwargs:'any_') -> 'None':

        if raw is not None:
            parts = raw.split('^')
            raw_components:'strlistlist' = []

            for part in parts:
                raw_components.append([part])

            self._raw_components = raw_components
        else:
            self._raw_components = []

        for key, value in kwargs.items():
            setattr(self, key, value)

# ################################################################################################################################

    def _resolve_semantic(self, name:'str') -> 'strnone':
        """ Resolve a semantic name to a positional attribute name.
        """
        position = resolve_component(self.__class__.__name__, name)
        if position is None:
            return None

        for attribute_name in dir(self.__class__):
            attribute = getattr(self.__class__, attribute_name, None)
            if isinstance(attribute, HL7Component):
                if attribute.position == position:
                    return attribute_name

        return None

# ################################################################################################################################

    def __getattr__(self, name:'str') -> 'any_':
        if name.startswith('_'):
            raise AttributeError(name)

        positional = self._resolve_semantic(name)
        if positional is not None:
            if positional != name:

                out = getattr(self, positional)
                return out

        raise AttributeError(f'\'{type(self).__name__}\' has no attribute \'{name}\'')

# ################################################################################################################################

    def __setattr__(self, name:'str', value:'any_') -> 'None':

        # Private attributes are set directly ..
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        # .. descriptor attributes are set through the descriptor protocol ..
        owner_class = type(self)
        if hasattr(owner_class, name):
            class_attribute = getattr(owner_class, name)
            if isinstance(class_attribute, HL7Component):
                super().__setattr__(name, value)
                return

        # .. semantic names are resolved to positional names ..
        positional = self._resolve_semantic(name)
        if positional is not None:
            setattr(self, positional, value)
            return

        # .. everything else is set directly.
        super().__setattr__(name, value)

# ################################################################################################################################

    def to_dict(self, include_empty:'bool' = True) -> 'stranydict':
        """ Convert this data type to a dictionary representation.
        """
        out:'stranydict' = {}

        # Walk through all component descriptors on this class ..
        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            if not isinstance(attribute, HL7Component):
                continue

            value = getattr(self, name, None)

            # .. include None entries when requested ..
            if value is None:
                if include_empty:
                    out[name] = None
                continue

            # .. recursively convert nested data types ..
            if isinstance(value, HL7DataType):
                out[name] = value.to_dict(include_empty=include_empty)
            elif isinstance(value, list):
                items:'anylist' = []

                for item in value:
                    if isinstance(item, HL7DataType):
                        items.append(item.to_dict(include_empty=include_empty))
                    else:
                        items.append(item)

                out[name] = items

            # .. or store the scalar value directly.
            else:
                out[name] = value

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone' = None, include_empty:'bool' = True) -> 'str':
        """ Convert this data type to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################

    def serialize(self) -> 'str':
        """ Serialize this data type to ER7 format.
        """

        # Collect all component descriptors ..
        components:'list[HL7Component]' = []

        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            if isinstance(attribute, HL7Component):
                components.append(attribute)

        if not components:
            return ''

        # .. sort them by position ..
        components.sort(key=_sort_by_position)

        # .. and build the output string.
        max_position = components[-1].position
        parts:'strlist' = []

        for position in range(1, max_position + 1):
            value = None

            for component in components:
                if component.position == position:
                    value = getattr(self, component.attr_name, None)
                    break

            string_value = str(value) if value is not None else ''
            parts.append(string_value)

        while parts:
            if parts[-1] == '':
                _ = parts.pop()
            else:
                break

        out = '^'.join(parts)
        return out

# ################################################################################################################################
# ################################################################################################################################

class HL7Segment:
    """ Base class for all HL7 segment definitions.
    """
    _segment_id:'str'  = ''
    _raw_segment:'any_' = None
    _parent_message:'any_' = None

# ################################################################################################################################

    def __init_subclass__(cls, **kwargs:'any_') -> 'None':
        super().__init_subclass__(**kwargs)
        if cls._segment_id:
            _segment_classes[cls._segment_id] = cls
            register_segment(cls._segment_id, cls)

# ################################################################################################################################

    def __init__(self, raw_segment:'any_' = None) -> 'None':
        self._raw_segment = raw_segment

# ################################################################################################################################

    @classmethod
    def from_er7(cls, raw:'str') -> 'HL7Segment':
        """ Parse an ER7-encoded segment string into a segment instance.
        """
        raise NotImplementedError

# ################################################################################################################################

    def serialize(self) -> 'str':
        """ Serialize this segment to ER7 format.
        """

        # If we have raw segment data, serialize from the Rust structure ..
        if self._raw_segment:

            # .. define the HL7 delimiter characters ..
            field_separator        = '|'
            component_separator    = '^'
            repetition_separator   = '~'
            escape_character       = '\\'
            subcomponent_separator = '&'

            # .. start with the segment ID ..
            out = self._segment_id

            # .. and append each field.
            for field_index, field in enumerate(self._raw_segment.fields):
                out += field_separator

                # MSH-1 (encoding characters) is handled specially ..
                if self._segment_id == 'MSH':
                    if field_index == 0:
                        out += f'{component_separator}{repetition_separator}{escape_character}{subcomponent_separator}'
                        continue

                # .. otherwise serialize each repetition ..
                repetition_strings:'strlist' = []

                for repetition in field:

                    # .. joining components within each repetition ..
                    component_strings:'strlist' = []

                    for component in repetition:

                        # .. and subcomponents within each component.
                        subcomponent_strings:'strlist' = []

                        for subcomponent in component:
                            subcomponent_strings.append(subcomponent)

                        joined_subcomponents = subcomponent_separator.join(subcomponent_strings)
                        component_strings.append(joined_subcomponents)

                    joined_components = component_separator.join(component_strings)
                    repetition_strings.append(joined_components)

                joined_repetitions = repetition_separator.join(repetition_strings)
                out += joined_repetitions

            return out

        # .. or serialize from the dict-based representation.
        out = self._serialize_from_dict()
        return out

# ################################################################################################################################

    def _serialize_from_dict(self) -> 'str':
        """ Serialize this segment from its Python-side field values.
        """
        # Collect serialized values keyed by field position ..
        fields_by_position:'intstrdict' = {}

        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            if isinstance(attribute, HL7Field):
                value = self.__dict__.get(attribute.attr_name)
                if value is not None:
                    if isinstance(value, HL7DataType):
                        fields_by_position[attribute.position] = value.serialize()
                    elif isinstance(value, str):
                        fields_by_position[attribute.position] = value
                    elif isinstance(value, list):
                        parts:'strlist' = []

                        for item in value:
                            if isinstance(item, HL7DataType):
                                parts.append(item.serialize())
                            else:
                                parts.append(str(item))

                        fields_by_position[attribute.position] = '~'.join(parts)
                    else:
                        fields_by_position[attribute.position] = str(value)

        if not fields_by_position:
            return ''

        # .. build the output parts starting with the segment ID ..
        max_position = max(fields_by_position.keys())
        parts = [self._segment_id]

        # .. MSH needs the encoding characters appended first ..
        if self._segment_id == 'MSH':
            parts.append('^~\\&')

        # .. then fill in each field position up to the maximum.
        start_position = 1 if self._segment_id != 'MSH' else 2

        for position in range(start_position, max_position + 1):
            parts.append(fields_by_position.get(position, ''))

        out = '|'.join(parts)
        return out

# ################################################################################################################################

    to_hl7 = serialize
    to_er7 = serialize

# ################################################################################################################################

    def to_dict(self, include_empty:'bool' = True) -> 'stranydict':
        """ Convert this segment to a dictionary representation.
        """
        out:'stranydict' = {'_segment_id': self._segment_id}

        # Walk through all field descriptors on this class ..
        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            if not isinstance(attribute, HL7Field):
                continue

            value = getattr(self, name, None)

            # .. include None entries when requested ..
            if value is None:
                if include_empty:
                    out[name] = None
                continue

            # .. recursively convert nested data types ..
            if isinstance(value, HL7DataType):
                out[name] = value.to_dict(include_empty=include_empty)
            elif isinstance(value, list):
                items:'anylist' = []

                for item in value:
                    if isinstance(item, HL7DataType):
                        items.append(item.to_dict(include_empty=include_empty))
                    else:
                        items.append(item)

                out[name] = items

            # .. or store the scalar value directly.
            else:
                out[name] = value

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone' = None, include_empty:'bool' = True) -> 'str':
        """ Convert this segment to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################
# ################################################################################################################################

class HL7Group:
    """ Base class for HL7 message groups.
    """
    _group_name:'str' = ''
    _raw_group:'any_'  = None

# ################################################################################################################################

    def serialize(self) -> 'str':
        """ Serialize this group to ER7 format.
        """
        if self._raw_group:

            out = _rust_serialize(self._raw_group)  # type: ignore[no-any-return]
            return out

        return ''

# ################################################################################################################################

    to_hl7 = serialize
    to_er7 = serialize

# ################################################################################################################################

    def to_dict(self, include_empty:'bool' = True) -> 'stranydict':
        """ Convert this group to a dictionary representation.
        """
        out:'stranydict' = {'_group_name': self._group_name}

        # Collect serialized segments from the raw group ..
        if self._raw_group:
            segments:'anylist' = []

            for item in self._raw_group.items:
                if hasattr(item, 'segment_id'):
                    segment_class = _segment_classes.get(item.segment_id)
                    if segment_class:
                        segment = segment_class.__new__(segment_class)  # type: ignore[call-overload]
                        segment._raw_segment = item
                        segments.append(segment.to_dict(include_empty=include_empty))

            out['segments'] = segments

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone' = None, include_empty:'bool' = True) -> 'str':
        """ Convert this group to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################
# ################################################################################################################################

class HL7Message:
    """ Base class for all HL7 message definitions.
    """
    _structure_id:'str'       = ''
    _registry:'strtypedict'  = {}  # noqa: RUF012
    _raw_message:'any_'        = None

# ################################################################################################################################

    def __init_subclass__(cls, **kwargs:'any_') -> 'None':
        super().__init_subclass__(**kwargs)
        if cls._structure_id:
            HL7Message._registry[cls._structure_id] = cls

# ################################################################################################################################

    @classmethod
    def parse(cls, raw:'str') -> 'HL7Message':
        """ Parse a raw ER7 string into a typed HL7 message.
        """
        v2_9 = _get_v2_9_module()

        out = v2_9.parse_message(raw)
        return out

# ################################################################################################################################

    def serialize(self) -> 'str':
        """ Serialize this message to ER7 format.
        """
        v2_9 = _get_v2_9_module()

        out = v2_9.serialize(self)
        return out

# ################################################################################################################################

    to_hl7 = serialize
    to_er7 = serialize

# ################################################################################################################################

    def to_dict(self, include_empty:'bool' = True) -> 'stranydict':
        """ Convert this message to a dictionary representation.
        """
        out:'stranydict' = {'_structure_id': self._structure_id}

        # Walk through all segment and group descriptors on this class ..
        for name in dir(self.__class__):
            attribute = getattr(self.__class__, name)
            is_segment_attribute = isinstance(attribute, HL7SegmentAttr)
            is_group_attribute = isinstance(attribute, HL7GroupAttr)

            if not is_segment_attribute:
                if not is_group_attribute:
                    continue

            value = getattr(self, name, None)

            # .. include None entries when requested ..
            if value is None:
                if include_empty:
                    out[name] = None
                continue

            # .. convert list values recursively ..
            if isinstance(value, list):
                items:'anylist' = []

                for item in value:
                    items.append(item.to_dict(include_empty=include_empty))

                out[name] = items

            # .. or convert a single value.
            else:
                out[name] = value.to_dict(include_empty=include_empty)

        # Append any extra segments (Z-segments or unexpected trailing segments)
        # that the Rust parser captured but that have no Python class definition ..
        raw_message = self._raw_message
        if raw_message is not None:
            extra = raw_message.extra_segments
            extra_count = len(extra)
            has_extra = extra_count > 0
            if has_extra:
                extra_list:'anylist' = []
                for raw_segment in extra:
                    segment_dict = _extra_segment_to_dict(raw_segment)
                    extra_list.append(segment_dict)
                out['_extra_segments'] = extra_list

        return out

# ################################################################################################################################

    def to_json(self, indent:'intnone' = None, include_empty:'bool' = True) -> 'str':
        """ Convert this message to a JSON string.
        """
        dict_data = self.to_dict(include_empty=include_empty)

        out = json.dumps(dict_data, indent=indent)
        return out

# ################################################################################################################################

    def get(self, path:'str') -> 'any_':
        """ Get a value by dotted path (e.g. 'pid.patient_name.family_name').
        """
        out = _get_by_path(self, path)
        return out

# ################################################################################################################################

    def set(self, path:'str', value:'str') -> 'None':
        """ Set a value by dotted path.
        """
        _set_by_path(self, path, value)

# ################################################################################################################################
# ################################################################################################################################

def _get_by_path(message:'HL7Message', path:'str') -> 'any_':
    """ Resolve a dotted path to a value within a parsed HL7 message.
    """

    parts = path.split('.')
    part_count = len(parts)

    if part_count < 2:
        return None

    segment_reference = parts[0]
    field_reference = parts[1]

    # Resolve the segment ..
    segment = _resolve_segment(message, segment_reference)
    if segment is None:
        return None

    # .. extract repetition index if present ..
    repetition_index = None
    if '[' in field_reference:
        field_reference, repetition_part = field_reference.split('[', 1)
        stripped_part = repetition_part.rstrip(']')
        repetition_index = int(stripped_part)

    # .. resolve the field ..
    resolved = _resolve_field(segment, field_reference)
    if resolved.position is None:
        return None

    raw_segment = segment._raw_segment
    if raw_segment is None:
        return None

    segment_id = segment._segment_id
    field_index = resolved.position - 2 if segment_id == 'MSH' else resolved.position - 1

    if field_index < 0:
        return None

    field_count = len(raw_segment.fields)
    if field_index >= field_count:
        return None

    field_data = raw_segment.fields[field_index]
    if not field_data:
        return None

    # .. pick the right repetition ..
    repetition_data = _pick_repetition(field_data, repetition_index)
    if repetition_data is None:
        return None

    # .. return the field-level value if no component was requested ..
    if part_count == 2:

        out = _extract_field_value(repetition_data)
        return out

    # .. resolve the component ..
    component_reference = parts[2]
    if '[' in component_reference:
        component_reference, _ = component_reference.split('[', 1)

    if resolved.datatype is None:
        return None

    component_position = _resolve_component(resolved.datatype, component_reference)
    if component_position is None:
        return None

    component_index = component_position - 1
    repetition_count = len(repetition_data)

    if component_index >= repetition_count:
        return None

    component_data = repetition_data[component_index]
    if not component_data:
        return None

    # .. return the component-level value if no subcomponent was requested ..
    if part_count == 3:
        first_subcomponent = component_data[0]
        if first_subcomponent:
            return first_subcomponent
        return None

    # .. or resolve the subcomponent.
    subcomponent_reference = parts[3]
    subcomponent_position = _resolve_subcomponent(subcomponent_reference)
    if subcomponent_position is None:
        return None

    subcomponent_index = subcomponent_position - 1
    subcomponent_count = len(component_data)

    if subcomponent_index >= subcomponent_count:
        return None

    subcomponent_value = component_data[subcomponent_index]
    if subcomponent_value:
        return subcomponent_value

    return None

# ################################################################################################################################

def _pick_repetition(field_data:'list', repetition_index:'intnone') -> 'any_':
    """ Pick the requested repetition from field data, or the first one if no index given.
    """
    if repetition_index is not None:
        data_count = len(field_data)
        if repetition_index >= data_count:
            return None

        out = field_data[repetition_index]
        return out

    if not field_data:
        return None

    out = field_data[0]
    return out

# ################################################################################################################################

def _extract_field_value(repetition_data:'list') -> 'any_':
    """ Extract the scalar value from the first component and first subcomponent of a repetition.
    """
    if not repetition_data:
        return None

    first_component = repetition_data[0]
    if not first_component:
        return None

    first_subcomponent = first_component[0]
    if first_subcomponent:
        return first_subcomponent

    return None

# ################################################################################################################################

def _resolve_segment(message:'HL7Message', segment_reference:'str') -> 'any_':
    """ Find a segment in a message by reference (segment ID or attribute name).
    """

    # Try to find by segment ID in the raw message items ..
    segment_reference_upper = segment_reference.upper()

    for item in message._raw_message.items:
        if hasattr(item, 'segment_id'):
            if item.segment_id == segment_reference_upper:
                segment_class = _segment_classes.get(segment_reference_upper)
                if segment_class:
                    segment = segment_class.__new__(segment_class)  # type: ignore[call-overload]
                    segment._raw_segment = item
                    segment._parent_message = message

                    return segment

    # .. or look up by attribute name on the message class.
    segment_reference_lower = segment_reference.lower()

    for name in dir(message.__class__):
        attribute = getattr(message.__class__, name)
        if isinstance(attribute, HL7SegmentAttr):
            if name == segment_reference_lower:

                out = getattr(message, name)
                return out

    return None

# ################################################################################################################################

def _resolve_field(segment:'HL7Segment', field_reference:'str') -> 'ResolvedField':
    """ Resolve a field reference to its position and datatype.
    """
    position, datatype = resolve_field(segment._segment_id, field_reference)

    out = ResolvedField(position=position, datatype=datatype)
    return out

# ################################################################################################################################

def _resolve_component(datatype:'str', component_reference:'str') -> 'intnone':
    """ Resolve a component reference to its position within a datatype.
    """
    out = resolve_component(datatype, component_reference)
    return out

# ################################################################################################################################

def _resolve_subcomponent(subcomponent_reference:'str') -> 'intnone':
    """ Resolve a subcomponent reference to its position.
    """
    if subcomponent_reference.isdigit():

        out = int(subcomponent_reference)
        return out

    return None

# ################################################################################################################################

def _set_by_path(message:'HL7Message', path:'str', value:'str') -> 'None':
    """ Set a value by dotted path within a parsed HL7 message.
    """

    parts = path.split('.')
    part_count = len(parts)

    if part_count < 2:
        return

    segment_reference = parts[0]
    field_reference = parts[1]

    # Resolve the target segment ID ..
    segment_id = segment_reference.upper()
    found = False

    for item in message._raw_message.items:
        if hasattr(item, 'segment_id'):
            if item.segment_id == segment_id:
                found = True
                break

    if not found:
        segment_reference_lower = segment_reference.lower()

        for name in dir(message.__class__):
            attribute = getattr(message.__class__, name)
            if isinstance(attribute, HL7SegmentAttr):
                if name == segment_reference_lower:
                    segment_id = attribute.segment_id
                    found = True
                    break

    if not found:
        return

    # .. extract repetition index if present ..
    repetition_index = 0
    if '[' in field_reference:
        field_reference, repetition_part = field_reference.split('[', 1)
        stripped_part = repetition_part.rstrip(']')
        repetition_index = int(stripped_part)

    # .. resolve the field ..
    field_position, field_datatype = resolve_field(segment_id, field_reference)
    if field_position is None:
        return

    field_index = field_position - 2 if segment_id == 'MSH' else field_position - 1

    # .. set at field level if no component was specified ..
    if part_count == 2:
        message._raw_message.set_segment_field(segment_id, field_index, repetition_index, 0, 0, value)
        return

    # .. resolve the component ..
    component_reference = parts[2]
    if '[' in component_reference:
        component_reference, _ = component_reference.split('[', 1)

    if field_datatype is None:
        return

    component_position = _resolve_component(field_datatype, component_reference)
    if component_position is None:
        return

    component_index = component_position - 1

    # .. set at component level if no subcomponent was specified ..
    if part_count == 3:
        message._raw_message.set_segment_field(
            segment_id, field_index, repetition_index, component_index, 0, value)
        return

    # .. or resolve and set at subcomponent level.
    subcomponent_reference = parts[3]
    subcomponent_position = _resolve_subcomponent(subcomponent_reference)
    if subcomponent_position is None:
        return

    subcomponent_index = subcomponent_position - 1
    message._raw_message.set_segment_field(
        segment_id, field_index, repetition_index, component_index, subcomponent_index, value)

# ################################################################################################################################
# ################################################################################################################################
