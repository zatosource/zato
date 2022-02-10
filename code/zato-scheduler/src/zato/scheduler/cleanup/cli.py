# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# sh
from sh import ErrorReturnCode

# Zato
from zato.common.typing_ import cast_
from zato.common.util.cli import CommandLineInvoker

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def start_cleanup():

    # Build the base invoker object
    invoker = CommandLineInvoker()

    # Our cleanup command to execute
    cli_params = [
        'pubsub',
        'cleanup',
        '--path',
        '/home/dsuch/env/pjm.global.4/scheduler',
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

        logger.warn('Cleanup exception -> %s', e.args[0])
        logger.warn('Cleanup exception stdout -> `%s`', stdout)
        logger.warn('Cleanup exception stderr -> `%s`', stderr)

    else:
        logger.info('Cleanup out.exit_code -> %s', out.exit_code)
        logger.info('Cleanup out.stderr -> %s', out.stderr)
        logger.info('Cleanup out.process.pid -> %s', out.process.pid if out.process else '(No PID)')
        logger.info('Cleanup out.cmd -> %s', out.cmd)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    start_cleanup()

# ################################################################################################################################
# ################################################################################################################################
