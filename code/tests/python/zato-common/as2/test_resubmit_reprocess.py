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
from .resubmit_helpers import cleanup_env, Default_Topic, get_events, RouteRecorder, use_tmp_audit_db
from zato.common.as2.common import AS2Exception
from zato.common.as2.partnership import new_partnership, Partnership
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import load_event, record_message_received, reprocess, Target_Service, Target_Topic
from zato.common.audit_log.api import AuditEvent, AuditLog
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

class TestReprocess:

    def _seed_received_message(self) -> 'AuditLog':
        """ Writes one inbound message into the audit database, the way the channel records it.
        """
        audit_log = AuditLog('test-server')

        options = {
            'payload': 'ISA*00*Test payload of an 810 invoice',
            'filename': 'invoice-810.edi',
            'content_type': 'application/edi-x12',
            'cid': 'cid-received',
            }
        record_message_received(audit_log, 'PartnerCorp', 'ZatoRetail', '<invoice-810@partnercorp>', **options)

        return audit_log

# ################################################################################################################################

    def _new_reversed_partnership(self) -> 'Partnership':
        """ Builds the partnership matching messages that arrive from PartnerCorp -
        the fields compare crosswise, the way inbound matching works.
        """
        out = new_partnership()
        out.as2_from = 'ZatoRetail'
        out.as2_to = 'PartnerCorp'

        return out

# ################################################################################################################################

    def test_reprocess_routes_to_the_partner_service(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            partnership = self._new_reversed_partnership()
            partnership.inbound_service = 'orders.process-invoice'
            partnerships = [partnership]

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            result = reprocess(event, partnerships, invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

            # The partner's own service received the message directly ..
            assert result.target_kind == Target_Service
            assert result.target_name == 'orders.process-invoice'
            assert invoke_service.target_name == 'orders.process-invoice'
            assert publish.target_name is None

            # .. in the same shape a live delivery would arrive in.
            message = invoke_service.message
            assert message is not None
            assert message['message_id'] == 'invoice-810@partnercorp'
            assert message['as2_from'] == 'PartnerCorp'
            assert message['as2_to'] == 'ZatoRetail'
            assert message['filename'] == 'invoice-810.edi'
            assert message['content_type'] == 'application/edi-x12'
            assert message['data'] == 'ISA*00*Test payload of an 810 invoice'
            assert 'edi' in message

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_reprocess_routes_to_the_partner_topic(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            partnership = self._new_reversed_partnership()
            partnership.inbound_topic = 'partnercorp.invoices'
            partnerships = [partnership]

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            result = reprocess(event, partnerships, invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

            assert result.target_kind == Target_Topic
            assert result.target_name == 'partnercorp.invoices'
            assert publish.target_name == 'partnercorp.invoices'
            assert invoke_service.target_name is None

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_reprocess_defaults_to_the_shared_topic(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            # No partnership matches the pair anymore, e.g. the connection was deleted.
            result = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

            assert result.target_kind == Target_Topic
            assert result.target_name == Default_Topic
            assert publish.target_name == Default_Topic

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_reprocess_records_the_new_attempt(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = self._seed_received_message()

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

            # The new attempt is its own event, linked to the original by its CID ..
            events = get_events(AuditEvent.Message_Received)
            event_count = len(events)
            assert event_count == 2

            reprocessed = events[1]
            assert reprocessed['cid'] == 'cid-reprocess'
            assert reprocessed['correl_id'] == 'cid-received'
            assert reprocessed['object_name'] == 'PartnerCorp:ZatoRetail'
            assert reprocessed['msg_id'] == 'invoice-810@partnercorp'

            # .. and it carries the payload too, so it can be reprocessed once again.
            details = loads(reprocessed['data'])
            assert details['payload'] == 'ISA*00*Test payload of an 810 invoice'
            assert details['filename'] == 'invoice-810.edi'
            assert details['content_type'] == 'application/edi-x12'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_reprocess_rejects_other_event_types(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            audit_log = AuditLog('test-server')

            reconciler = MDNReconciler('test-server')
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', payload='Test payload')

            event = load_event(1)

            invoke_service = RouteRecorder()
            publish = RouteRecorder()

            with pytest.raises(AS2Exception, match='can be reprocessed'):
                _ = reprocess(event, [], invoke_service, publish, audit_log, 'cid-reprocess', Default_Topic)

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
