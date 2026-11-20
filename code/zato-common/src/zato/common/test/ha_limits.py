# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The limits that the suites of the active-standby pair apply to the steps of a failover.

# ################################################################################################################################
# ################################################################################################################################

class HALimits:

    # How long a server started with the generation of a node may take, from the spawn of its command to the first answer
    # of /zato/ping, in seconds. The start measures 2.9 s in breakdowns/ha-start/03.md of private-zato-perf
    # and 4.3 s while eight other suites run.
    Server_Start = 5.0

# ################################################################################################################################
# ################################################################################################################################
