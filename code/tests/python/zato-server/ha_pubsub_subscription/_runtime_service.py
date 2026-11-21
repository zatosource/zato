# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time

# Zato
from zato.common.db_env.database import Type_PostgreSQL
from zato.common.db_env.engine import get_database_engine
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# SQLAlchemy
from sqlalchemy import text

# ################################################################################################################################
# ################################################################################################################################

class Runtime(Service):
    """ Holds locks, reports subscription list status and kills the worker for the live suite.
    """
    name = 'ha.pubsub.subscription.runtime'

# ################################################################################################################################

    def handle(self) -> 'None':
        payload = self.request.payload
        action = payload['action']

        if action == 'hold_locks':
            self._hold_locks(payload)
            self.response.payload = {'is_held': True}
            return

        if action == 'governed_pairs':
            pairs = self.server.pubsub_backend.get_governed_pairs()
            self.response.payload = {'pairs': pairs}
            return

        if action == 'statuses':
            statuses = list(self.server.pubsub_subscription_list.statuses())
            self.response.payload = {'statuses': statuses}
            return

        if action == 'kill_worker':
            os.kill(os.getpid(), signal.SIGKILL)
            return

        raise Exception(f'Unknown action `{action}`')

# ################################################################################################################################

    def _hold_locks(self, payload:'dict') -> 'None':
        """ Holds the locks that publications wait on for the given time.
        """
        hold_seconds = payload['hold_seconds']
        engine = get_database_engine()

        if engine.dialect.name == Type_PostgreSQL:
            statement = text(
                'select 1 from pubsub_topic_sub where topic_name = :topic_name limit :row_count for update')
            params = {
                'topic_name': payload['topic_name'].lower(),
                'row_count': payload['row_count'],
            }
        else:
            statement = text('begin immediate')
            params = {}

        with engine.connect() as connection:
            _ = connection.execute(statement, params)
            time.sleep(hold_seconds)
            connection.rollback()

# ################################################################################################################################
# ################################################################################################################################
