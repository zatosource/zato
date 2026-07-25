# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import deepcopy
from functools import partial
from threading import RLock

# Zato
from zato.common.api import AS4
from zato.common.as4.audit import record_inbound_result, record_message_handed_over
from zato.common.as4.common import AS4ProtocolException, EbMSError, Peppol_Not_Serviced
from zato.common.as4.config import apply_credentials, build_keystore, build_pmodes, get_text_field
from zato.common.as4.inbound import handle as inbound_handle, PullServed
from zato.common.as4.mpc import build_response, claim_next, complete
from zato.common.as4.reconcile import ReceiptReconciler
from zato.common.as4.resubmit import Target_Service, Target_Topic
from zato.common.as4.sbdh import parse_sbdh
from zato.common.audit_log.api import AuditLog
from zato.server.connection.as4.routing import build_routed_message, build_routed_signal

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import UserMessageDetails
    from zato.common.as4.inbound import InboundResult, pmode_list
    from zato.common.as4.mpc import QueuedMessage
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import anylist, anytuple, stranydict
    anytuple = anytuple
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import part_list
    from zato.server.base.parallel import ParallelServer
    anylist = anylist
    PMode = PMode
    QueuedMessage = QueuedMessage

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AS4ChannelRuntime:
    """ The runtime representation of one AS4 channel - its P-Modes, keystore,
    serviced participants and routing target, built from the channel's configuration.
    """

    def __init__(self, server:'ParallelServer', config:'stranydict') -> 'None':
        self.server = server
        self.config = config
        self.name = config['name']

        # The runtime P-Modes and keystore are built lazily, on first use,
        # so that incomplete configuration does not break config propagation.
        self._lock = RLock()
        self._pmodes:'pmode_list | None' = None
        self._keystore:'Keystore | None' = None

        # The participants this channel accepts documents for - one per line,
        # an empty list means every participant is accepted. The opaque column
        # genuinely stores a null when the channel was saved without any.
        serviced_participants = config['as4_serviced_participants']
        if serviced_participants is None:
            serviced_participants = ''

        participants = set()

        for line in serviced_participants.splitlines():
            line = line.strip()
            if line:
                participants.add(line)

        self.serviced_participants = participants

        # Where accepted messages go - the channel's service when one is configured,
        # its pub/sub topic otherwise.
        self.service_name = config['service_name']

        topic_name = config['as4_inbound_topic']
        if not topic_name:
            topic_name = AS4.Default.Inbound_Topic
        self.inbound_topic = topic_name

        # Signals that arrive on their own go to their own topic - what they carry is an outcome of an
        # earlier message of ours, not a document to process.
        self.signal_topic = AS4.Default.Signal_Topic

        # The two identifiers of the exchange this channel takes part in - a signal arriving on its
        # own names no parties of its own, so these are what place it. On a channel the initiator is
        # the partner and the responder is this access point.
        self.partner_party = config['as4_from_party']
        self.own_party = config['as4_to_party']

        # A channel with a message partition channel configured answers the partner's pull requests
        # for it, and for any sub-channel of it. One without it takes deliveries only.
        self.pull_mpc = get_text_field(config, 'as4_mpc')

        # A channel whose audit log was turned off writes no events. The flag lives in an opaque
        # attribute, so a channel saved before it existed carries a null, which means it was
        # never turned off.
        is_audit_log_active = config['is_audit_log_active']

        if is_audit_log_active is None:
            is_audit_log_active = True

        self.needs_audit = is_audit_log_active

        if self.needs_audit:
            self.audit_log = AuditLog(server.name)

            # A receipt that arrives on its own echoes only the id of the message it answers, so
            # the store is what turns that id back into the exchange the receipt closes.
            self.reconciler = ReceiptReconciler(server.name)

# ################################################################################################################################

    def _get_pmodes(self) -> 'pmode_list':
        """ Returns this channel's P-Modes, building them on first use.
        """
        with self._lock:
            if self._pmodes is None:
                pmodes = build_pmodes(self.config)

                # Every P-Mode of one channel asks for the same credentials, because they are what
                # the partner on the other end of it was given.
                for pmode in pmodes:
                    apply_credentials(pmode, self.config, self.server.decrypt)

                self._pmodes = pmodes

            out = self._pmodes

        return out

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

    def _duplicate_cache_key(self, message_id:'str') -> 'str':
        out = AS4.Default.Duplicate_Cache_Prefix + message_id
        return out

# ################################################################################################################################

    def _is_duplicate(self, message_id:'str') -> 'bool':
        """ Claims an eb:MessageId for this delivery and returns True if it was already claimed. The
        claim and the check are one cache operation, so two servers receiving the same message at the
        same time still deliver it once. The claim lasts for the duplicate detection window.
        """
        cache = self.server.config_manager.cache_api
        key = self._duplicate_cache_key(message_id)

        claimed = cache.set_if_absent(key, True, expiry=AS4.Default.Duplicate_Detection_TTL)

        out = not claimed
        return out

