# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

class MessageIdentity(NamedTuple):
    """ What makes one received message the same message when it arrives again.
    """
    protocol:   str
    from_party: str
    to_party:   str
    message_id: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredResponse:
    """ The response signal that answered a received message, kept so that a duplicate gets the same one.
    """
    status_code:    int
    content_type:   str
    body:           bytes
    is_synchronous: bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredMessage:
    """ One received message as the store remembers it.
    """
    status:      str
    received_at: 'datetime'
    expires_at:  'datetime'
    response:    StoredResponse

# ################################################################################################################################
# ################################################################################################################################
