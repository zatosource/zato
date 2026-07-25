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

# Zato
from zato.common.api import AS2
from zato.common.as2.async_mdn import AsyncMDNQueue, deliver as deliver_async_mdn, post_async_mdn
from zato.common.as2.audit import record_inbound_result
from zato.common.as2.config import build_keystore, build_partnerships
from zato.common.as2.duplicates import DuplicateStore
from zato.common.as2.inbound import handle as inbound_handle
from zato.common.audit_log.api import AuditLog
from zato.common.util.api import utcnow
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
    """ The runtime representation of one AS2 channel - its keystore, duplicate store,
    asynchronous MDN queue and routing target, built from the channel's configuration.
    The partnerships come from the Dashboard-managed AS2 connections and are rebuilt
    whenever one of those connections changes, so an edit takes effect immediately.
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

        # So is the queue asynchronous MDNs are persisted in.
        self._async_mdn_queue:'AsyncMDNQueue | None' = None

        # The partnerships built out of the AS2 outgoing connections, kept alongside the generation
        # of the configuration they were built from. Building one costs an X.509 parse per
        # configured certificate, which is not something to spend per arriving message.
        self._partnerships:'partnership_list' = []
        self._partnerships_generation = -1

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
        """ Returns the partnerships of all the AS2 connections defined in this cluster, built out
        of the live configuration - the per-type dict that create, edit and delete events keep
        current - and reused until one of those events says the configuration moved on, which
        is how a Dashboard change takes effect without a channel restart.
        """
        config_manager = self.server.config_manager

        with self._lock:

            generation = config_manager.as2_config_generation

            if generation != self._partnerships_generation:

                # The flat configuration dicts of all the AS2 connections
                configs:'dictlist' = []

                for config in config_manager.outconn_as2.values():
                    configs.append(config)

                self._partnerships = build_partnerships(configs)

                # The generation is recorded after the build, so that a build that raised
                # is attempted again rather than remembered as done.
                self._partnerships_generation = generation

            out = self._partnerships

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

    def _get_async_mdn_queue(self) -> 'AsyncMDNQueue':
        """ Returns the queue asynchronous MDNs are persisted in, building it on first use.
        """
        with self._lock:
            if self._async_mdn_queue is None:
                self._async_mdn_queue = AsyncMDNQueue()

            out = self._async_mdn_queue

        return out

# ################################################################################################################################

    def _queue_async_mdn(self, cid:'str', result:'InboundResult', pending:'PendingAsyncMDN') -> 'int':
        """ Persists one asynchronous MDN before the inbound POST is answered, returning the row id
        the delivery can complete it by, or zero when the receipt could not be queued.

        Persisting first is what makes the receipt survive a restart. The alternative - handing it
        straight to a greenlet - loses it if the process stops between accepting the message and
        delivering the receipt, and the sender is then waiting for a receipt nobody will ever send.
        """
        queue = self._get_async_mdn_queue()

        try:
            out = queue.enqueue(result.as2_from, result.as2_to, result.message_id, pending, self.name, cid)

        # The queue is a database write - a receipt that cannot be persisted is still worth
        # attempting once, so this is logged rather than allowed to fail the request that
        # already accepted the message.
        except Exception:
            logger.warning('AS2 async MDN for message `%s` could not be queued on channel `%s`; cid:%s; %s',
                result.message_id, self.name, cid, format_exc())
            return 0

        return out

# ################################################################################################################################

    def _deliver_async_mdn(self, cid:'str', row_id:'int') -> 'None':
        """ Makes the first delivery attempt at one queued asynchronous MDN. Runs in its own
        greenlet - the inbound POST was already answered with HTTP 202 by the time this runs -
        and a failed attempt stays in the queue for the drain job to retry.
        """
        try:
            queue = self._get_async_mdn_queue()

            # The row is read back rather than carried in, so that an attempt the drain job made
            # in the meantime cannot be repeated here on a receipt already delivered.
            if item := queue.get(row_id):
                _ = deliver_async_mdn(queue, item, post_async_mdn, utcnow())

        # Nothing above may propagate out of a greenlet nobody waits on - the receipt stays
        # in the queue either way, which is what the durability is for.
        except Exception:
            logger.warning('AS2 async MDN attempt failed on channel `%s`; cid:%s; %s', self.name, cid, format_exc())

# ################################################################################################################################

    def _claim(self, cid:'str', result:'InboundResult') -> 'bool':
        """ Claims the message so that a replay is detectable, returning whether this request is
        the one that gets to deliver it. Losing the claim turns the result into the replay it
        actually is - the stored MDN of the delivery that won goes back instead of the one
        built here, so both copies of the message get the same answer.
        """
        is_claimed = self.duplicates.claim(
            result.as2_from, result.as2_to, result.message_id, result.status_code, result.body, result.headers)

        if is_claimed:
            return True

        logger.info('AS2 message `%s` was claimed concurrently on channel `%s`, stored MDN returned; cid:%s',
            result.message_id, self.name, cid)

        result.is_duplicate = True
        result.payloads = []

        # The winner's MDN is what the peer is owed. It is normally there, and a claim that was
        # won and then aged out of the retention window between the two calls would leave nothing
        # to read back - in which case the answer stays the MDN built here, which says the same
        # thing about the same message.
        if stored := self.duplicates.get(result.as2_from, result.as2_to, result.message_id):
            result.status_code = stored.status_code
            result.body = stored.body
            result.headers = stored.headers

            if content_type := stored.headers.get('Content-Type'):
                result.content_type = content_type

        return False

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

        # The message is claimed before anything is delivered, so that two concurrent copies of it
        # cannot both pass the duplicate check and both hand the document over. Losing the claim
        # means another greenlet or another server got there first, and the answer is that
        # delivery's own MDN rather than the one just built here.
        if out.message_id:
            if not self._claim(cid, out):
                return out

        # An asynchronous MDN is persisted before the POST is answered, so that a restart resumes
        # its delivery rather than losing the receipt the sender is waiting for. Zero means
        # nothing to deliver from here - either there is no asynchronous receipt at all,
        # or this message's receipt is already queued from an earlier delivery.
        row_id = 0

        if pending := out.pending_async_mdn:
            row_id = self._queue_async_mdn(cid, out, pending)

        # Hand the accepted documents over to their routing targets ..
        self._route(cid, out)

        # .. and attempt the queued receipt in the background, with the drain job retrying
        # whatever this attempt does not get through.
        if row_id:
            _ = spawn(self._deliver_async_mdn, cid, row_id)

        payload_count = len(out.payloads)
        suffix = 'payload' if payload_count == 1 else 'payloads'

        logger.info('AS2 message `%s` accepted on channel `%s`, %d %s routed',
            out.message_id, self.name, payload_count, suffix)

        return out

# ################################################################################################################################
# ################################################################################################################################
