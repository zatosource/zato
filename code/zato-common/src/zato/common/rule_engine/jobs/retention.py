# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
from datetime import timedelta
from logging import getLogger

# Zato
from zato.common.rule_engine.jobs.common import build_backend, configure_job
from zato.common.rule_engine.sql.time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many days of decision history survive a sweep when the command line does not say otherwise.
Default_Retention_Days = 90

# ################################################################################################################################
# ################################################################################################################################

def run_retention(backend:'RuleSQLBackend', days:'int') -> 'int':
    """ Deletes decisions older than the retention window, returning how many were removed.
    """
    # Everything before the cutoff goes ..
    now = utc_now()
    cutoff = now - timedelta(days=days)

    # .. in bounded chunks over the indexed timestamp.
    out = backend.decisions.delete_before(cutoff)
    return out

# ################################################################################################################################

def main() -> 'None':
    """ The decision retention sweep - one bounded pass and exit.
    """
    # Set up the argument parser ..
    parser = argparse.ArgumentParser(description='Zato rule engine retention - deletes decisions past their window')

    _ = parser.add_argument(
        '--env-file', default='',
        help='Path to a file with environment variables to use')

    _ = parser.add_argument(
        '--days', type=int, default=Default_Retention_Days,
        help=f'How many days of decisions to keep (default: {Default_Retention_Days})')

    args = parser.parse_args()

    # .. prepare logging and the environment ..
    configure_job(args.env_file)

    # .. open the shared rule engine database ..
    backend = build_backend()

    # .. and run the one bounded pass.
    deleted_count = run_retention(backend, args.days)
    suffix = 'decision' if deleted_count == 1 else 'decisions'
    logger.info('Retention sweep complete -> %d %s deleted (keeping %d days)', deleted_count, suffix, args.days)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
