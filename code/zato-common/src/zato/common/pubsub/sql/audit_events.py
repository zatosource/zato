# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.payload import prepare_payloads
from zato.common.pubsub.sql.pending import PendingAtomic, PendingPublication

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.pending import pending_atomic_list, pending_lease_list, pending_publication_list
    from zato.common.typing_ import anylist

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    pending_atomic_list = pending_atomic_list
    pending_lease_list = pending_lease_list
    pending_publication_list = pending_publication_list
    PendingPublication = PendingPublication

# ################################################################################################################################
# ################################################################################################################################

def _add_publication_events(out:'anylist', pending:'PendingPublication') -> 'None':
    """ Adds the audit events of a publication that wrote its message.
    """
    if not pending.exception and not pending.is_repeat:
        out.extend(pending.audit_events)

# ################################################################################################################################

def collect_audit_events(
    publications:'pending_publication_list',
    atomics:'pending_atomic_list',
    leases:'pending_lease_list',
    ) -> 'anylist':
    """ Returns the audit events that commit in the transaction of the given items - those of each publication
    that wrote its message, those of each fenced acknowledgement with those of the publications it wrote,
    and those of each lease.
    """
    out:'anylist' = []

    for pending in publications:
        _add_publication_events(out, pending)

    # The deliveries that a fenced acknowledgement concludes took place whether or not the acknowledgement is written ..
    for atomic in atomics:
        out.extend(atomic.audit_events)

        # .. whereas its publications exist only if it is written.
        if not atomic.exception:
            for pending in atomic.publications:
                _add_publication_events(out, pending)

    for lease in leases:
        out.extend(lease.audit_events)

    return out

# ################################################################################################################################

def prepare_audit_payloads(batch:'anylist') -> 'None':
    """ Prepares the payloads of the audit events that the items of a batch carry before the batch is written,
    which are those of the publications and of the fenced acknowledgements with their publications.
    The audit events of a pull are built in the transaction that leases its messages.
    """
    events:'anylist' = []

    for item in batch:
        if isinstance(item, PendingPublication):
            events.extend(item.audit_events)

        elif isinstance(item, PendingAtomic):
            events.extend(item.audit_events)

            for pending in item.publications:
                events.extend(pending.audit_events)

    prepare_payloads(events)

# ################################################################################################################################

def drop_audit_events(batch:'anylist') -> 'None':
    """ Removes the audit events that the publications and the fenced acknowledgements of a batch were built with,
    for a batch that commits after the audit log was turned off. The audit events of a pull are built
    in the transaction that leases its messages, which reads the switch itself.
    """
    for item in batch:
        if isinstance(item, PendingPublication):
            item.audit_events.clear()

        elif isinstance(item, PendingAtomic):
            item.audit_events.clear()

            for pending in item.publications:
                pending.audit_events.clear()

# ################################################################################################################################
# ################################################################################################################################
