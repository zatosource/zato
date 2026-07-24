# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
from logging import getLogger

# Zato
from zato.common.rule_engine.jobs.common import build_backend, configure_job
from zato.common.rule_engine.notify.loop import Default_Interval_Seconds, run_forever, run_once

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ The resident notification dispatcher - advisory suite runs and message delivery over the event feed.
    """
    # Set up the argument parser ..
    parser = argparse.ArgumentParser(description='Zato rule engine notifications - advisory runs and chat delivery')

    _ = parser.add_argument(
        '--env-file', default='',
        help='Path to a file with environment variables to use')

    _ = parser.add_argument(
        '--interval', type=int, default=Default_Interval_Seconds,
        help=f'How many seconds to sleep between passes (default: {Default_Interval_Seconds})')

    _ = parser.add_argument(
        '--once', action='store_true',
        help='Run a single pass and exit instead of staying resident')

    args = parser.parse_args()

    # .. prepare logging and the environment ..
    configure_job(args.env_file)

    # .. open the shared rule engine database ..
    backend = build_backend()

    # .. and run one pass or stay resident.
    if args.once:
        result = run_once(backend)
        logger.info('Notify pass complete -> %d advisory runs, %d messages sent, %d failures',
            result.advisory_runs, result.messages_sent, result.delivery_failures)
    else:
        run_forever(backend, args.interval)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
