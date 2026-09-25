# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Project
from adapter_records.records_apply import SourceRules
from model.facility import ReferenceIDs, Section_Consult_Notes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from adapter_records.records_writer import fieldvalues
    from model.facility import consult_list, ConsultNoteChange, FacilityReferences

# ################################################################################################################################
# ################################################################################################################################

# The fields of the consult notes section, as FIELD_DEF names them.
Field_ID              = 'CONSULT_NOTE_ID'
Field_Staff           = 'CONSULT_NOTE_STAFF'
Field_Treatment       = 'CONSULT_NOTE_TREATMENT'
Field_Created_Date    = 'CONSULT_NOTE_CREATED_DATE'
Field_Modified_Date   = 'CONSULT_NOTE_MODIFIED_DATE'
Field_Complaint_Code  = 'CONSULT_NOTE_COMPLAINT_CODE'
Field_Complaint_Note  = 'CONSULT_NOTE_COMPLAINT_NOTE'
Field_Findings_Note   = 'CONSULT_NOTE_FINDINGS_NOTE'
Field_Assessment_Code = 'CONSULT_NOTE_ASSESSMENT_CODE'
Field_Assessment_Note = 'CONSULT_NOTE_ASSESSMENT_NOTE'
Field_Plan_Note       = 'CONSULT_NOTE_PLAN_NOTE'
Field_Progress_Note   = 'CONSULT_NOTE_PROGRESS_NOTE'

# ################################################################################################################################
# ################################################################################################################################

def collect_reference_ids(changes:'consult_list') -> 'ReferenceIDs':
    """ The IDs a batch of notes points at.
    """
    out = ReferenceIDs()
    out.patient_ids = set()
    out.staff_ids = set()
    out.condition_ids = set()
    out.treatment_ids = set()

    for change in changes:

        if change.staff_id is not None:
            out.staff_ids.add(change.staff_id)

        if change.complaint_code_id is not None:
            out.condition_ids.add(change.complaint_code_id)

        if change.assessment_code_id is not None:
            out.condition_ids.add(change.assessment_code_id)

        if change.treatment_id is not None:
            out.treatment_ids.add(change.treatment_id)

    return out

# ################################################################################################################################

def patient_reference(change:'ConsultNoteChange', references:'FacilityReferences') -> 'int':
    """ The reference the target knows the note's patient by - the patient is the treatment's.
    """
    if change.treatment_id not in references.treatments:
        raise Exception(f'Treatment not found for consult note -> {change.source_id} -> {change.treatment_id}')

    patient_id = references.treatments[change.treatment_id]

    if patient_id not in references.patients:
        raise Exception(f'Patient not found for consult note -> {change.source_id} -> {patient_id}')

    out = references.patients[patient_id]
    return out

# ################################################################################################################################

def _condition_code(change:'ConsultNoteChange', references:'FacilityReferences', condition_id:'int') -> 'str':
    if condition_id not in references.conditions:
        raise Exception(f'Condition not found for consult note -> {change.source_id} -> {condition_id}')

    condition = references.conditions[condition_id]

    out = condition.code
    return out

# ################################################################################################################################

def field_values(change:'ConsultNoteChange', references:'FacilityReferences') -> 'fieldvalues':
    """ What each field of the note's section is to hold. A source value that is NULL has no field at all.
    """
    out:'fieldvalues' = {}

    out[Field_ID] = str(change.source_id)
    out[Field_Treatment] = str(change.treatment_id)

    if change.staff_id is not None:

        if change.staff_id not in references.staff:
            raise Exception(f'Staff not found for consult note -> {change.source_id} -> {change.staff_id}')

        staff_reference = references.staff[change.staff_id]
        out[Field_Staff] = str(staff_reference)

    if change.created_date is not None:
        out[Field_Created_Date] = change.created_date.isoformat()

    if change.modified_date is not None:
        out[Field_Modified_Date] = change.modified_date.isoformat()

    if change.complaint_code_id is not None:
        out[Field_Complaint_Code] = _condition_code(change, references, change.complaint_code_id)

    if change.assessment_code_id is not None:
        out[Field_Assessment_Code] = _condition_code(change, references, change.assessment_code_id)

    if change.complaint_note is not None:
        out[Field_Complaint_Note] = change.complaint_note

    if change.findings_note is not None:
        out[Field_Findings_Note] = change.findings_note

    if change.assessment_note is not None:
        out[Field_Assessment_Note] = change.assessment_note

    if change.plan_note is not None:
        out[Field_Plan_Note] = change.plan_note

    if change.progress_note is not None:
        out[Field_Progress_Note] = change.progress_note

    return out

# ################################################################################################################################
# ################################################################################################################################

Consult_Note_Rules = SourceRules(Section_Consult_Notes, collect_reference_ids, patient_reference, field_values)

# ################################################################################################################################
# ################################################################################################################################
