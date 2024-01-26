# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

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

class Cleanup(ZatoCommand):
    """ Cleans up the pub/sub database.
    """
    opts = [
        {'name':'--subscriptions',
            'help':'Should unused subscriptions be deleted',
            'required':False, 'default':True},

        {'name':'--topics-without-subscribers',
            'help':'Should messages from topics without subscribers be deleted',
            'required':False, 'default':True},

        {'name':'--topics-with-max-retention-reached',
            'help':'Whether to delete messages whose max. retention time has been reached',
            'required':False, 'default':True},

        {'name':'--queues-with-expired-messages',
            'help':'Whether to delete messages whose expiration time has been reached',
            'required':False, 'default':True},

        {'name':'--path', 'help':'Local path to a Zato scheduler', 'required':True},
    ]

# ################################################################################################################################

    def execute(self, args:'Namespace'):

        # Zato
        from zato.common.util.api import as_bool
        from zato.scheduler.cleanup.core import run_cleanup

        clean_up_subscriptions = getattr(args, 'subscriptions', True)
        clean_up_topics_without_subscribers = getattr(args, 'topics_without_subscribers', True)
        clean_up_topics_with_max_retention_reached = getattr(args, 'topics_with_max_retention_reached', True)
        clean_up_queues_with_expired_messages = getattr(args, 'queues_with_expired_messages', True)

        clean_up_subscriptions = as_bool(clean_up_subscriptions)
        clean_up_topics_without_subscribers = as_bool(clean_up_topics_without_subscribers)
        clean_up_topics_with_max_retention_reached = as_bool(clean_up_topics_with_max_retention_reached)
        clean_up_queues_with_expired_messages = as_bool(clean_up_queues_with_expired_messages)

        _ = run_cleanup(
            clean_up_subscriptions,
            clean_up_topics_without_subscribers,
            clean_up_topics_with_max_retention_reached,
            clean_up_queues_with_expired_messages,
            scheduler_path = args.path
        )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    from argparse import Namespace
    from os import environ

    args = Namespace()
    args.verbose      = True
    args.store_log    = False
    args.store_config = False
    args.path = environ['ZATO_SCHEDULER_BASE_DIR']

    # while True:
    command = Cleanup(args)
    command.run(args, needs_sys_exit=False)

# ################################################################################################################################
# ################################################################################################################################
