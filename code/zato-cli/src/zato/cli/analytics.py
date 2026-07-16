# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

class Rollup(ZatoCommand):
    """ Aggregates new audit log events into the analytics store as hourly rows.
    """

    opts = []

    def execute(self, args:'Namespace') -> 'int':

        # Zato
        from zato.common.analytics.rollup import run_rollup

        result = run_rollup()

        suffix = 'event' if result.event_count == 1 else 'events'
        self.logger.info('Aggregated %d %s, watermark is now %d', result.event_count, suffix, result.last_event_id)

        return 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace

    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False

    command = Rollup(args)
    command.run(args)

# ################################################################################################################################
# ################################################################################################################################
