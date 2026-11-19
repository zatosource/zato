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
    from live_windows.peer_server import PeerServer, ScheduleRunner
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

    def on_activity(self) -> 'None':
        """ Called when a guest reports a file that a schedule may pick up.
        """

# ################################################################################################################################
# ################################################################################################################################

class RunBarrier(SettleBarrier):
    """ Tells a test when no more files can arrive from what it produced, by the runs of the schedules of the peer.
    Once each schedule completed a run that started after the last file arrived, a file processed twice has been processed.
    """
    what = 'a run of each schedule after the last file'

    def __init__(self, peer:'PeerServer') -> 'None':
        self.peer = peer

    def begin(self) -> 'callable_':

        targets:'list[tuple[ScheduleRunner, int]]' = []

        for runner in self.peer.schedule_runners():
            target = runner.started_runs + 1
            targets.append((runner, target))

        self.peer.wake()

        def _is_settled() -> 'bool':
            for runner, target in targets:
                if runner.completed_runs < target:
                    return False
            return True

        return _is_settled

    def on_activity(self) -> 'None':
        """ Starts the next run of each schedule at once, so that a file is picked up without waiting for the interval.
        """
        self.peer.wake()

# ################################################################################################################################
# ################################################################################################################################
