# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every audit log source needs a label, a title and a column layout.

# Zato
from zato.admin.web.views.audit_log.columns import get_source_catalog
from zato.common.audit_log.common import AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

def _get_all_sources() -> 'strlist':
    """ Every source code the AuditSource catalog defines.
    """
    out = []

    # Walk the catalog's namespace ..
    for name, value in vars(AuditSource).items():

        # .. skipping what is not a source code ..
        if name.startswith('_'):
            continue

        # .. and keeping every string entry.
        if isinstance(value, str):
            out.append(value)

    return out

# ################################################################################################################################

_all_sources = _get_all_sources()
_catalog = get_source_catalog()

# ################################################################################################################################
# ################################################################################################################################

class TestSourceCatalog:
    """ The audit log source catalog.
    """

    def test_every_source_has_a_label(self:'any_') -> 'None':

        labels = _catalog['labels']

        for source in _all_sources:
            assert source in labels, f'No label for `{source}`'

# ################################################################################################################################

    def test_every_source_has_a_title(self:'any_') -> 'None':

        titles = _catalog['titles']

        for source in _all_sources:
            assert source in titles, f'No title for `{source}`'

# ################################################################################################################################

    def test_every_source_has_columns(self:'any_') -> 'None':

        columns = _catalog['columns']

        for source in _all_sources:
            assert source in columns, f'No columns for `{source}`'
            assert columns[source], f'Empty columns for `{source}`'

# ################################################################################################################################
# ################################################################################################################################
