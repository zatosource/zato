# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Project
from adapter_records.records_sql import Create_Section_Function, Delete_Field, Delete_Fields, Delete_Map_Row, \
    Delete_Section, Get_Checkpoint, Get_Field_Def_IDs, Get_Field_Defs, Get_Field_ID, Get_Section_Def_ID, Get_Section_ID, \
    Insert_Map_Row, Save_Field_Function, Set_Checkpoint
from model.facility import Checkpoint

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from common_sync.sync_database import DatabaseSession
    from zato.common.typing_ import intnone, intset

# ################################################################################################################################
# ################################################################################################################################

# A field's name to the value it is to hold.
fieldvalues = dict[str, str]

# A field's name to the definition ID the target knows it by.
fielddefs = dict[str, int]

# ################################################################################################################################
# ################################################################################################################################

class RecordsWriter:
    """ Writes into the target database on behalf of one source - creates, fills and removes sections,
    keeps the map of source IDs to sections and moves the checkpoint.
    """

    def __init__(self, database:'DatabaseSession', source:'str', section_name:'str') -> 'None':
        self.database = database
        self.source = source
        self.section_name = section_name

        # Resolved once per run.
        self.section_def_id = self._get_section_def_id()
        self.field_defs = self._get_field_defs()

# ################################################################################################################################

    def _get_section_def_id(self) -> 'int':
        rows = self.database.fetch_values(Get_Section_Def_ID, {'section_name': self.section_name})

        if not rows:
            raise Exception(f'Section not defined in the target -> {self.section_name}')

        out = rows[0]
        return out

# ################################################################################################################################

    def _get_field_defs(self) -> 'fielddefs':
        """ Each field name of the section to the definition ID the target knows it by.
        """
        out:'fielddefs' = {}

        for row in self.database.fetch_all(Get_Field_Defs, {'section_def_id': self.section_def_id}):
            out[row['field_name']] = row['field_def_id']

        return out

# ################################################################################################################################

    def get_checkpoint(self) -> 'Checkpoint':
        """ Where the previous run of this source got to. A source without a checkpoint row is not synced.
        """
        rows = self.database.fetch_values(Get_Checkpoint, {'source': self.source})

        if not rows:
            raise Exception(f'No checkpoint for source -> {self.source}')

        out = Checkpoint()
        out.source = self.source
        out.last_timestamp = rows[0]

        return out

# ################################################################################################################################

    def set_checkpoint(self, last_timestamp:'datetime') -> 'None':
        """ Moves the checkpoint of this source, in the same transaction as the changes it covers.
        """
        last_timestamp_bound = self.database.timestamp(last_timestamp)

        parameters = {
            'source': self.source,
            'last_timestamp': last_timestamp_bound,
        }

        updated = self.database.execute(Set_Checkpoint, parameters)

        if updated != 1:
            raise Exception(f'Checkpoint not updated for source -> {self.source} -> {updated}')

# ################################################################################################################################

    def get_section_id(self, source_id:'int') -> 'intnone':
        """ The section a source row was mapped to, or None if it was never written.
        """
        parameters = {
            'source_table': self.source,
            'source_id': source_id,
        }

        rows = self.database.fetch_values(Get_Section_ID, parameters)

        if rows:
            out = rows[0]
        else:
            out = None

        return out

# ################################################################################################################################

    def create_section(self, source_id:'int', patient_reference:'int') -> 'int':
        """ Creates a section through the target's package and records which source row it stands for.
        The source ID doubles as the sequence number.
        """
        out = self.database.call_function(Create_Section_Function, [patient_reference, source_id, self.section_def_id])

        parameters = {
            'source_table': self.source,
            'source_id': source_id,
            'section_id': out,
        }

        _ = self.database.execute(Insert_Map_Row, parameters)

        return out

# ################################################################################################################################

    def save_fields(self, section_id:'int', patient_reference:'int', values:'fieldvalues', answered_at:'datetime') -> 'None':
        """ Writes each value into its field of the section - a field that is already there is updated,
        any other one is inserted, always through the target's package.
        """
        answered_at_timestamp = self.database.timestamp(answered_at)

        for name, value in values.items():

            field_def_id = self.field_defs[name]
            existing = self.database.fetch_values(Get_Field_ID, {'section_id': section_id, 'field_def_id': field_def_id})
            existing_count = len(existing)

            if existing_count > 1:
                raise Exception(f'Field stored more than once -> {section_id} -> {name} -> {existing}')

            if existing:
                field_id = existing[0]
            else:
                field_id = None

            _ = self.database.call_function(Save_Field_Function, [
                field_id, patient_reference, field_def_id, section_id, value, value, answered_at_timestamp
            ])

# ################################################################################################################################

    def remove_other_fields(self, section_id:'int', values:'fieldvalues') -> 'None':
        """ Removes the fields of the section that the current values no longer have.
        """
        wanted:'intset' = set()

        for name in values:
            field_def_id = self.field_defs[name]
            wanted.add(field_def_id)

        for field_def_id in self.database.fetch_values(Get_Field_Def_IDs, {'section_id': section_id}):
            if field_def_id not in wanted:
                _ = self.database.execute(Delete_Field, {'section_id': section_id, 'field_def_id': field_def_id})

# ################################################################################################################################

    def delete_section(self, source_id:'int', section_id:'int') -> 'None':
        """ Removes a section, its fields and the map row that pointed at it.
        """
        parameters = {
            'source_table': self.source,
            'source_id': source_id,
        }

        _ = self.database.execute(Delete_Fields, {'section_id': section_id})
        _ = self.database.execute(Delete_Section, {'section_id': section_id})
        _ = self.database.execute(Delete_Map_Row, parameters)

# ################################################################################################################################
# ################################################################################################################################
