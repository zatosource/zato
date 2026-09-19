# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from time import sleep, time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the ceiling in seconds - unset means the wait has no ceiling
Ready_Timeout_Env = 'Zato_Test_Container_Ready_Timeout'

# How long to sleep between two attempts
Ready_Sleep = 1

# After how many attempts the wait reports its progress
Ready_Report_Every = 10

# ################################################################################################################################
# ################################################################################################################################

class WaitOver(Exception):
    """ Raised by a check that knows the system is not going to become ready - nothing is left to wait for,
    and the message says why.
    """

class ContainerExited(WaitOver):
    """ Raised by a check when the container it watches is gone.
    """

class StartupFailed(WaitOver):
    """ Raised by a check when the system's own log says its startup failed, a deployment among it.
    """

# ################################################################################################################################
# ################################################################################################################################

def _read_timeout() -> 'float':
    """ Returns the ceiling from the environment, 0 when there is none.
    """
    if value := os.environ.get(Ready_Timeout_Env):
        out = float(value)
    else:
        out = 0.0

    return out

# ################################################################################################################################

def wait_until(check:'callable_', what:'str') -> 'None':
    """ Polls check once a second until it returns True. An exception raised by check counts as not ready,
    except for WaitOver and its kinds, which end the wait at once. Gives up otherwise only when
    Zato_Test_Container_Ready_Timeout is set and that many seconds have passed.
    """
    timeout = _read_timeout()
    has_timeout = timeout > 0

    start = time()
    last_error = ''
    attempt_count = 0

    while True:

        # One attempt - a check that raises is a check that says no, unless it says the wait is over ..
        try:
            is_ready = check()
        except WaitOver:
            raise
        except Exception as e:
            is_ready = False
            last_error = str(e)

        # .. the moment it says yes we are done ..
        if is_ready:
            return

        # .. a long wait reports that it is still alive and what it last saw ..
        attempt_count += 1

        if attempt_count % Ready_Report_Every == 0:
            elapsed = int(time() - start)
            print(f'Still waiting for {what}, attempt {attempt_count}, {elapsed}s, last error: {last_error}', flush=True)

        # .. and the ceiling, when there is one, is the only thing that ends the wait early.
        if has_timeout:
            elapsed = time() - start
            if elapsed >= timeout:
                raise Exception(f'{what} was not ready within {timeout}s, last error: {last_error}')

        sleep(Ready_Sleep)

# ################################################################################################################################
# ################################################################################################################################
