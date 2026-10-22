# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class Limits:
    """ What one incoming message is allowed to be. These ceilings apply before an agreement is matched,
    so they are the same for every exchange.
    """
    # How many payload parts one message may have, the part with the SOAP envelope not included.
    Max_Part_Count = 16

    # How large one incoming message may be on the wire, all of its MIME parts included.
    Max_Message_Size_Bytes = 64 * 1024 * 1024

    # The smallest RSA key a message or a receipt may be signed with.
    Min_RSA_Key_Size_Bits = 2048

# ################################################################################################################################
# ################################################################################################################################
