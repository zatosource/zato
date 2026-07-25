# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from .resubmit_helpers import cleanup_env, get_last_event_id, use_tmp_audit_db
from zato.common.as2.common import AS2Exception
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import find_connection_name, load_event
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource

# ################################################################################################################################
# ################################################################################################################################

class TestLoadEvent:

    def test_load_event_returns_the_stored_details(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            options = {
                'mic': 'T3JkZXJzTUlD, sha-256',
                'cid': 'cid-original',
                'payload': 'ISA*00*Test payload of an 850 order',
                'filename': 'orders-850.edi',
                }
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', **options)

            event_id = get_last_event_id()
            event = load_event(event_id)
            details = event.details

            assert event.id == event_id
            assert event.cid == 'cid-original'
            assert event.source == AuditSource.AS2
            assert event.event_type == AuditEvent.Message_Sent
            assert event.object_name == 'ZatoRetail:PartnerCorp'
            assert event.msg_id == 'orders-850@zato'
            assert details['payload'] == 'ISA*00*Test payload of an 850 order'
            assert details['filename'] == 'orders-850.edi'
            assert details['mic'] == 'T3JkZXJzTUlD, sha-256'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_load_event_rejects_an_unknown_id(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            _ = AuditLog('test-server')

            with pytest.raises(AS2Exception, match='was not found'):
                _ = load_event(12345)

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_load_event_rejects_an_event_without_json_data(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            options = {'cid': 'cid-raw', 'data': 'Not a JSON document at all'}
            audit_log.insert(AuditSource.AS2, AuditEvent.Message_Sent, 'ZatoRetail:PartnerCorp', **options)

            event_id = get_last_event_id()

            with pytest.raises(AS2Exception, match='does not carry JSON data'):
                _ = load_event(event_id)

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestFindConnectionName:

    def test_the_matching_pair_names_its_connection(self) -> 'None':
        configs = [
            {'name': 'AS2 to PartnerCorp', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorp'},
            {'name': 'AS2 to PartnerCorpEU', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorpEU'},
        ]

        out = find_connection_name(configs, 'ZatoRetail', 'PartnerCorpEU')
        assert out == 'AS2 to PartnerCorpEU'

# ################################################################################################################################

    def test_an_unknown_pair_is_rejected(self) -> 'None':
        configs = [
            {'name': 'AS2 to PartnerCorp', 'as2_from': 'ZatoRetail', 'as2_to': 'PartnerCorp'},
        ]

        with pytest.raises(AS2Exception, match='No outgoing AS2 connection matches'):
            _ = find_connection_name(configs, 'ZatoRetail', 'UnknownPartner')

# ################################################################################################################################
# ################################################################################################################################
