# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Delivering one message to the destinations of one channel. The destination that produces the
# caller's reply is delivered to first and while the caller waits, because its answer is the
# answer, and its failure is the channel's failure. Everything else happens once the caller
# already has its reply, either all at once or one after another, each delivery isolated so
# that one destination being down is one red row rather than a message nobody received.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from time import monotonic

# Zato
from zato.common.audit_log.common import AuditClassification, AuditOutcome, derive_classification
from zato.common.destination.audit import record_hop
from zato.common.destination.constants import Default_Retry_Count, Default_Retry_Sleep_Seconds, DeliveryMode, \
    Respond_From_Service
from zato.common.destination.payload import resolve_payload
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.destination.model import ChannelDestinationConfig, DestinationEntry
    from zato.common.destination.payload import PayloadOverrides
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
hop_result_list = list['HopResult']
planned_hop_list = list['PlannedHop']

# ################################################################################################################################
# ################################################################################################################################

# How many milliseconds one second has, for the duration each delivery is recorded with
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeliveryTransports:
    """ How the coordinator reaches the outside world, injected by the layer that owns
    the connections - the coordinator decides what is delivered and in what order,
    the transports perform each delivery.
    """

    # send(entry, payload, cid) - delivers one payload through one destination and returns
    # whatever the connection answered with. The cid ties the rows the connection itself
    # writes to the hop rows the coordinator writes.
    send: 'callable_' = None

    # sleep(seconds) - waits between two attempts at the same destination.
    sleep: 'callable_' = None

    # spawn(function, *args) - runs the deliveries the caller does not wait for.
    spawn: 'callable_' = None

# ################################################################################################################################

@dataclass(init=False)
class DeliveryContext:
    """ Everything the deliveries of one message share.
    """

    # The channel the destinations belong to.
    channel_name: str = ''

    # The correlation id of the message that came in - every delivery is recorded under it.
    cid: str = ''

    # How the deliveries reach the outside world.
    transports: 'DeliveryTransports'

    # Where every attempt is recorded.
    audit_log: 'AuditLog'

    # How many further attempts one delivery gets after its first one failed.
    retry_count: int = Default_Retry_Count

    # How long to wait before another attempt at the same destination.
    retry_sleep_seconds: float = Default_Retry_Sleep_Seconds

# ################################################################################################################################

@dataclass(init=False)
class PlannedHop:
    """ One destination and the payload it is to receive.
    """

    entry: 'DestinationEntry'
    payload: 'any_' = None

    # The place the destination takes in the order they were declared in.
    sequence: int = 0

# ################################################################################################################################

@dataclass(init=False)
class HopResult:
    """ What delivering to one destination came to.
    """

    destination_name: str = ''
    connection: str = ''
    sequence: int = 0

    # How many attempts it took, successful or not.
    attempt_count: int = 0

    is_ok: bool = False

    # What the connection answered with, when it answered at all.
    response: 'any_' = None

    # What stopped the delivery, when something did.
    error: str = ''

# ################################################################################################################################

@dataclass(init=False)
class DeliveryResult:
    """ What delivering one message to one channel's destinations came to. The reply is
    filled in only when a destination produced it - the caller keeps its own otherwise.
    """

    has_response: bool = False
    response: 'any_' = None

    # The deliveries the caller waited for - the ones spawned are not here,
    # their outcome is in the audit trail alone.
    hops: 'hop_result_list' = list_field()

# ################################################################################################################################
# ################################################################################################################################

def new_transports(send:'callable_', sleep:'callable_', spawn:'callable_') -> 'DeliveryTransports':
    """ Builds the transports one delivery run uses.
    """

    # Our response to produce
    out = DeliveryTransports()

    out.send = send
    out.sleep = sleep
    out.spawn = spawn

    return out

# ################################################################################################################################

def new_context(
    channel_name:'str',
    cid:'str',
    transports:'DeliveryTransports',
    audit_log:'AuditLog',
    *,
    retry_count:'int' = Default_Retry_Count,
    retry_sleep_seconds:'float' = Default_Retry_Sleep_Seconds,
    ) -> 'DeliveryContext':
    """ Builds the context the deliveries of one message share.
    """

    # Our response to produce
    out = DeliveryContext()

    out.channel_name = channel_name
    out.cid = cid
    out.transports = transports
    out.audit_log = audit_log
    out.retry_count = retry_count
    out.retry_sleep_seconds = retry_sleep_seconds

    return out

# ################################################################################################################################

