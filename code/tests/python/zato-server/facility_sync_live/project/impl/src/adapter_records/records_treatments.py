# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Project
from adapter_records.records_apply import SourceRules
from model.facility import ReferenceIDs, Section_Treatments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from adapter_records.records_writer import fieldvalues
    from model.facility import FacilityReferences, treatment_list, TreatmentChange

# ################################################################################################################################
# ################################################################################################################################

# The fields of the treatments section, as FIELD_DEF names them.
Field_ID              = 'TREATMENT_ID'
Field_Patient         = 'TREATMENT_PATIENT'
Field_Staff           = 'TREATMENT_STAFF'
Field_Condition_Code  = 'TREATMENT_CONDITION_CODE'
Field_Condition_Title = 'TREATMENT_CONDITION_TITLE'
Field_Start_Date      = 'TREATMENT_START_DATE'
Field_End_Date        = 'TREATMENT_END_DATE'
Field_Clarification   = 'TREATMENT_CLARIFICATION'
Field_Attention_Value = 'TREATMENT_ATTENTION_VALUE'

# The word the target stores for each attention value.
Attention_Labels = {
    1: 'Low',
    2: 'High',
    3: 'Inactive',
}

# ################################################################################################################################
# ################################################################################################################################

def collect_reference_ids(changes:'treatment_list') -> 'ReferenceIDs':
    out = ReferenceIDs()
    out.patient_ids = set()
    out.staff_ids = set()
    out.condition_ids = set()
    out.treatment_ids = set()

    for change in changes:

        if change.patient_id is not None:
            out.patient_ids.add(change.patient_id)

        if change.staff_id is not None:
            out.staff_ids.add(change.staff_id)

        if change.condition_id is not None:
            out.condition_ids.add(change.condition_id)

    return out

# ################################################################################################################################

def patient_reference(change:'TreatmentChange', references:'FacilityReferences') -> 'int':
    """ The reference the target knows the treatment's patient by.
    """
    if change.patient_id not in references.patients:
        raise Exception(f'Patient not found for treatment -> {change.source_id} -> {change.patient_id}')

    out = references.patients[change.patient_id]
    return out

# ################################################################################################################################

def field_values(change:'TreatmentChange', references:'FacilityReferences') -> 'fieldvalues':
    """ What each field of the treatment's section is to hold. A source value that is NULL has no field at all.
    """
    out:'fieldvalues' = {}

    reference = patient_reference(change, references)

    out[Field_ID] = str(change.source_id)
    out[Field_Patient] = str(reference)

    if change.staff_id is not None:

        if change.staff_id not in references.staff:
            raise Exception(f'Staff not found for treatment -> {change.source_id} -> {change.staff_id}')

        staff_reference = references.staff[change.staff_id]
        out[Field_Staff] = str(staff_reference)

    if change.condition_id is not None:

        if change.condition_id not in references.conditions:
            raise Exception(f'Condition not found for treatment -> {change.source_id} -> {change.condition_id}')

        condition = references.conditions[change.condition_id]
        out[Field_Condition_Code] = condition.code
        out[Field_Condition_Title] = condition.title

    if change.start_date is not None:
        out[Field_Start_Date] = change.start_date.isoformat()

    if change.end_date is not None:
        out[Field_End_Date] = change.end_date.isoformat()

    if change.clarification is not None:
        out[Field_Clarification] = change.clarification

    if change.attention_value_id is not None:
        out[Field_Attention_Value] = Attention_Labels[change.attention_value_id]

    return out

# ################################################################################################################################
# ################################################################################################################################

Treatment_Rules = SourceRules(Section_Treatments, collect_reference_ids, patient_reference, field_values)

# ################################################################################################################################
# ################################################################################################################################