# ################################################################################################################################

    def _release_duplicate_claim(self, message_id:'str') -> 'None':
        """ Gives up the claim on an eb:MessageId. The claim says the message was delivered, so it
        has to go when the delivery did not happen after all - the sender's retry is then a first
        delivery rather than a replay.
        """
        cache = self.server.config_manager.cache_api
        key = self._duplicate_cache_key(message_id)

        cache.delete(key)

# ################################################################################################################################

    def _validate(self, user_message:'UserMessageDetails', payloads:'part_list') -> 'anylist':
        """ Rejects Peppol documents addressed to a participant this channel does not serve,
        the way the Peppol AS4 profile requires. Returns what was read out of each payload while
        validating it, one entry per payload, so that routing reads none of it again.
        """
        _ = user_message

        # Our response to produce
        out:'anylist' = []

        # Only the Peppol profile carries SBDH-wrapped documents.
        if self.config['as4_profile'] != AS4.Profile.Peppol:

            for _ in payloads:
                out.append(None)

            return out

        for payload in payloads:
            sbdh_details, _ = parse_sbdh(payload.data)

            # A receiver outside the serviced list is answered with the error signal and detail the
            # Peppol profile defines for this case. No configured participants accepts everyone.
            if self.serviced_participants:
                if sbdh_details.receiver_id not in self.serviced_participants:
                    raise AS4ProtocolException(EbMSError.Other, Peppol_Not_Serviced)

            out.append(sbdh_details)

        return out

# ################################################################################################################################

    def _route(self, cid:'str', user_message:'UserMessageDetails', result:'InboundResult') -> 'None':
        """ Hands each accepted payload over to the channel's routing target.
        """
        profile = self.config['as4_profile']

        for payload, sbdh_details in zip(result.payloads, result.payload_details):

            message = build_routed_message(profile, user_message, payload, sbdh_details)

            # A configured service receives the message directly ..
            if self.service_name:
                _ = self.server.invoke(self.service_name, message)

            # .. without one, the message goes to the channel's topic, which is where
            # reliability lives - redelivery and retries are pub/sub's built-in behavior.
            else:
                _ = self.server.pubsub_backend.publish(self.inbound_topic, message, cid=cid, correl_id=cid)

# ################################################################################################################################

    def get_target(self) -> 'anytuple':
        """ Returns what this channel routes accepted payloads to - its service when one is
        configured, its topic otherwise.
        """
        if self.service_name:
            out = Target_Service, self.service_name
        else:
            out = Target_Topic, self.inbound_topic

        return out

# ################################################################################################################################

    def route_again(self, cid:'str', user_message:'UserMessageDetails', payloads:'part_list') -> 'anylist':
        """ Routes the payloads of a message that was already received once, to the target this
        channel routes live deliveries to - the reprocess of a delivery whose recipient system was
        down. Returns every message that was routed, so an operator sees how many went out.

        Duplicate detection has no say here, because the whole point is to deliver again what was
        already delivered once.
        """
        profile = self.config['as4_profile']

        # The identifiers a Peppol payload is routed by are in the payload itself, so they are read
        # again the way a live delivery reads them.
        payload_details = self._validate(user_message, payloads)

        # Our response to produce
        out:'anylist' = []

        for payload, sbdh_details in zip(payloads, payload_details):

            message = build_routed_message(profile, user_message, payload, sbdh_details)
            out.append(message)

            if self.service_name:
                _ = self.server.invoke(self.service_name, message)
            else:
                _ = self.server.pubsub_backend.publish(self.inbound_topic, message, cid=cid, correl_id=cid)

        return out

# ################################################################################################################################

    def _route_signals(self, cid:'str', result:'InboundResult') -> 'None':
        """ Hands each signal that arrived on its own over to the channel's routing target. These are
        receipts and errors for messages this server sent earlier, so they go to their own topic
        rather than to the one payloads arrive on.
        """
        for signal in result.signals:

            message = build_routed_signal(signal)

            if self.service_name:
                _ = self.server.invoke(self.service_name, message)
            else:
                _ = self.server.pubsub_backend.publish(self.signal_topic, message, cid=cid, correl_id=cid)

# ################################################################################################################################

    def _pull_pmode(self, pmode:'PMode', queued:'QueuedMessage') -> 'PMode':
        """ Returns the P-Mode one queued message is handed over under - the one governing the channel
        it waited on, with the business information the message was queued with.

        The parties are the other way round from a delivery arriving here, because a message handed
        over on a pull travels out from this access point.
        """
        out = deepcopy(pmode)

        out.mpc = queued.mpc
        out.service = queued.service
        out.action = queued.action

        out.initiator.party_id = queued.from_party
        out.responder.party_id = queued.to_party

        return out