def plan_hops(
    config:'ChannelDestinationConfig',
    overrides:'PayloadOverrides',
    request_payload:'any_',
    ) -> 'planned_hop_list':
    """ Works out which destinations receive something and what each of them receives, keeping
    the order they were declared in. A destination that is not active and one the service
    dropped are both left out.
    """
    out:'planned_hop_list' = []
    sequence = 0

    for entry in config.entries:

        if not entry.is_active:
            continue

        payload = resolve_payload(entry.name, overrides, request_payload)

        # The service dropped this destination for this message alone
        if payload is None:
            continue

        planned = PlannedHop()

        planned.entry = entry
        planned.payload = payload
        planned.sequence = sequence

        out.append(planned)

        sequence += 1

    return out

# ################################################################################################################################

def _is_worth_another_attempt(error:'str') -> 'bool':
    """ Tells whether the same message can work at the same destination a moment later.
    A failure that says the message itself is wrong never can, everything else may.
    """
    classification = derive_classification(AuditOutcome.Error, error)
    out = classification != AuditClassification.Permanent

    return out

# ################################################################################################################################

def deliver_hop(context:'DeliveryContext', planned:'PlannedHop') -> 'HopResult':
    """ Delivers one payload to one destination, trying again for as long as the failure is one
    another attempt can get past. Every attempt is recorded, the last one included, so a
    delivery that never got through is a row somebody can act on.
    """
    entry = planned.entry
    transports = context.transports

    # Our response to produce
    out = HopResult()

    out.destination_name = entry.name
    out.connection = entry.connection
    out.sequence = planned.sequence

    attempt = 0

    while True:

        attempt += 1
        out.attempt_count = attempt
        attempt_start = monotonic()
        error = ''

        # The delivery itself, whatever it is that the destination's type does ..
        try:
            response = transports.send(entry, planned.payload, context.cid)

        # .. a delivery that raised has its error recorded and may be tried again ..
        except Exception as e:
            error = str(e)
            out.error = error
            out.is_ok = False

        # .. and one that went through is the end of it.
        else:
            out.response = response
            out.error = ''
            out.is_ok = True

        duration_ms = int((monotonic() - attempt_start) * _ms_per_second)

        _ = record_hop(
            context.audit_log,
            context.channel_name,
            entry,
            planned.payload,
            cid=context.cid,
            sequence=planned.sequence,
            attempt=attempt,
            duration_ms=duration_ms,
            error=error,
        )

        if out.is_ok:
            break

        # A message the destination will never accept is not sent again ..
        if not _is_worth_another_attempt(error):
            break

        # .. neither is one that has had all the attempts it is allowed ..
        if attempt > context.retry_count:
            break

        # .. and one that may still get through waits before trying again.
        transports.sleep(context.retry_sleep_seconds)

    return out

# ################################################################################################################################

def deliver_in_order(context:'DeliveryContext', planned_list:'planned_hop_list') -> 'None':
    """ Delivers to each destination in turn, one failing being one failure rather than
    the end of the run.
    """
    for planned in planned_list:
        _ = deliver_hop(context, planned)

# ################################################################################################################################

def _spawn_remaining(context:'DeliveryContext', config:'ChannelDestinationConfig',
    planned_list:'planned_hop_list') -> 'None':
    """ Hands the deliveries the caller does not wait for over to the transports, either as
    one run through all of them or as one run each.
    """
    spawn = context.transports.spawn

    # One after another means one run through the whole list, in the order it is in ..
    if config.delivery_mode == DeliveryMode.In_Order:
        spawn(deliver_in_order, context, planned_list)

    # .. and all at once means each destination on its own, none waiting for another.
    else:
        for planned in planned_list:
            spawn(deliver_hop, context, planned)

# ################################################################################################################################

def deliver(
    context:'DeliveryContext',
    config:'ChannelDestinationConfig',
    overrides:'PayloadOverrides',
    request_payload:'any_',
    ) -> 'DeliveryResult':
    """ Delivers one message to every destination of one channel. The destination the channel
    replies from goes first and its failure is the caller's failure, the rest follow once the
    caller has its reply.
    """
    planned_list = plan_hops(config, overrides, request_payload)

    # Our response to produce
    out = DeliveryResult()

    out.hops = []

    # The channel may reply from one of its destinations rather than from its service ..
    if config.respond_from != Respond_From_Service:

        for planned in planned_list:
            if planned.entry.name == config.respond_from:
                responding = planned
                break

        # .. that destination not receiving this message means nobody replies in its place ..
        else:
            responding = None

        if responding:
            planned_list.remove(responding)

            hop = deliver_hop(context, responding)
            out.hops.append(hop)

            # .. and its failure is what the caller learns about, the remaining destinations
            # never being reached at all.
            if not hop.is_ok:
                raise Exception(
                    f'Channel `{config.channel_name}` could not deliver to `{hop.destination_name}`; e:`{hop.error}`')

            out.has_response = True
            out.response = hop.response

    _spawn_remaining(context, config, planned_list)

    return out

# ################################################################################################################################
# ################################################################################################################################
