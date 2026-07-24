# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rate_limiting.common import client_address_headers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# What the address resolves to when no header carries one - the same value the server's HTTP core uses
No_Remote_Address = '(None)'

# ################################################################################################################################
# ################################################################################################################################

def client_address(req:'any_') -> 'str':
    """ Returns the client address of a Django request, resolved the same way the servers do it.
    """
    # Each header is genuinely optional in a request, hence the boundary checks
    for name in client_address_headers:
        if value := req.META.get(name):
            out = value
            break
    else:
        out = No_Remote_Address

    return out

# ################################################################################################################################
# ################################################################################################################################
