# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from typing import NamedTuple

# oracledb
from oracledb import DB_TYPE_TIMESTAMP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist, dtnone, intnone, strnone, strtuple

    from _schema import Schema

# ################################################################################################################################
# ################################################################################################################################

section_list = list['SectionRow']
field_list   = list['FieldRow']
map_list     = list['MapRow']
field_dict   = dict[str, 'strnone']

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Who a log row says made the change.
    Username = 'facility.app'

    # The steps the fault plan knows.
    Step_Section_Create    = 'section_create'
    Step_Field_Save        = 'field_save'
    Step_Map_Insert        = 'map_insert'
    Step_Checkpoint_Update = 'checkpoint_update'

    # A moment every test builds its timestamps from.
    Base_Time = datetime(2026, 3, 10, 9, 0, 0)

    # The service that runs one sync.
    Sync_Service = 'facility.sync.run'

    # The users the helpers connect as.
    Facility_Owner = 'FACILITY'
    Records_Owner  = 'RECORDS'
    Sync_Writer    = 'SYNC_WRITER'
    Sync_Faults    = 'SYNC_FAULTS'

# ################################################################################################################################
# ################################################################################################################################

class SectionRow(NamedTuple):
    section_id:      'int'
    patient:         'int'
    sequence_number: 'int'

class FieldRow(NamedTuple):
    name:        'str'
    answer:      'strnone'
    answer_text: 'strnone'
    answered_at: 'dtnone'

class MapRow(NamedTuple):
    source_table: 'str'
    source_id:    'int'
    section_id:   'int'

# ################################################################################################################################
# ################################################################################################################################

_insert_patient   = 'insert into PATIENTS (ID, REFERENCE_ID, FULL_NAME) values (:id, :reference_id, :full_name)'
_insert_staff     = 'insert into STAFF (ID, REFERENCE_ID, FULL_NAME) values (:id, :reference_id, :full_name)'
_insert_condition = 'insert into CONDITION_CODES (ID, CONDITION_CODE, CONDITION_TITLE) values (:id, :code, :title)'
_insert_treatment = 'insert into TREATMENTS (ID, PATIENT_ID) values (:id, :patient_id)'
_delete_patient   = 'delete from PATIENTS where ID = :id'

_insert_log_treatment = """
insert into LOG_TREATMENTS (
    "TIMESTAMP", USERNAME, OPERATION, ID, PATIENT_ID, STAFF_ID, CONDITION_ID,
    START_DATE, END_DATE, CLARIFICATION, ATTENTION_VALUE_ID
) values (
    :changed_at, :username, :operation, :id, :patient_id, :staff_id, :condition_id,
    :start_date, :end_date, :clarification, :attention_value_id
)
"""

_insert_log_consult_note = """
insert into LOG_CONSULT_NOTES (
    "TIMESTAMP", USERNAME, OPERATION, ID, STAFF_ID, CREATED_DATE, MODIFIED_DATE, TREATMENT_ID,
    COMPLAINT_CODE_ID, COMPLAINT_NOTE, FINDINGS_NOTE, ASSESSMENT_CODE_ID, ASSESSMENT_NOTE, PLAN_NOTE, PROGRESS_NOTE
) values (
    :changed_at, :username, :operation, :id, :staff_id, :created_date, :modified_date, :treatment_id,
    :complaint_code_id, :complaint_note, :findings_note, :assessment_code_id, :assessment_note, :plan_note, :progress_note
)
"""

_select_sections = """
select ps.PS_ID, ps.PS_PATIENT, ps.PS_SEQUENCE_NO
from PATIENT_SECTION ps
join SECTION_DEF sd on sd.SD_ID = ps.PS_SD_ID
where sd.SD_NAME = :section_name
order by ps.PS_ID
"""

_select_fields = """
select fd.FD_NAME, pf.PF_ANSWER, pf.PF_ANSWER_TEXT, pf.PF_ANSWERED_AT
from PATIENT_FIELD pf
join FIELD_DEF fd on fd.FD_ID = pf.PF_FD_ID
where pf.PF_PS_ID = :section_id
order by pf.PF_ID
"""

_count_sections = 'select count(*) from PATIENT_SECTION'
_count_fields   = 'select count(*) from PATIENT_FIELD'

_insert_checkpoint = 'insert into SYNC_CHECKPOINT (SOURCE, LAST_TS) values (:source, :last_ts)'
_select_checkpoint = 'select LAST_TS from SYNC_CHECKPOINT where SOURCE = :source'
_select_map        = 'select SOURCE_TABLE, SOURCE_ID, PS_ID from SYNC_ID_MAP order by SOURCE_TABLE, SOURCE_ID'

# The parameters of each statement that go into TIMESTAMP columns.
_treatment_timestamps    = ('changed_at',)
_consult_note_timestamps = ('changed_at', 'created_date', 'modified_date')
_checkpoint_timestamps   = ('last_ts',)

