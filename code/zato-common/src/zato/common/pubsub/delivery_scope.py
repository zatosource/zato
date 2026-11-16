# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# gevent
from gevent import getcurrent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeliveryScope:
    """ What the subscriber services of one push delivery batch produce while they process it, which commits
    in the transaction that acknowledges the batch rather than in transactions of its own.
    """

    # The publications that the subscriber services made, as PendingPublication objects
    publications: 'anylist'

    # The audit events of the batch, as PendingEvent objects
    audit_events: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

# The scope of each greenlet that delivers a batch, by the greenlet
_scopes:'anydict' = {}

# ################################################################################################################################

def open_delivery_scope() -> 'DeliveryScope':
    """ Opens the scope of the batch that the current greenlet delivers.
    """
    out = DeliveryScope()
    out.publications = []
    out.audit_events = []

    _scopes[getcurrent()] = out

    return out

# ################################################################################################################################

def close_delivery_scope() -> 'None':
    """ Closes the scope of the batch that the current greenlet delivered.
    """
    del _scopes[getcurrent()]

# ################################################################################################################################

def get_delivery_scope() -> 'DeliveryScope | None':
    """ Returns the scope of the batch that the current greenlet delivers, or None outside of a delivery batch.
    """
    out = _scopes.get(getcurrent())
    return out

# ################################################################################################################################
# ################################################################################################################################
