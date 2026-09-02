# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Re-exports only - the implementation lives in the sibling modules.

# Zato
from zato.admin.web.views.audit_log.columns.labels import _all_sources_section_title, _all_sources_title, \
    _event_type_label, _source_endpoint_label, _source_event_label, _source_except_label, _source_label, \
    _source_object_label, _source_title
from zato.admin.web.views.audit_log.columns.tables import _all_sources_columns, _data_preview_length, _default_page, \
    _default_page_size, _flow_columns, _get_outcomes, _poll_url, _preview_length, _row_columns, _row_numeric_columns, \
    _search_columns, _source_attr_columns, _source_body_preview, _source_columns, _status_outstanding
from zato.admin.web.views.audit_log.columns.urls import _endpoint_page_url, _object_page_url, _run_page_url, \
    _source_page_url

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    # Add dummy assignments to satisfy type checkers
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# For flake8
_all_sources_columns = _all_sources_columns
_all_sources_section_title = _all_sources_section_title
_all_sources_title = _all_sources_title
_data_preview_length = _data_preview_length
_default_page = _default_page
_default_page_size = _default_page_size
_endpoint_page_url = _endpoint_page_url
_event_type_label = _event_type_label
_flow_columns = _flow_columns
_get_outcomes = _get_outcomes
_object_page_url = _object_page_url
_poll_url = _poll_url
_preview_length = _preview_length
_row_columns = _row_columns
_row_numeric_columns = _row_numeric_columns
_run_page_url = _run_page_url
_search_columns = _search_columns
_source_attr_columns = _source_attr_columns
_source_body_preview = _source_body_preview
_source_columns = _source_columns
_source_endpoint_label = _source_endpoint_label
_source_event_label = _source_event_label
_source_except_label = _source_except_label
_source_label = _source_label
_source_object_label = _source_object_label
_source_page_url = _source_page_url
_source_title = _source_title
_status_outstanding = _status_outstanding

# ################################################################################################################################
# ################################################################################################################################

def get_source_catalog() -> 'anydict':
    """ Returns the per-source catalog - the label, the page title and the table columns of each source.
    """
    out = {
        'labels': _source_label,
        'titles': _source_title,
        'columns': _source_columns,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
