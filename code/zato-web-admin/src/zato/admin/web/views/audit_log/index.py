# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# SQLAlchemy
from sqlalchemy import select

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.audit_log.columns import _all_sources_columns, _all_sources_section_title, _all_sources_title, \
    _endpoint_page_url, _event_type_label, _get_outcomes, _object_page_url, _poll_url, _run_page_url, _source_columns, \
    _source_endpoint_label, _source_event_label, _source_except_label, _source_label, _source_object_label, \
    _source_page_url, _source_title
from zato.admin.web.views.audit_log.sources import get_resubmit_labels, _source_outstanding
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.file_transfer_words import file_transfer_words
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

def _get_filter_options() -> 'anylist':
    """ What the all-events page offers its filter selects - every source there can be,
    each under its human label and with the objects its events were written against.
    """

    # Every source of the catalog is on offer whether or not it has events yet ..
    by_source:'anydict' = {}
    out:'anylist' = []

    for source, label in _source_label.items():
        entry = {'source': source, 'label': label, 'objects': []}

        by_source[source] = entry
        out.append(entry)

    # .. and the objects come from the events themselves.
    statement = select(event_table.c.source, event_table.c.object_name)
    statement = statement.distinct()
    statement = statement.order_by(event_table.c.source, event_table.c.object_name)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)

        for source, object_name in result:

            # A source the log holds that the catalog does not know is still shown,
            # under its raw name - the log may be ahead of this application.
            if source not in by_source:
                entry = {'source': source, 'label': source, 'objects': []}

                by_source[source] = entry
                out.append(entry)

            # An event written down with no object at all adds nothing to filter by
            if object_name:
                by_source[source]['objects'].append(object_name)

    return out

# ################################################################################################################################

@method_allowed('GET')
def object_index(req:'any_') -> 'TemplateResponse':
    """ The audit log page - for one object of one source, e.g. a pub/sub topic, or, with
    no source named at all, for every event of every source in one listing.
    """
    source = req.GET.get('source', '')
    object_name = req.GET.get('object_name', '')

    # The page can open pre-filtered to the open exchanges of this source
    status = req.GET.get('status', '')

    # It can also open pre-filtered to a time window and a search query,
    # which is how the analytics screens drill down into the raw events.
    time_from = req.GET.get('time_from', '')
    time_to = req.GET.get('time_to', '')
    query = req.GET.get('query', '')

    # And to events of one kind alone, which is what a clicked event word deep-links to
    event_type = req.GET.get('event_type', '')

    # The listing draws each row's cells and chips out of this source's columns - the
    # all-events page reads by the columns every source shares, the source among them.
    if source:
        columns = _source_columns[source]
        audit_log_title = _source_title[source]
        section_title = object_name
    else:
        columns = _all_sources_columns
        audit_log_title = _all_sources_title
        section_title = _all_sources_section_title

    # Every rendering of the page offers the source and object filter selects
    filter_options = _get_filter_options()

    columns_json = json.dumps(columns)

    # .. and offers filters for the outcomes this source's events actually report
    outcomes_json = json.dumps(list(_get_outcomes(source)))

    # The per-event-type resubmit labels of each source, keyed by source, so any row
    # of any listing knows what its action link is to say
    resubmit_labels = get_resubmit_labels()
    resubmit_labels_json = json.dumps(resubmit_labels)

    # The words the file transfer presenter renders runs with.
    words = file_transfer_words()
    file_transfer_words_json = json.dumps(words)

    # The exchanges of this source - the event that opens one and the event that closes it -
    # which is what pairing the two halves of an exchange onto one line needs.
    exchange = {'open_event': '', 'close_event': ''}

    if outstanding := _source_outstanding.get(source):
        exchange['open_event'] = outstanding.open_event
        exchange['close_event'] = outstanding.close_event

    return_data = {
        'cluster_id': default_cluster_id,
        'source': source,
        'object_name': object_name,
        'audit_log_title': audit_log_title,
        'section_title': section_title,
        'poll_url': _poll_url,
        'columns_json': columns_json,
        'outcomes_json': outcomes_json,
        'status': status,
        'time_from': time_from,
        'time_to': time_to,
        'query': query,
        'event_type': event_type,
        'resubmit_labels_json': resubmit_labels_json,
        'exchange_json': json.dumps(exchange),
        'filter_options_json': json.dumps(filter_options),
        'source_labels_json': json.dumps(_source_event_label),
        'source_except_labels_json': json.dumps(_source_except_label),
        'object_links_json': json.dumps(_object_page_url),
        'object_labels_json': json.dumps(_source_object_label),
        'source_links_json': json.dumps(_source_page_url),
        'endpoint_links_json': json.dumps(_endpoint_page_url),
        'endpoint_labels_json': json.dumps(_source_endpoint_label),
        'run_links_json': json.dumps(_run_page_url),
        'event_labels_json': json.dumps(_event_type_label),
        'file_transfer_words_json': file_transfer_words_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/audit-log.html',
    }

    out = TemplateResponse(req, 'zato/audit-log.html', return_data)

    return out

# ################################################################################################################################
# ################################################################################################################################
