# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.pending import PendingPublication, pending_atomic_list, pending_lease_list, \
        pending_publication_list
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
# ################################################################################################################################
