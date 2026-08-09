# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The poll and the strip narrow the log down by included and excluded picks alike -
# included sources and objects read as IN conditions, excluded ones as NOT IN,
# and empty lists of either kind add nothing to the query.

# Zato
from zato.admin.web.views.audit_log.query import _build_where

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def _compile(condition:'any_') -> 'str':
    """ One condition as the SQL text it compiles to, with its values written in.
    """
    compiled = condition.compile(compile_kwargs={'literal_binds': True})

    out = str(compiled)

    return out

# ################################################################################################################################

def _build(
    sources:'strlist' = [],
    object_names:'strlist' = [],
    sources_excluded:'strlist' = [],
    object_names_excluded:'strlist' = [],
    ) -> 'anylist':
    """ Builds the WHERE conditions out of the picks alone - no outcomes, no query,
    no status and no time window, so what comes back is the picks' own doing.
    """
    out = _build_where(
        sources, object_names, [], '', '',
        sources_excluded=sources_excluded, object_names_excluded=object_names_excluded)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExcludedPicks:

    def test_excluded_sources_read_as_not_in(self):
        conditions = _build(sources_excluded=['config', 'pubsub'])
        condition_count = len(conditions)

        assert condition_count == 1

        text = _compile(conditions[0])

        assert 'NOT IN' in text
        assert "'config'" in text
        assert "'pubsub'" in text

# ################################################################################################################################

    def test_excluded_object_names_read_as_not_in(self):
        conditions = _build(object_names_excluded=['crm.customer.sync'])
        condition_count = len(conditions)

        assert condition_count == 1

        text = _compile(conditions[0])

        assert 'NOT IN' in text
        assert "'crm.customer.sync'" in text

# ################################################################################################################################

    def test_includes_and_excludes_combine(self):
        conditions = _build(sources=['mllp-channel'], object_names_excluded=['billing.invoice.export'])
        condition_count = len(conditions)

        assert condition_count == 2

        # The included sources come first, the excluded objects after them,
        # the same order the conditions are appended in.
        included_text = _compile(conditions[0])
        excluded_text = _compile(conditions[1])

        assert 'IN' in included_text
        assert 'NOT IN' not in included_text
        assert "'mllp-channel'" in included_text

        assert 'NOT IN' in excluded_text
        assert "'billing.invoice.export'" in excluded_text

# ################################################################################################################################

    def test_empty_lists_add_no_conditions(self):
        conditions = _build()

        assert conditions == []

# ################################################################################################################################

    def test_source_picks_match_case_insensitively(self):

        # The log is written to by more components than this application, each casing
        # its source names its own way - the picks match whatever casing is stored.
        included = _build(sources=['Sys'])
        excluded = _build(sources_excluded=['SYS'])

        included_text = _compile(included[0])
        excluded_text = _compile(excluded[0])

        assert 'lower(event.source)' in included_text
        assert "'sys'" in included_text

        assert 'lower(event.source)' in excluded_text
        assert "'sys'" in excluded_text

# ################################################################################################################################
# ################################################################################################################################
