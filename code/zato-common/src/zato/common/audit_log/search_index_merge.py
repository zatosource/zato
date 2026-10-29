# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from threading import Event, Thread

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.db_env.engine import call_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import strtuple
    Engine = Engine
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How often the pending lists of the trigram indexes are merged into the indexes. Each merge rewrites the entry
# of every key the merged rows contain once, so a longer interval covers more rows with each rewrite.
Merge_Interval_Seconds = 10.0

# Merges the pending list of one GIN index into the index.
_merge_query = text('select gin_clean_pending_list(cast(:index_name as regclass))')

# ################################################################################################################################
# ################################################################################################################################

class SearchIndexMerger:
    """ Merges the pending lists of the trigram GIN indexes of PostgreSQL into the indexes every ten seconds, in a thread
    of its own. An insert that finds a pending list over its limit merges the whole list within its own statement,
    which delays the transaction of that insert and writes the WAL of the merge at once. Merged every ten seconds,
    each pending list stays well below its limit, so that no insert merges it.
    """

    def __init__(self, engine:'Engine', index_names:'strtuple', interval_seconds:'float'=Merge_Interval_Seconds) -> 'None':
        self.engine = engine
        self.index_names = index_names
        self.interval_seconds = interval_seconds
        self._stop_event = Event()
        self._thread = Thread(target=self._run, name='audit-search-index-merge', daemon=True)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts merging the pending lists.
        """
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops merging the pending lists after the merge in progress, if any.
        """
        self._stop_event.set()

# ################################################################################################################################

    def merge(self) -> 'None':
        """ Merges the pending list of each index into the index, each in a transaction of its own.
        """
        for index_name in self.index_names:
            with self.engine.begin() as connection:
                _ = connection.execute(_merge_query, {'index_name': index_name})

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Merges the pending lists at each interval, until the merger is stopped.
        """
        while not self._stop_event.wait(self.interval_seconds):
            try:
                call_database(self.engine, self.merge)
            except Exception:
                logger.exception('Search index merge failed')

# ################################################################################################################################
# ################################################################################################################################
