# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def start_cleanup(path:'str') -> 'None':

    # Zato
    from zato.common.util.platform_ import is_windows

    if is_windows:
        return

    # sh
    from sh import ErrorReturnCode # type: ignore

    # Zato
    from zato.common.typing_ import cast_
    from zato.common.util.cli import CommandLineInvoker

    # Build the base invoker object
    invoker = CommandLineInvoker()

    # Our cleanup command to execute
    cli_params = [
        'pubsub',
        'cleanup',
        '--path',
        path,
        '--verbose',
    ]

    try:

        # We are ready to invoke it now
        out = invoker.invoke_cli(cli_params)

    except ErrorReturnCode as e:

        stdout = cast_('bytes', e.stdout)
        stdout = stdout.decode('utf8', errors='replace')

        stderr = cast_('bytes', e.stderr)
        stderr = stderr.decode('utf8', errors='replace')

        if stdout:
            logger.info('Cleanup return stdout -> `\n%s`', stdout)

        if stderr:
            logger.warn('Cleanup return stderr -> `\n%s`', stderr)

    else:
        logger.info('Cleanup out.exit_code -> %s', out.exit_code)
        logger.info('Cleanup out.stderr -> %s', out.stderr)
        logger.info('Cleanup out.process.pid -> %s', out.process.pid if out.process else '(No PID)')
        logger.info('Cleanup out.cmd -> %s', cast_('str', out.cmd))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import os

    # Zato
    from zato.common.util.platform_ import is_windows

    # We do not run on Windows
    if not is_windows:

        # Look up the path through an environment variable ..
        path = os.environ['ZATO_SCHEDULER_BASE_DIR']

        # .. and run the cleanup job.
        start_cleanup(path)

# ################################################################################################################################
# ################################################################################################################################
