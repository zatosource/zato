# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every rendering of the audit log page carries the same filter selects and the same
# resubmit labels, whether it was opened from the menu or from a listing's own link -
# only the columns follow the source the address names.

# stdlib
import os
from contextlib import contextmanager
from json import loads

# Django
from django.http import QueryDict

# Zato
from zato.admin.web.views.audit_log import object_index
from zato.admin.web.views.audit_log.sources import get_resubmit_labels, _source_resubmit
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource, ModuleCtx as AuditLogCtx
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_

# Test support
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server and channel the one event of these tests is written under
_server_name = 'test-page-parity-server'
_channel_name = 'test.page.parity.channel'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _one_mllp_event(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database holding one MLLP channel event.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details_config = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details_config):

        audit_log = AuditLog(_server_name)

        _ = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Message_Received, _channel_name,
            cid='cid-page-parity-1', outcome=AuditOutcome.OK, data='MSH|^~\\&|')

        yield

# ################################################################################################################################

def _new_request(source:'str', object_name:'str') -> 'Bunch':
    """ Builds the GET request the page is opened with - a listing's link names a source
    and an object, the menu link names neither.
    """
    query = QueryDict('', mutable=True)

    if source:
        query['source'] = source

    if object_name:
        query['object_name'] = object_name

    out = Bunch()

    out.method = 'GET'
    out.GET = query

    return out

# ################################################################################################################################

def _get_context(tmp_path:'any_', source:'str', object_name:'str') -> 'dict':
    with _one_mllp_event(tmp_path):
        response = object_index(_new_request(source, object_name))

    out = cast_('dict', response.context_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResubmitLabels:

    def test_the_labels_are_keyed_by_source(self):
        labels = get_resubmit_labels()

        assert set(labels) == set(_source_resubmit)

# ################################################################################################################################

    def test_each_source_maps_its_event_types_to_display_labels(self):
        labels = get_resubmit_labels()

        assert labels['mllp-channel'] == {AuditEvent.Message_Received: 'Resubmit'}
        assert labels['rest-outgoing'] == {AuditEvent.Request_Sent: 'Resubmit'}

# ################################################################################################################################
# ################################################################################################################################

class TestPageContext:

    def test_a_per_source_page_offers_the_filter_selects_too(self, tmp_path:'os.PathLike'):
        context = _get_context(tmp_path, AuditSource.MLLP_Channel, _channel_name)
        filter_options = loads(context['filter_options_json'])

        assert filter_options

        by_source = {option['source']: option for option in filter_options}
        assert by_source[AuditSource.MLLP_Channel]['objects'] == [_channel_name]

# ################################################################################################################################

    def test_the_menu_page_offers_the_same_filter_selects(self, tmp_path:'os.PathLike'):
        context = _get_context(tmp_path, '', '')
        filter_options = loads(context['filter_options_json'])

        by_source = {option['source']: option for option in filter_options}
        assert by_source[AuditSource.MLLP_Channel]['objects'] == [_channel_name]

# ################################################################################################################################

    def test_both_renderings_serve_the_same_source_keyed_resubmit_labels(self, tmp_path:'os.PathLike'):
        per_source_context = _get_context(tmp_path, AuditSource.MLLP_Channel, _channel_name)
        menu_context = _get_context(tmp_path, '', '')

        per_source_labels = loads(per_source_context['resubmit_labels_json'])
        menu_labels = loads(menu_context['resubmit_labels_json'])

        assert per_source_labels == menu_labels
        assert per_source_labels['mllp-channel'] == {AuditEvent.Message_Received: 'Resubmit'}

# ################################################################################################################################
# ################################################################################################################################
