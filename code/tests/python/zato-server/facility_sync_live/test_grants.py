# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# oracledb
from oracledb import DatabaseError

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _schema import Schema

# ################################################################################################################################
# ################################################################################################################################

# The users the two outgoing connections log in as.
Standby_User = 'FACILITY_READER'
Writer_User  = 'SYNC_WRITER'

# The codes a refused statement fails with, and the range of per-privilege codes.
Table_Not_Visible       = 942
Insufficient_Privileges = 1031

Missing_Privilege_First = 41900
Missing_Privilege_Last  = 41999

# ################################################################################################################################
# ################################################################################################################################

def _refused_code(schema:'Schema', username:'str', statement:'str') -> 'int':
    """ The error code Oracle refuses a statement with, as the given user.
    """
    connection = schema.connect(username)

    try:
        with connection.cursor() as cursor:
            with pytest.raises(DatabaseError) as raised:
                cursor.execute(statement)

        connection.rollback()

    finally:
        connection.close()

    error = raised.value.args[0]

    out = error.code
    return out

# ################################################################################################################################

def _is_refusal(code:'int') -> 'bool':
    out = False

    if code in (Table_Not_Visible, Insufficient_Privileges):
        out = True

    if Missing_Privilege_First <= code <= Missing_Privilege_Last:
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('statement', [
    'insert into FACILITY.PATIENTS (ID, REFERENCE_ID, FULL_NAME) values (1, 1, \'Test patient\')',
    'update FACILITY.PATIENTS set FULL_NAME = \'Test patient\'',
    'delete from FACILITY.LOG_TREATMENTS',
    'select count(*) from RECORDS.PATIENT_SECTION',
    'select count(*) from SYNC_WRITER.SYNC_CHECKPOINT',
])
def test_standby_connection_cannot_write_anywhere(schema:'Schema', statement:'str') -> 'None':
    code = _refused_code(schema, Standby_User, statement)
    assert _is_refusal(code), code

# ################################################################################################################################

@pytest.mark.parametrize('statement', [
    'select count(*) from FACILITY.PATIENTS',
    'select count(*) from FACILITY.LOG_TREATMENTS',
    'insert into RECORDS.PATIENT_SECTION (PS_ID, PS_PATIENT, PS_SD_ID) values (1, 1, 1)',
    'update RECORDS.PATIENT_FIELD set PF_ANSWER = \'Test answer\'',
    'insert into RECORDS.SECTION_DEF (SD_ID, SD_NAME) values (99, \'TEST_SECTION\')',
])
def test_writer_connection_cannot_read_the_source_or_write_around_the_package(schema:'Schema', statement:'str') -> 'None':
    code = _refused_code(schema, Writer_User, statement)
    assert _is_refusal(code), code

# ################################################################################################################################

def test_standby_connection_reads_the_source(schema:'Schema') -> 'None':
    connection = schema.connect(Standby_User)

    try:
        with connection.cursor() as cursor:
            cursor.execute('select count(*) from FACILITY.LOG_TREATMENTS')
            row = cursor.fetchone()
    finally:
        connection.close()

    assert row == (0,)

# ################################################################################################################################
# ################################################################################################################################
