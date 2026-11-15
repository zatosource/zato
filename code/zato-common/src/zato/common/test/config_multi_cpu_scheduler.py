# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class SchedulerConfig:
    """ The jobs of the scheduler suite and the file in which the service of the jobs records each run.
    """

    # The variable with the path of the file that receives one line for the start and one for the end of each run,
    # which every worker appends to
    Fire_Log_Env = 'Zato_Test_Multi_CPU_Fire_Log'

    # The key of the request context under which the server passes the details of a scheduled run
    Zato_Ctx_Key = 'zato.zato_ctx'

    Record_Service = 'test.multi-cpu.record-fire'

    Phase_Start = 'start'
    Phase_End = 'end'

    # The job whose runs complete at once and the job whose runs take longer than its interval
    Quick_Job = 'test.multi-cpu.scheduler.quick'
    Slow_Job = 'test.multi-cpu.scheduler.slow'

    # The job whose interval a test changes
    Changed_Job = 'test.multi-cpu.scheduler.changed'

    Interval_Seconds = 1
    Changed_Interval_Seconds = 3
    Slow_Run_Seconds = 3

# ################################################################################################################################
# ################################################################################################################################
