# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intset, strnone
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

class SegmentAccessor:
    """ Positional read access to the fields of one raw parsed segment.

    The underlying data is the Rust parser's structure: each field is a list
    of repetitions, each repetition a list of components, each component a list
    of subcomponents (plain strings). Positions are the 1-based HL7 field numbers,
    including the MSH offset - MSH-2 lives at raw index 0.
    """

    def __init__(self, raw_segment:'any_') -> 'None':
        self.segment_id:'str' = raw_segment.segment_id
        self._fields = raw_segment.fields
        self._index_offset = 2 if self.segment_id == 'MSH' else 1

# ################################################################################################################################

    def repetitions(self, position:'int') -> 'anylist':
        """ Returns all the repetitions of a field, each a list of components. Empty list when the field is absent.
        """
        index = position - self._index_offset
        if index < 0:
            return []

        field_count = len(self._fields)
        if index >= field_count:
            return []

        # Repetitions that carry no data at all are of no interest to any mapper
        out:'anylist' = []

        for repetition in self._fields[index]:
            if _repetition_has_data(repetition):
                out.append(repetition)

        return out

# ################################################################################################################################

    def first(self, position:'int') -> 'anylist':
        """ Returns the first repetition of a field as a list of components. Empty list when the field is absent.
        """
        repetitions = self.repetitions(position)
        if repetitions:

            out = repetitions[0]
            return out

        return []

# ################################################################################################################################

    def value(self, position:'int') -> 'strnone':
        """ Returns the first subcomponent of the first component of the first repetition, or None.
        """
        repetition = self.first(position)

        out = component_value(repetition, 1)
        return out

# ################################################################################################################################

    def component(self, position:'int', component_position:'int') -> 'strnone':
        """ Returns one component's value from the first repetition of a field, or None.
        """
        repetition = self.first(position)

        out = component_value(repetition, component_position)
        return out

# ################################################################################################################################

    def populated_positions(self) -> 'intset':
        """ Returns the 1-based positions of all the fields that carry any data.
        """
        out:'intset' = set()

        for index, field_data in enumerate(self._fields):
            for repetition in field_data:
                if _repetition_has_data(repetition):
                    out.add(index + self._index_offset)
                    break

        return out

# ################################################################################################################################
# ################################################################################################################################

def _repetition_has_data(repetition:'anylist') -> 'bool':
    """ Tells whether any component of a repetition carries a non-empty subcomponent.
    """
    for component in repetition:
        for subcomponent in component:
            if subcomponent:
                return True

    return False

# ################################################################################################################################

def component_value(repetition:'anylist', position:'int') -> 'strnone':
    """ Returns the first subcomponent of the component at a 1-based position, or None when empty or absent.
    """
    index = position - 1
    component_count = len(repetition)

    if index >= component_count:
        return None

    component = repetition[index]
    if not component:
        return None

    first_subcomponent = component[0]
    if first_subcomponent:

        out = first_subcomponent
        return out

    return None

# ################################################################################################################################

def subcomponent_value(repetition:'anylist', position:'int', sub_position:'int') -> 'strnone':
    """ Returns one subcomponent of the component at a 1-based position, or None when empty or absent.
    """
    index = position - 1
    component_count = len(repetition)

    if index >= component_count:
        return None

    component = repetition[index]
    sub_index = sub_position - 1
    subcomponent_count = len(component)

    if sub_index >= subcomponent_count:
        return None

    subcomponent = component[sub_index]
    if subcomponent:

        out = subcomponent
        return out

    return None

# ################################################################################################################################
# ################################################################################################################################