# ################################################################################################################################

    def _record_pull_served(
        self,
        cid:'str',
        queued:'QueuedMessage',
        payloads:'part_list',
        body:'bytes',
        ) -> 'None':
        """ Records the message one pull request was answered with. It went out from here, so it is
        recorded the way a push is - a receipt for it is what closes the exchange.
        """
        if not self.needs_audit:
            return

        record_message_handed_over(self.audit_log, queued.from_party, queued.to_party,
            message_id=queued.message_id, conversation_id=queued.conversation_id, service=queued.service,
            action=queued.action, payloads=payloads, raw_message=body, cid=cid)

# ################################################################################################################################

    def _serve_pull(self, cid:'str', mpc:'str', pmode:'PMode') -> 'PullServed | None':
        """ Hands over the message that has waited longest on one message partition channel, or
        nothing at all when the channel is empty, which is what the pull request is then told.

        The message is signed and encrypted as the P-Mode of its channel says, exactly as a pushed
        message would be, because it is the same message travelling the other way around.
        """
        queued = claim_next(mpc)

        if queued is None:
            logger.info('AS4 pull of `%s` found no message on channel `%s`; cid:%s', mpc, self.name, cid)
            return None

        pull_pmode = self._pull_pmode(pmode, queued)
        keystore = self._get_keystore()

        body, content_type, submitted = build_response(pull_pmode, keystore, queued)

        self._record_pull_served(cid, queued, submitted, body)

        logger.info('AS4 pull of `%s` handed over message `%s` on channel `%s`; attempt:%d; cid:%s',
            mpc, queued.message_id, self.name, queued.pull_count, cid)

        # Our response to produce
        out = PullServed()

        out.body = body
        out.content_type = content_type
        out.message_id = queued.message_id
        out.payloads = submitted

        return out

# ################################################################################################################################

    def _close_pulled(self, result:'InboundResult') -> 'None':
        """ Closes the queue row of each message a receipt in this request acknowledges. A receipt
        answering a pushed message closes no row, which is what the store says by finding none.
        """
        for signal in result.signals:

            if not signal.is_receipt:
                continue

            ref_to_message_id = signal.ref_to_message_id

            if not ref_to_message_id:
                continue

            if complete(ref_to_message_id):
                logger.info('AS4 pulled message `%s` acknowledged on channel `%s`',
                    ref_to_message_id, self.name)

# ################################################################################################################################

    def _record(self, cid:'str', body:'bytes', result:'InboundResult') -> 'None':
        """ Records what one incoming request produced - the message and the signal answering it, or
        the signals it delivered for messages sent from here.
        """
        if not self.needs_audit:
            return

        record_inbound_result(self.audit_log, result, body, cid,
            own_party=self.own_party, partner_party=self.partner_party, reconciler=self.reconciler)

# ################################################################################################################################

    def handle(self, cid:'str', body:'bytes', content_type:'str') -> 'InboundResult':
        """ Runs one incoming request through the AS4 inbound pipeline
        and routes whatever payloads it accepted.
        """
        pmodes = self._get_pmodes()
        keystore = self._get_keystore()

        # Only a channel that has a partition channel of its own answers pull requests - without one
        # there is nothing for a partner to ask about and the request is refused.
        if self.pull_mpc:
            serve_pull = partial(self._serve_pull, cid)
        else:
            serve_pull = None

        out = inbound_handle(
            body,
            content_type,
            pmodes,
            keystore,
            is_duplicate=self._is_duplicate,
            validate=self._validate,
            serve_pull=serve_pull,
        )

        # The evidence is written before anything is routed - what arrived and what was answered
        # with is the same whether the routing that follows succeeds or not.
        self._record(cid, body, out)

        # Only messages that were accepted and are not replays carry payloads to route.
        user_message = out.user_message

        if user_message:

            message_id = user_message.message_id

            # A routing failure means the message was not delivered, so the claim that duplicate
            # detection placed on this message id has to go with it.
            try:
                self._route(cid, user_message, out)
            except Exception:
                self._release_duplicate_claim(message_id)
                raise

            payload_count = len(out.payloads)
            suffix = 'payload' if payload_count == 1 else 'payloads'

            logger.info('AS4 message `%s` accepted on channel `%s`, %d %s routed',
                message_id, self.name, payload_count, suffix)

        # Signals arrive without a user message - they are about an earlier message of ours.
        elif out.signals:

            # A receipt among them may be the one closing a message this channel handed over
            # on a pull, in which case that message is done waiting.
            self._close_pulled(out)

            self._route_signals(cid, out)

            signal_count = len(out.signals)
            suffix = 'signal' if signal_count == 1 else 'signals'

            logger.info('AS4 %d %s delivered on channel `%s`; cid:%s', signal_count, suffix, self.name, cid)

        elif out.is_error:
            logger.warning('AS4 request rejected with `%s` on channel `%s`; cid:%s', out.error_code, self.name, cid)

        return out

# ################################################################################################################################
# ################################################################################################################################
