# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

# What a standalone system sends its HL7 to - Zato's MLLP channel on this machine, on the standard HL7 port
# unless the variable says otherwise.
Zato_MLLP_Port_Env = 'Zato_HL7_Zato_MLLP_Port'
Default_Zato_MLLP_Port = 2575

# ################################################################################################################################
# ################################################################################################################################

def zato_mllp_port() -> 'int':
    value = os.environ.get(Zato_MLLP_Port_Env)

    if value:
        out = int(value)
    else:
        out = Default_Zato_MLLP_Port

    return out

# ################################################################################################################################
# ################################################################################################################################
