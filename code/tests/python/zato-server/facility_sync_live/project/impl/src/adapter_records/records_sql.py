# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Everything the sync runs against the target database as SYNC_WRITER - its own tables by name, the target's tables
# through the synonyms it has for them, and the target's package for anything that creates or changes a record.

# ################################################################################################################################
# ################################################################################################################################

Get_Checkpoint = """
select LAST_TS
from SYNC_CHECKPOINT
where SOURCE = :source
"""

Set_Checkpoint = """
update SYNC_CHECKPOINT
set LAST_TS = :last_timestamp, UPDATED_AT = systimestamp
where SOURCE = :source
"""

Get_Section_ID = """
select PS_ID
from SYNC_ID_MAP
where SOURCE_TABLE = :source_table
and SOURCE_ID = :source_id
"""

Insert_Map_Row = """
insert into SYNC_ID_MAP (SOURCE_TABLE, SOURCE_ID, PS_ID)
values (:source_table, :source_id, :section_id)
"""

Delete_Map_Row = """
delete from SYNC_ID_MAP
where SOURCE_TABLE = :source_table
and SOURCE_ID = :source_id
"""

Get_Section_Def_ID = """
select SD_ID
from SECTION_DEF
where SD_NAME = :section_name
"""

Get_Field_Defs = """
select FD_ID as FIELD_DEF_ID, FD_NAME as FIELD_NAME
from FIELD_DEF
where FD_SD_ID = :section_def_id
"""

Get_Field_ID = """
select PF_ID
from PATIENT_FIELD
where PF_PS_ID = :section_id
and PF_FD_ID = :field_def_id
"""

Get_Field_Def_IDs = """
select PF_FD_ID
from PATIENT_FIELD
where PF_PS_ID = :section_id
"""

Delete_Field = """
delete from PATIENT_FIELD
where PF_PS_ID = :section_id
and PF_FD_ID = :field_def_id
"""

Delete_Fields = """
delete from PATIENT_FIELD
where PF_PS_ID = :section_id
"""

Delete_Section = """
delete from PATIENT_SECTION
where PS_ID = :section_id
"""

# The target's own way of creating a record and writing a field into it.
Create_Section_Function = 'RECORDS_API.PKG_FORMS.ATTACH_AND_CREATE_FORM'
Save_Field_Function     = 'RECORDS_API.PKG_FORMS.SAVE_PATIENT_FIELD'

# ################################################################################################################################
# ################################################################################################################################
