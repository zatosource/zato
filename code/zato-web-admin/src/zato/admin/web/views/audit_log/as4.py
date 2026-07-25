# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What an AS4 channel or outgoing connection contributes to its own audit log page - the object
its exchanges are filed under, so a row on either page links straight to them.
"""

# Zato
from zato.common.as4.audit import party_pair

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def get_audit_log_object_name(item:'any_') -> 'str':
    """ Returns the object name the exchanges of one AS4 item are recorded under - its two party
    identifiers. Both fields are optional in the get-list response, so either may be missing on an
    item that was saved without it.
    """
    if hasattr(item, 'as4_from_party'):
        from_party = item.as4_from_party
    else:
        from_party = ''

    if hasattr(item, 'as4_to_party'):
        to_party = item.as4_to_party
    else:
        to_party = ''

    # The opaque column genuinely stores a null when an item was saved without a party.
    if from_party is None:
        from_party = ''

    if to_party is None:
        to_party = ''

    out = party_pair(from_party, to_party)
    return out

# ################################################################################################################################
# ################################################################################################################################
