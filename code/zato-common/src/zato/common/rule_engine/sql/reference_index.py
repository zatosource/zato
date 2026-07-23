# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import delete, insert, select

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.rule_engine.references import extract_references

# Local
from .data import anydict, reference_record_list, rowlist
from .database import SessionFactory
from .records import reference_record
from .schema import rule_reference_table
from .store_common import get_definition, require_text

# ################################################################################################################################
# ################################################################################################################################

class ReferenceIndex:
    """ A persisted where-used index over the terms every stored rule references.

    The index is rebuilt from a definition's canonical documents whenever they change,
    so where-used answers come from one indexed query instead of parsing every document.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def rebuild(self, *, definition_id:'int', documents:'anydict') -> 'int':
        """ Replaces one definition's index rows with what its documents reference now.
        """
        # Extract every term usage before opening the transaction ..
        rows:'rowlist' = []

        for document in documents.values():
            for usage in extract_references(document):
                row = {
                    'cluster_id':    default_cluster_id,
                    'definition_id': definition_id,
                    'rule_name':     document['full_name'],
                    'term':          usage['term'],
                    'block':         usage['block'],
                    'role':          usage['role'],
                }
                rows.append(row)

        session = self._session_factory()

        try:
            with session.begin():

                # Confirm the parent inside the same transaction ..
                _ = get_definition(session, definition_id)

                # .. drop the definition's previous index rows ..
                statement = delete(rule_reference_table)
                definition_condition = rule_reference_table.c.definition_id == definition_id
                statement = statement.where(definition_condition)
                _ = session.execute(statement)

                # .. and store the current ones in the same commit, so the index
                # .. can never hold a mix of the old and the new documents.
                if rows:
                    statement = insert(rule_reference_table)
                    _ = session.execute(statement, rows)

        # Release the transactional session in every case.
        finally:
            session.close()

        out = len(rows)
        return out

# ################################################################################################################################

    def where_used(self, term:'str') -> 'reference_record_list':
        """ Returns every indexed place that references one term, across all definitions.
        """
        # Validate the term before constructing the query ..
        require_text(term, 'Reference term')

        # .. ask the index by its promoted term column ..
        query = select(rule_reference_table)
        cluster_condition = rule_reference_table.c.cluster_id == default_cluster_id
        term_condition = rule_reference_table.c.term == term
        query = query.where(cluster_condition)
        query = query.where(term_condition)
        query = query.order_by(
            rule_reference_table.c.definition_id,
            rule_reference_table.c.rule_name,
            rule_reference_table.c.id,
        )
        session = self._session_factory()

        # .. load every usage ..
        try:
            result = session.execute(query)
            out:'reference_record_list' = []

            for row in result:
                record = reference_record(row)
                out.append(record)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def is_used(self, term:'str') -> 'bool':
        """ Returns whether anything anywhere still references one term.
        """
        usages = self.where_used(term)

        out = len(usages) > 0
        return out

# ################################################################################################################################
# ################################################################################################################################
