# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

# typing-extensions
from typing_extensions import TypeAlias

# Local
from zato.common.rule_engine.sql.schema import metadata, rule_definition_table, rule_version_table
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

table_name_set:TypeAlias = set[str]

# ################################################################################################################################
# ################################################################################################################################

def test_schema_has_exactly_the_planned_tables() -> 'None':
    """ The backend follows planned write patterns rather than entity proliferation.
    """
    # Read the complete metadata table set ..
    table_names:'table_name_set' = set(metadata.tables)

    # .. and verify that it contains exactly the definitions and their immutable versions.
    expected = {
        'rule_definition',
        'rule_version',
    }
    assert table_names == expected

# ################################################################################################################################

def test_documents_are_text_not_database_json() -> 'None':
    """ Every opaque document stays portable TEXT interpreted only by application code.
    """
    # Inspect every opaque document column ..
    definition_document_type = rule_definition_table.c.document.type
    version_document_type = rule_version_table.c.document.type

    # .. and verify that each one is plain SQL TEXT.
    assert isinstance(definition_document_type, Text)
    assert isinstance(version_document_type, Text)

# ################################################################################################################################

def test_every_table_and_index_compiles_for_postgresql() -> 'None':
    """ The SQLAlchemy schema compiles for PostgreSQL.
    """
    dialect = postgresql.dialect()

    # Compile every table and index ..
    for table in metadata.sorted_tables:
        create_table = CreateTable(table)
        compiled_table = create_table.compile(dialect=dialect)
        table_sql = str(compiled_table)

        # .. verify that the emitted statement names the intended table ..
        assert table.name in table_sql

        # .. and verify that every index has an emitted statement.
        for index in table.indexes:
            create_index = CreateIndex(index)
            compiled_index = create_index.compile(dialect=dialect)
            index_sql = str(compiled_index)
            index_name = cast_('str', index.name)
            assert index_name in index_sql

# ################################################################################################################################
# ################################################################################################################################