_set_raise = 'update FAULT_PLAN set NEEDS_RAISE = 1 where STEP = :step'
_set_sleep = 'update FAULT_PLAN set SLEEP_SECONDS = :seconds where STEP = :step'
_clear     = 'update FAULT_PLAN set NEEDS_RAISE = 0, SLEEP_SECONDS = 0'

# ################################################################################################################################
# ################################################################################################################################

class _Database:
    """ One connection as one user.
    """

    username = ''

    def __init__(self, schema:'Schema') -> 'None':
        self.schema = schema
        self.connection = schema.connect(self.username)

# ################################################################################################################################

    def execute(self, statement:'str', parameters:'anydict', timestamp_names:'strtuple'=()) -> 'None':
        """ Runs one statement, binding the named parameters as TIMESTAMP.
        """
        bind_types:'anydict' = {}

        for name in timestamp_names:
            bind_types[name] = DB_TYPE_TIMESTAMP

        with self.connection.cursor() as cursor:

            if bind_types:
                _ = cursor.setinputsizes(**bind_types)

            cursor.execute(statement, parameters)

# ################################################################################################################################

    def fetch_all(self, statement:'str', parameters:'anydict') -> 'anylist':
        with self.connection.cursor() as cursor:
            cursor.execute(statement, parameters)
            out = cursor.fetchall()

        return out

# ################################################################################################################################

    def fetch_value(self, statement:'str', parameters:'anydict') -> 'any_':
        with self.connection.cursor() as cursor:
            cursor.execute(statement, parameters)
            row = cursor.fetchone()

        if row is None:
            out = None
        else:
            out = row[0]

        return out

# ################################################################################################################################

    def commit(self) -> 'None':
        self.connection.commit()

# ################################################################################################################################

    def close(self) -> 'None':
        self.connection.close()

# ################################################################################################################################
# ################################################################################################################################

class FacilityDatabase(_Database):
    """ The source database as its owner - what a test fills before a run.
    """

    username = ModuleCtx.Facility_Owner

    def add_patient(self, patient_id:'int', reference_id:'int', full_name:'str') -> 'None':
        self.execute(_insert_patient, {'id': patient_id, 'reference_id': reference_id, 'full_name': full_name})

# ################################################################################################################################

    def delete_patient(self, patient_id:'int') -> 'None':
        self.execute(_delete_patient, {'id': patient_id})

# ################################################################################################################################

    def add_staff(self, staff_id:'int', reference_id:'int', full_name:'str') -> 'None':
        self.execute(_insert_staff, {'id': staff_id, 'reference_id': reference_id, 'full_name': full_name})

# ################################################################################################################################

    def add_condition(self, condition_id:'int', code:'str', title:'str') -> 'None':
        self.execute(_insert_condition, {'id': condition_id, 'code': code, 'title': title})

# ################################################################################################################################

    def add_treatment(self, treatment_id:'int', patient_id:'int') -> 'None':
        self.execute(_insert_treatment, {'id': treatment_id, 'patient_id': patient_id})

# ################################################################################################################################

    def log_treatment(
        self,
        changed_at:'datetime',
        operation:'str',
        treatment_id:'int',
        *,
        patient_id:'intnone' = None,
        staff_id:'intnone' = None,
        condition_id:'intnone' = None,
        start_date:'dtnone' = None,
        end_date:'dtnone' = None,
        clarification:'strnone' = None,
        attention_value_id:'intnone' = None,
        ) -> 'None':
        """ One row in the treatments log.
        """
        parameters = {
            'changed_at':         changed_at,
            'username':           ModuleCtx.Username,
            'operation':          operation,
            'id':                 treatment_id,
            'patient_id':         patient_id,
            'staff_id':           staff_id,
            'condition_id':       condition_id,
            'start_date':         start_date,
            'end_date':           end_date,
            'clarification':      clarification,
            'attention_value_id': attention_value_id,
        }

        self.execute(_insert_log_treatment, parameters, _treatment_timestamps)

# ################################################################################################################################

    def log_consult_note(
        self,
        changed_at:'datetime',
        operation:'str',
        consult_note_id:'int',
        *,
        staff_id:'intnone' = None,
        created_date:'dtnone' = None,
        modified_date:'dtnone' = None,
        treatment_id:'intnone' = None,
        complaint_code_id:'intnone' = None,
        complaint_note:'strnone' = None,
        findings_note:'strnone' = None,
        assessment_code_id:'intnone' = None,
        assessment_note:'strnone' = None,
        plan_note:'strnone' = None,
        progress_note:'strnone' = None,
        ) -> 'None':
        """ One row in the consult notes log.
        """
        parameters = {
            'changed_at':         changed_at,
            'username':           ModuleCtx.Username,
            'operation':          operation,
            'id':                 consult_note_id,
            'staff_id':           staff_id,
            'created_date':       created_date,
            'modified_date':      modified_date,
            'treatment_id':       treatment_id,
            'complaint_code_id':  complaint_code_id,
            'complaint_note':     complaint_note,
            'findings_note':      findings_note,
            'assessment_code_id': assessment_code_id,
            'assessment_note':    assessment_note,
            'plan_note':          plan_note,
            'progress_note':      progress_note,
        }

        self.execute(_insert_log_consult_note, parameters, _consult_note_timestamps)

