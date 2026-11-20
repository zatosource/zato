# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The client libraries of Microsoft 365, which a client imports when it builds its account on first use.

# stdlib
from warnings import catch_warnings

# MSAL
from msal import ConfidentialClientApplication as ConfidentialClientApplication

# Office-365 - importing it sets every DeprecationWarning to always show whenever Python runs with any -W option,
# which the warning filters of the process are restored from once the import completes.
with catch_warnings():
    from O365 import Account as Account
    from O365.connection import MSGraphProtocol as MSGraphProtocol
    from O365.utils.token import MemoryTokenBackend as MemoryTokenBackend

# ################################################################################################################################
# ################################################################################################################################
