# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from threading import RLock
from traceback import format_exc

# gevent
from gevent import spawn

# httpx
import httpx

# Zato
from zato.common.api import AS2
from zato.common.as2.audit import record_inbound_result
from zato.common.as2.config import build_keystore, build_partnerships
from zato.common.as2.duplicates import DuplicateStore
from zato.common.as2.inbound import handle as inbound_handle
from zato.common.audit_log.api import AuditLog
from zato.edi.envelope import read_envelope

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.inbound import InboundPayload, InboundResult, PendingAsyncMDN
    from zato.common.as2.partnership import Partnership, partnership_list
    from zato.common.typing_ import dictlist, stranydict, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    from zato.server.base.parallel import ParallelServer
    InboundPayload = InboundPayload
    InboundResult = InboundResult
    Partnership = Partnership
    PendingAsyncMDN = PendingAsyncMDN

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AS2ChannelRuntime:
    """ The runtime representation of one AS2 channel - its keystore, duplicate store
    and routing target, built from the channel's configuration. The partnerships come
    from the Dashboard-managed AS2 connections and are rebuilt on each request,
    so an edit takes effect immediately.
    """

    def __init__(self, server:'ParallelServer', config:'stranydict') -> 'None':
        self.server = server
        self.config = config
        self.name = config['name']

        # The runtime keystore is built lazily, on first use,
        # so that incomplete configuration does not break config propagation.
        self._lock = RLock()
        self._keystore:'Keystore | None' = None

        # The audit log is built lazily too - opening the shared database can wait
        # until the first message actually arrives.
        self._audit_log:'AuditLog | None' = None

        # For how many days an already-processed message and its stored MDN are remembered.
        # The opaque column genuinely stores a null when the channel was saved without one.
        window_days = config['as2_duplicate_window_days']

        if not window_days:
            window_days = AS2.Default.Duplicate_Window_Days

        self.duplicates = DuplicateStore(window_days)

        # Where accepted messages go - the channel's service when one is configured,
        # its pub/sub topic otherwise. A partner's own routing target overrides both.
        self.service_name = config['service_name']

        topic_name = config['as2_inbound_topic']
        if not topic_name:
            topic_name = AS2.Default.Inbound_Topic
        self.inbound_topic = topic_name

# ################################################################################################################################

    def _get_keystore(self) -> 'Keystore':
        """ Returns this channel's keystore, building it on first use -
        the private keys are decrypted only at this point.
        """
        with self._lock:
            if self._keystore is None:
                self._keystore = build_keystore(self.config, self.server.decrypt)

            out = self._keystore

        return out

# ################################################################################################################################

    def _get_audit_log(self) -> 'AuditLog':
        """ Returns this channel's audit log, building it on first use.
        """
        with self._lock:
            if self._audit_log is None:
                self._audit_log = AuditLog(self.server.name)

            out = self._audit_log

        return out

# ################################################################################################################################

    def _get_partnerships(self) -> 'partnership_list':
        """ Returns the partnerships of all the AS2 connections defined in this cluster.
        They are rebuilt on each request from the live configuration - the per-type dict
        that create, edit and delete events keep current - which is how a Dashboard
        change takes effect without a channel restart.
        """

        # The flat configuration dicts of all the AS2 connections
        configs:'dictlist' = []

        for config in self.server.config_manager.outconn_as2.values():
            configs.append(config)

        out = build_partnerships(configs)
        return out

# ################################################################################################################################

    def _build_routed_message(self, result:'InboundResult', payload:'InboundPayload') -> 'stranydict':
        """ Builds the dictionary that one accepted document is routed with - the AS2 identities
        plus the EDI envelope identifiers, so subscribers route without re-parsing anything.
        """

        # The envelope identifiers of an EDI document - a payload that is not EDI
        # comes back with all of them empty, which subscribers can tell by the format field.
        envelope = read_envelope(payload.data)
        envelope_dict = envelope.to_dict()

        data = payload.data.decode('utf8', 'replace')

        out = {
            'message_id': result.message_id,
            'as2_from': result.as2_from,
            'as2_to': result.as2_to,
            'filename': payload.filename,
            'content_type': payload.content_type,
            'data': data,
            'edi': envelope_dict,
        }

        return out

