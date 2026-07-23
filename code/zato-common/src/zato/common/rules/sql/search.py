# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.rules.render import render_document

# Local
from .constants import Default_Search_Limit, Definition_Type_Ruleset, Documents_Key
from .data import any_, dictlist
from .database import SessionFactory
from .document import deserialize_document
from .errors import InvalidStoreInputError
from .schema import rule_definition_table
from .store_common import require_text

# ################################################################################################################################
# ################################################################################################################################

# A query that is one plain token also appears verbatim in the stored JSON,
# so such searches can be prefiltered in the database before any rendering.
_plain_token = re.compile(r'^[\w.]+$')

# ################################################################################################################################
# ################################################################################################################################

class ContentSearch:
    """ Case-insensitive search over rules as their readable rendered sentences.

    Matches come back with the whole rendered line and the position of the match
    inside it, so a view can highlight the hit in place.
    """

    def __init__(self, session_factory:'SessionFactory') -> 'None':
        self._session_factory = session_factory

# ################################################################################################################################

    def _candidates(self, text:'str') -> 'list[any_]':
        """ Returns the active ruleset definitions that could contain the search text.
        """
        # Every search covers active rulesets only ..
        query = select(
            rule_definition_table.c.id,
            rule_definition_table.c.name,
            rule_definition_table.c.document,
        )
        cluster_condition = rule_definition_table.c.cluster_id == default_cluster_id
        type_condition = rule_definition_table.c.object_type == Definition_Type_Ruleset
        active_condition = rule_definition_table.c.is_active.is_(True)
        query = query.where(cluster_condition)
        query = query.where(type_condition)
        query = query.where(active_condition)

        # .. a one-token query appears verbatim in the stored JSON, so the database
        # .. can discard non-matching documents before any of them is rendered ..
        if _plain_token.match(text):
            escaped = text.lower()
            escaped = escaped.replace('\\', '\\\\')
            escaped = escaped.replace('%', '\\%')
            escaped = escaped.replace('_', '\\_')
            pattern = f'%{escaped}%'
            lower_document = func.lower(rule_definition_table.c.document)
            document_condition = lower_document.like(pattern, escape='\\')
            query = query.where(document_condition)

        # .. request a stable order ..
        query = query.order_by(rule_definition_table.c.name, rule_definition_table.c.id)
        session = self._session_factory()

        # .. load every candidate ..
        try:
            result = session.execute(query)
            out = list(result)

        # .. and release the read-only session.
        finally:
            session.close()

        return out

# ################################################################################################################################

    def search(self, text:'str', limit:'int' = Default_Search_Limit) -> 'dictlist':
        """ Returns every place the text appears in a rendered rule, line by line.
        """
        # Validate the query and pagination before any database work ..
        require_text(text, 'Search text')

        if limit < 1:
            raise InvalidStoreInputError('Search limit must be at least 1')

        candidates = self._candidates(text)
        needle = text.lower()

        # Our response to produce
        out:'dictlist' = []

        for candidate in candidates:
            payload = deserialize_document(candidate.document)

            # Only canonical rulesets carry rule documents to render.
            if Documents_Key not in payload:
                continue

            for document in payload[Documents_Key].values():

                # Search the rule as the sentences a person reads, not as stored JSON ..
                rendered = render_document(document)
                lines = rendered.split('\n')

                for line_number, line in enumerate(lines, 1):

                    # .. a line without the text contributes nothing ..
                    start = line.lower().find(needle)
                    if start < 0:
                        continue

                    # .. while a match reports its exact place, so a view can highlight it.
                    hit = {
                        'definition_id':   candidate.id,
                        'definition_name': candidate.name,
                        'rule':            document['full_name'],
                        'line_number':     line_number,
                        'line':            line,
                        'match_start':     start,
                        'match_end':       start + len(needle),
                    }
                    out.append(hit)

                    # One full page is enough - stop before rendering anything else.
                    if len(out) == limit:
                        return out

        return out

# ################################################################################################################################
# ################################################################################################################################
