# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.ebms2.outbound import build, SendOptions
from zato.common.b2b.ebms2.outbound_record import new_sent_message, restore_outbound
from zato.common.b2b.ebms2.packaging import unpack

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.common.send_log import SendLog
    from zato.common.b2b.ebms2.agreement import Agreement
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    Agreement = Agreement
    Clock = Clock
    LocalKeys = LocalKeys
    OutboundMessage = OutboundMessage
    SendLog = SendLog

# ################################################################################################################################
# ################################################################################################################################

def reprocess(
    send_log:'SendLog',
    agreement:'Agreement',
    local_keys:'LocalKeys',
    message_id:'str',
    clock:'Clock',
    ) -> 'OutboundMessage':
    """ Builds a new message out of the payloads of a sent one, read from its stored bytes, under a new MessageId
    in the same conversation and under the same binding, and records its first delivery, linked to the original.
    An exchange of the original that has not ended ends as superseded. Sending the new message is left to the caller.
    """
    original = send_log.get(message_id)
    body = send_log.wire_body(message_id)

    unpacked = unpack(original.wire_headers, body)
    restored = restore_outbound(agreement, local_keys, original)

    options = SendOptions()
    options.conversation_id = restored.header.conversation_id
    options.ref_to_message_id = restored.header.message_data.ref_to_message_id

    out = build(agreement, local_keys, restored.binding, unpacked.payloads, clock, options)

    sent = new_sent_message(out, out.package)
    send_log.record_reprocess(original, sent)

    return out

# ################################################################################################################################
# ################################################################################################################################
