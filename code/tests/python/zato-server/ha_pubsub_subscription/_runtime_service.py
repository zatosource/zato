# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Runtime(Service):
    """ Reports the governed rows and the subscription list of the worker, and kills the worker, for the live suite.
    """
    name = 'ha.pubsub.subscription.runtime'

# ################################################################################################################################

    def handle(self) -> 'None':
        action = self.request.payload['action']

        if action == 'governed_pairs':
            pairs = self.server.pubsub_backend.get_governed_pairs()
            self.response.payload = {'pairs': pairs}

        elif action == 'statuses':
            statuses = self.server.pubsub_subscription_list.statuses()
            self.response.payload = {'statuses': statuses}

        elif action == 'kill_worker':
            os.kill(os.getpid(), signal.SIGKILL)

        else:
            raise Exception(f'Unknown action `{action}`')

# ################################################################################################################################
# ################################################################################################################################