# ################################################################################################################################

    def _route(self, cid:'str', result:'InboundResult') -> 'None':
        """ Hands each accepted document over to its routing target - the partner's own
        service or topic when the partnership names one, with the service taking precedence,
        the channel's own target otherwise.
        """
        partnership = result.partnership

        for payload in result.payloads:

            message = self._build_routed_message(result, payload)

            # The partner's own service receives the message directly ..
            if partnership.inbound_service:
                _ = self.server.invoke(partnership.inbound_service, message)

            # .. or the partner's own topic ..
            elif partnership.inbound_topic:
                _ = self.server.pubsub_backend.publish(partnership.inbound_topic, message, cid=cid, correl_id=cid)

            # .. or the channel's service ..
            elif self.service_name:
                _ = self.server.invoke(self.service_name, message)

            # .. and by default, the channel's topic, which is where reliability lives -
            # redelivery and retries are pub/sub's built-in behavior.
            else:
                _ = self.server.pubsub_backend.publish(self.inbound_topic, message, cid=cid, correl_id=cid)

# ################################################################################################################################

    def _deliver_async_mdn(self, cid:'str', pending:'PendingAsyncMDN') -> 'None':
        """ Delivers one asynchronous MDN to the URL the sender named. Runs in its own greenlet -
        the inbound POST was already answered with HTTP 202 by the time this runs.
        """
        try:
            response = httpx.post(pending.url, content=pending.body, headers=pending.headers)
            logger.info('AS2 async MDN delivered to `%s` (HTTP %d) on channel `%s`; cid:%s',
                pending.url, response.status_code, self.name, cid)

        # The peer's endpoint is an external boundary - a failed delivery is logged,
        # the message itself was already accepted and routed.
        except Exception:
            logger.warning('AS2 async MDN delivery to `%s` failed on channel `%s`; cid:%s; %s',
                pending.url, self.name, cid, format_exc())

# ################################################################################################################################

    def handle(self, cid:'str', body:'bytes', headers:'strstrdict') -> 'InboundResult':
        """ Runs one incoming request through the AS2 inbound pipeline,
        routes whatever documents it accepted and remembers the message
        so a replay gets the same MDN back without being delivered twice.
        """
        partnerships = self._get_partnerships()
        keystore = self._get_keystore()

        out = inbound_handle(
            body,
            headers,
            partnerships,
            keystore,
            is_duplicate=self.duplicates.get,
        )

        # A partnership whose audit log was turned off explicitly records no events,
        # while a request that matched no partnership is always recorded.
        if out.partnership:
            needs_audit = out.partnership.is_audit_log_active
        else:
            needs_audit = True

        # The arrival and the MDN that went back are recorded as non-repudiation evidence -
        # a replay records nothing new because its first delivery already did.
        if needs_audit:
            audit_log = self._get_audit_log()
            record_inbound_result(audit_log, out, body, cid)

        # A replay gets the stored MDN back, byte for byte - nothing is routed.
        if out.is_duplicate:
            logger.info('AS2 message `%s` replayed on channel `%s`, stored MDN returned; cid:%s',
                out.message_id, self.name, cid)
            return out

        # A rejected message carries an MDN with an error disposition - nothing is routed either.
        if out.is_error:
            logger.warning('AS2 request rejected with `%s` on channel `%s`; cid:%s', out.error_modifier, self.name, cid)
            return out

        # Hand the accepted documents over to their routing targets ..
        self._route(cid, out)

        # .. remember the message so a replay is detectable - only successfully processed
        # messages are remembered, a failed one stays reprocessable, and a partnership
        # whose audit log is off keeps nothing, since the duplicate store lives
        # in the same database the audit log does ..
        if out.message_id:
            if needs_audit:
                _ = self.duplicates.store(out.as2_from, out.as2_to, out.message_id, out.status_code, out.body, out.headers)

        # .. an asynchronous MDN is delivered in the background, after the inbound POST is answered ..
        if out.pending_async_mdn:
            _ = spawn(self._deliver_async_mdn, cid, out.pending_async_mdn)

        payload_count = len(out.payloads)
        suffix = 'payload' if payload_count == 1 else 'payloads'

        logger.info('AS2 message `%s` accepted on channel `%s`, %d %s routed',
            out.message_id, self.name, payload_count, suffix)

        return out

# ################################################################################################################################
# ################################################################################################################################