# ################################################################################################################################
# ################################################################################################################################

class RecordsDatabase(_Database):
    """ The target database as its owner - what a test reads back after a run.
    """

    username = ModuleCtx.Records_Owner

    def sections(self, section_name:'str') -> 'section_list':
        out:'section_list' = []

        for section_id, patient, sequence_number in self.fetch_all(_select_sections, {'section_name': section_name}):
            row = SectionRow(section_id, patient, sequence_number)
            out.append(row)

        return out

# ################################################################################################################################

    def field_rows(self, section_id:'int') -> 'field_list':
        out:'field_list' = []

        for name, answer, answer_text, answered_at in self.fetch_all(_select_fields, {'section_id': section_id}):
            row = FieldRow(name, answer, answer_text, answered_at)
            out.append(row)

        return out

# ################################################################################################################################

    def fields(self, section_id:'int') -> 'field_dict':
        """ The fields of one section, name to answer.
        """
        out:'field_dict' = {}

        for row in self.field_rows(section_id):
            out[row.name] = row.answer

        return out

# ################################################################################################################################

    def count_sections(self) -> 'int':
        out = self.fetch_value(_count_sections, {})
        return out

# ################################################################################################################################

    def count_fields(self) -> 'int':
        out = self.fetch_value(_count_fields, {})
        return out

# ################################################################################################################################
# ################################################################################################################################

class SyncDatabase(_Database):
    """ The mapping and the checkpoint, as the user the writer connection has.
    """

    username = ModuleCtx.Sync_Writer

    def seed_checkpoint(self, source:'str', last_timestamp:'datetime') -> 'None':
        """ The checkpoint row a source starts from.
        """
        self.execute(_insert_checkpoint, {'source': source, 'last_ts': last_timestamp}, _checkpoint_timestamps)
        self.commit()

# ################################################################################################################################

    def checkpoint(self, source:'str') -> 'dtnone':
        out = self.fetch_value(_select_checkpoint, {'source': source})
        return out

# ################################################################################################################################

    def map_rows(self) -> 'map_list':
        out:'map_list' = []

        for source_table, source_id, section_id in self.fetch_all(_select_map, {}):
            row = MapRow(source_table, source_id, section_id)
            out.append(row)

        return out

# ################################################################################################################################
# ################################################################################################################################

class FaultPlan(_Database):
    """ The faults the package and the triggers raise, or the sleep they take, at a named step.
    """

    username = ModuleCtx.Sync_Faults

    def raise_at(self, step:'str') -> 'None':
        self.execute(_set_raise, {'step': step})
        self.commit()

# ################################################################################################################################

    def sleep_at(self, step:'str', seconds:'int') -> 'None':
        self.execute(_set_sleep, {'step': step, 'seconds': seconds})
        self.commit()

# ################################################################################################################################

    def clear(self) -> 'None':
        self.execute(_clear, {})
        self.commit()

# ################################################################################################################################
# ################################################################################################################################

# The references add_references creates.
Patient_ID        = 101
Patient_Reference = 90101
Staff_ID          = 201
Staff_Reference   = 90201
Condition_ID      = 301
Condition_Code    = 'R05'
Condition_Title   = 'Cough'
Treatment_ID      = 5001

# The consult note most tests log against Treatment_ID.
Consult_Note_ID = 7001

# The fields every synced treatment and consult note carries.
Field_Treatment_ID      = 'TREATMENT_ID'
Field_Treatment_Patient = 'TREATMENT_PATIENT'
Field_Consult_Note_ID   = 'CONSULT_NOTE_ID'

# ################################################################################################################################
# ################################################################################################################################

def run_sync(client:'AdminClient', source:'str') -> 'anydict':
    """ One run of the sync for one source.
    """
    out = client.invoke(ModuleCtx.Sync_Service, {'source': source})
    return out

# ################################################################################################################################

def run_sync_failing(client:'AdminClient', source:'str') -> 'str':
    """ One run that is expected to fail - what the server said about it.
    """
    try:
        _ = run_sync(client, source)
    except Exception as e:
        out = str(e)
    else:
        raise Exception(f'Sync of {source} was expected to fail')

    return out

# ################################################################################################################################

def add_references(facility:'FacilityDatabase') -> 'None':
    """ The patient, the staff member, the condition and the treatment the tests share.
    """
    facility.add_patient(Patient_ID, Patient_Reference, 'John Smith')
    facility.add_staff(Staff_ID, Staff_Reference, 'Anna Miller')
    facility.add_condition(Condition_ID, Condition_Code, Condition_Title)
    facility.add_treatment(Treatment_ID, Patient_ID)
    facility.commit()

# ################################################################################################################################
# ################################################################################################################################
