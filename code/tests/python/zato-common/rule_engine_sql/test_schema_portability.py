# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import Text
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.engine import Dialect
from sqlalchemy.schema import CreateIndex, CreateTable

# typing-extensions
from typing_extensions import TypeAlias

# Local
from zato.common.rule_engine.sql.schema import metadata, rule_decision_table, rule_definition_table, rule_event_table, \
    rule_version_table

# ################################################################################################################################
# ################################################################################################################################

dialect_list:TypeAlias = list[Dialect]
table_name_set:TypeAlias = set[str]

# ################################################################################################################################
# ################################################################################################################################

def _dialects() -> 'dialect_list':
    """ Returns every database dialect required from the first release.
    """
    # Instantiate each required SQL compiler ..
    sqlite_dialect = sqlite.dialect()
    mysql_dialect = mysql.dialect()
    postgresql_dialect = postgresql.dialect()

    # .. and return them in the stable test order.
    out = [sqlite_dialect, mysql_dialect, postgresql_dialect]
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_schema_has_exactly_the_planned_tables() -> 'None':
    """ The backend follows planned write patterns rather than entity proliferation.
    """
    # Read the complete metadata table set ..
    table_names:'table_name_set' = set(metadata.tables)

    # .. and verify that it contains exactly the planned write patterns - the four
    # .. core ones plus the where-used index and the per-actor workspace stores.
    expected = {
        'rule_definition',
        'rule_version',
        'rule_event',
        'rule_decision',
        'rule_reference',
        'rule_follow',
        'rule_view',
        'rule_recent',
    }
    assert table_names == expected

# ################################################################################################################################

def test_documents_and_stories_are_text_not_database_json() -> 'None':
    """ Every opaque document stays portable TEXT interpreted only by application code.
    """
    # Inspect every opaque document and story column ..
    definition_document_type = rule_definition_table.c.document.type
    version_document_type = rule_version_table.c.document.type
    event_payload_type = rule_event_table.c.payload.type
    decision_payload_type = rule_decision_table.c.payload.type
    fired_rule_ids_type = rule_decision_table.c.fired_rule_ids.type

    # .. and verify that each one is plain SQL TEXT.
    assert isinstance(definition_document_type, Text)
    assert isinstance(version_document_type, Text)
    assert isinstance(event_payload_type, Text)
    assert isinstance(decision_payload_type, Text)
    assert isinstance(fired_rule_ids_type, Text)

# ################################################################################################################################

def test_every_table_and_index_compiles_for_required_dialects() -> 'None':
    """ The same SQLAlchemy schema compiles for every initially supported database.
    """
    # Compile every table and index with every required dialect ..
    dialects = _dialects()

    for dialect in dialects:
        for table in metadata.sorted_tables:
            create_table = CreateTable(table)
            compiled_table = create_table.compile(dialect=dialect)
            table_sql = str(compiled_table)

            # .. verify that the emitted statement names the intended table ..
            assert table.name in table_sql

            # .. and verify every index has a portable emitted statement.
            for index in table.indexes:
                create_index = CreateIndex(index)
                compiled_index = create_index.compile(dialect=dialect)
                index_sql = str(compiled_index)
                assert index.name in index_sql

# ################################################################################################################################
# ################################################################################################################################
