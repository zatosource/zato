# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from threading import Event, Lock, Thread

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.audit_log.common import event_attr_table
from zato.common.audit_log.search_index import get_postgresql_index_names
from zato.common.db_env.common import Type_PostgreSQL
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

class _MergerCtx:
    """ The merger of the audit engine the process writes to, if that engine is a PostgreSQL one.
    """

    # Guards the replacement of the merger
    lock = Lock()

    # The engine the merger was chosen for, or None before the first write
    engine:'Engine | None' = None

    # The merger of that engine, or None on SQLite
    merger:'SearchIndexMerger | None' = None

# ################################################################################################################################

def get_search_index_merger(engine:'Engine') -> 'SearchIndexMerger | None':
    """ Returns the started merger of the trigram indexes of the event and attribute tables for a PostgreSQL engine,
    starting it with the first call. The merger of a previous engine is stopped once another engine takes its place,
    and no merger runs on SQLite.
    """

    # The merger of this engine has been chosen already ..
    if _MergerCtx.engine is engine:
        return _MergerCtx.merger

    with _MergerCtx.lock:

        # .. it was chosen while this caller waited for the lock ..
        if _MergerCtx.engine is engine:
            return _MergerCtx.merger

        # .. the merger of the previous engine stops ..
        if previous := _MergerCtx.merger:
            previous.stop()

        # .. and a PostgreSQL engine receives one of its own.
        if engine.dialect.name == Type_PostgreSQL:
            index_names = get_postgresql_index_names(event_attr_table.name)

            out = SearchIndexMerger(engine, index_names)
            out.start()
        else:
            out = None

        _MergerCtx.merger = out
        _MergerCtx.engine = engine

    return out

# ################################################################################################################################
# ################################################################################################################################
