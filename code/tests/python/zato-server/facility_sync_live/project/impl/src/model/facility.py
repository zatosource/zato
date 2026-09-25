# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dtnone, intnone, intset, strnone

# ################################################################################################################################
# ################################################################################################################################

intintdict     = dict[int, int]
conditiondict  = dict[int, 'ConditionCode']
treatment_list = list['TreatmentChange']
consult_list   = list['ConsultNoteChange']

# ################################################################################################################################
# ################################################################################################################################

# The outgoing SQL connections, as enmasse names them - one to read the source, one to write the target.
Connection_Facility = 'Facility Standby'
Connection_Records  = 'Records Writer'

# The sources the sync runs for - the names of the log tables.
Source_Treatments    = 'LOG_TREATMENTS'
Source_Consult_Notes = 'LOG_CONSULT_NOTES'

# The sections of the target the two sources land in.
Section_Treatments    = 'TREATMENTS'
Section_Consult_Notes = 'CONSULT_NOTES'

# What a log row says happened to its source row.
Operation_Insert = 'I'
Operation_Update = 'U'
Operation_Delete = 'D'

# A run reads from this much before its checkpoint.
Read_Overlap = timedelta(minutes=5)

# ################################################################################################################################
# ################################################################################################################################

def _to_iso(value:'dtnone') -> 'strnone':
    """ A datetime as an ISO string, None as it is.
    """
    if value is None:
        out = None
    else:
        out = value.isoformat()

    return out

# ################################################################################################################################

def _from_iso(value:'strnone') -> 'dtnone':
    """ A datetime out of an ISO string, None as it is.
    """
    if value is None:
        out = None
    else:
        out = datetime.fromisoformat(value)

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TreatmentChange:
    """ One row of the treatments log.
    """

    # When the change was logged and what it was.
    changed_at: 'datetime'
    operation:  'str'

    # The treatment the change is about.
    source_id: 'int'

    # What the treatment pointed at.
    patient_id:   'intnone'
    staff_id:     'intnone'
    condition_id: 'intnone'

    # The treatment's own values.
    start_date:         'dtnone'
    end_date:           'dtnone'
    clarification:      'strnone'
    attention_value_id: 'intnone'

# ################################################################################################################################

    def to_dict(self) -> 'anydict':
        """ The change as a dict that can travel as JSON - timestamps become ISO strings.
        """
        out:'anydict' = {
            'changed_at':         self.changed_at.isoformat(),
            'operation':          self.operation,
            'source_id':          self.source_id,
            'patient_id':         self.patient_id,
            'staff_id':           self.staff_id,
            'condition_id':       self.condition_id,
            'start_date':         _to_iso(self.start_date),
            'end_date':           _to_iso(self.end_date),
            'clarification':      self.clarification,
            'attention_value_id': self.attention_value_id,
        }

        return out

# ################################################################################################################################

    @classmethod
    def from_dict(class_, data:'anydict') -> 'TreatmentChange':
        """ The reverse of to_dict.
        """
        out = class_()
        out.changed_at = datetime.fromisoformat(data['changed_at'])
        out.operation = data['operation']
        out.source_id = data['source_id']
        out.patient_id = data['patient_id']
        out.staff_id = data['staff_id']
        out.condition_id = data['condition_id']
        out.start_date = _from_iso(data['start_date'])
        out.end_date = _from_iso(data['end_date'])
        out.clarification = data['clarification']
        out.attention_value_id = data['attention_value_id']

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ConsultNoteChange:
    """ One row of the consult notes log.
    """

    # When the change was logged and what it was.
    changed_at: 'datetime'
    operation:  'str'

    # The consult note the change is about.
    source_id: 'int'

    # What the note pointed at.
    staff_id:           'intnone'
    treatment_id:       'intnone'
    complaint_code_id:  'intnone'
    assessment_code_id: 'intnone'

    # The note's own values.
    created_date:    'dtnone'
    modified_date:   'dtnone'
    complaint_note:  'strnone'
    findings_note:   'strnone'
    assessment_note: 'strnone'
    plan_note:       'strnone'
    progress_note:   'strnone'

# ################################################################################################################################

    def to_dict(self) -> 'anydict':
        """ The change as a dict that can travel as JSON - timestamps become ISO strings.
        """
        out:'anydict' = {
            'changed_at':         self.changed_at.isoformat(),
            'operation':          self.operation,
            'source_id':          self.source_id,
            'staff_id':           self.staff_id,
            'treatment_id':       self.treatment_id,
            'complaint_code_id':  self.complaint_code_id,
            'assessment_code_id': self.assessment_code_id,
            'created_date':       _to_iso(self.created_date),
            'modified_date':      _to_iso(self.modified_date),
            'complaint_note':     self.complaint_note,
            'findings_note':      self.findings_note,
            'assessment_note':    self.assessment_note,
            'plan_note':          self.plan_note,
            'progress_note':      self.progress_note,
        }

        return out

# ################################################################################################################################

    @classmethod
    def from_dict(class_, data:'anydict') -> 'ConsultNoteChange':
        """ The reverse of to_dict.
        """
        out = class_()
        out.changed_at = datetime.fromisoformat(data['changed_at'])
        out.operation = data['operation']
        out.source_id = data['source_id']
        out.staff_id = data['staff_id']
        out.treatment_id = data['treatment_id']
        out.complaint_code_id = data['complaint_code_id']
        out.assessment_code_id = data['assessment_code_id']
        out.created_date = _from_iso(data['created_date'])
        out.modified_date = _from_iso(data['modified_date'])
        out.complaint_note = data['complaint_note']
        out.findings_note = data['findings_note']
        out.assessment_note = data['assessment_note']
        out.plan_note = data['plan_note']
        out.progress_note = data['progress_note']

        return out

# ################################################################################################################################
# ################################################################################################################################

class ConditionCode(NamedTuple):
    """ A condition as the target names it.
    """
    code:  'str'
    title: 'str'

# ################################################################################################################################

@dataclass(init=False)
class ReferenceIDs:
    """ Everything a batch of changes points at in the current tables.
    """
    patient_ids:   'intset'
    staff_ids:     'intset'
    condition_ids: 'intset'
    treatment_ids: 'intset'

# ################################################################################################################################

@dataclass(init=False)
class FacilityReferences:
    """ What the current tables say about the IDs a batch of changes carries - each ID to what the target needs.
    """

    # A patient's or a staff member's ID to the reference the target knows them by.
    patients: 'intintdict'
    staff:    'intintdict'

    # A condition's ID to its code and title.
    conditions: 'conditiondict'

    # A treatment's ID to the patient it belongs to.
    treatments: 'intintdict'

# ################################################################################################################################

@dataclass(init=False)
class Checkpoint:
    """ Where the sync of one source got to.
    """
    source:         'str'
    last_timestamp: 'datetime'

# ################################################################################################################################
# ################################################################################################################################
