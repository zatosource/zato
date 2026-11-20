# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a test waits after its last file arrived, so that a file processed twice has the time to arrive again,
    # when nothing tells it when the server listed the directories again, in seconds
    Settle_Seconds = 2

# ################################################################################################################################
# ################################################################################################################################

class SettleBarrier:
    """ Tells a test when no more files can arrive from what it produced. A server does not report its runs,
    so the test waits for a fixed time, longer than the interval of the schedules.
    """
    what = f'{ModuleCtx.Settle_Seconds}s after the last file'

    def begin(self) -> 'callable_':
        """ Returns a condition that holds once the files that a run started now would process have arrived.
        """
        until = monotonic() + ModuleCtx.Settle_Seconds

        def _is_settled() -> 'bool':
            out = monotonic() >= until
            return out

        return _is_settled

# ################################################################################################################################
# ################################################################################################################################
