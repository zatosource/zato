# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from datetime import datetime, timezone
from time import sleep

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Run_Log = 'Zato_Test_Scheduler_Run_Log'
    Env_Server_Label = 'Zato_Test_Scheduler_Server_Label'
    Zato_Ctx_Key = 'zato.zato_ctx'

# ################################################################################################################################
# ################################################################################################################################

class RecordRun(Service):
    """ Appends the start and the end of each run of a scheduler job to the run log of this server, with the job,
    its nominal slot, the server and the time, and runs for as many seconds as the payload of the job requests.
    """
    name = 'test.scheduler.failover.record-run'

    def _append(self, entry:'dict') -> 'None':
        path = os.environ[ModuleCtx.Env_Run_Log]
        line = json.dumps(entry) + '\n'

        with open(path, 'a') as run_log:
            _ = run_log.write(line)

    def handle(self) -> 'None':

        payload = self.request.payload
        zato_ctx = self.request_ctx[ModuleCtx.Zato_Ctx_Key]

        entry = {
            'job': payload['job'],
            'slot': zato_ctx['scheduler_nominal_fire_time'],
            'run': zato_ctx['scheduler_current_run'],
            'server': os.environ[ModuleCtx.Env_Server_Label],
            'phase': 'start',
            'time': datetime.now(timezone.utc).timestamp(),
        }

        # The run is recorded as begun before it does its work ..
        self._append(entry)

        sleep(payload['run_seconds'])

        # .. and as completed once the work is done.
        entry['phase'] = 'end'
        entry['time'] = datetime.now(timezone.utc).timestamp()

        self._append(entry)

# ################################################################################################################################
# ################################################################################################################################
