# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.common.outcome import SignalKind
from zato.common.b2b.ebms2.outbound import build

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.agreement import Agreement, Binding
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    Agreement = Agreement
    Binding = Binding
    Clock = Clock
    LocalKeys = LocalKeys
    OutboundMessage = OutboundMessage

# ################################################################################################################################
# ################################################################################################################################

def build_ping(agreement:'Agreement', local_keys:'LocalKeys', binding:'Binding', clock:'Clock') -> 'OutboundMessage':
    """ Builds the Ping that probes a suspended address, under the binding of the Ping service of the message service
    handler. Sending it is left to the caller, which passes the response to accept_response.
    """
    out = build(agreement, local_keys, binding, [], clock)
    return out

# ################################################################################################################################

def is_pong(outbound:'OutboundMessage') -> 'bool':
    """ Says whether a Ping was answered with a Pong, which means that its address accepts messages again.
    """
    out = outbound.outcome.signal_kind == SignalKind.Pong
    return out

# ################################################################################################################################
# ################################################################################################################################
