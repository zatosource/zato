# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Callable, NamedTuple

# Project
from model.facility import Operation_Delete, Operation_Insert, Operation_Update

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from adapter_records.records_writer import fieldvalues, RecordsWriter
    from model.facility import FacilityReferences, ReferenceIDs
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

collect_ids_func       = Callable[['anylist'], 'ReferenceIDs']
patient_reference_func = Callable[['any_', 'FacilityReferences'], int]
field_values_func      = Callable[['any_', 'FacilityReferences'], 'fieldvalues']

# ################################################################################################################################
# ################################################################################################################################

class SourceRules(NamedTuple):
    """ What one source contributes to the sync - which IDs its changes point at, which patient a change belongs to
    and what the fields of its section are to hold.
    """
    section_name:          'str'
    collect_reference_ids: 'collect_ids_func'
    patient_reference:     'patient_reference_func'
    field_values:          'field_values_func'

# ################################################################################################################################
# ################################################################################################################################

def apply_change(writer:'RecordsWriter', rules:'SourceRules', change:'any_', references:'FacilityReferences') -> 'None':
    """ Brings the target up to date with one change - a deletion removes the section the source row had,
    anything else creates the section if it is not there yet and writes the current values into its fields.
    """
    section_id = writer.get_section_id(change.source_id)

    if change.operation == Operation_Delete:

        # A row deleted before it was ever synced leaves nothing to remove.
        if section_id is not None:
            writer.delete_section(change.source_id, section_id)

    elif change.operation in (Operation_Insert, Operation_Update):

        patient_reference = rules.patient_reference(change, references)
        values = rules.field_values(change, references)

        if section_id is None:
            section_id = writer.create_section(change.source_id, patient_reference)
            writer.save_fields(section_id, patient_reference, values, change.changed_at)

        # An existing section also loses the fields the values no longer have.
        else:
            writer.save_fields(section_id, patient_reference, values, change.changed_at)
            writer.remove_other_fields(section_id, values)

    else:
        raise Exception(f'Unknown operation -> {change.operation} -> {change.source_id}')

# ################################################################################################################################
# ################################################################################################################################
