# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from pubsub_exactly_once.traffic_report import TrafficReport
from zato.common.pubsub.sql.schema import message_table
from zato.common.test.pubsub_database import get_db_mode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from threading import Event
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import callable_, strintdict, strlist

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_perf.progress')

# ################################################################################################################################
# ################################################################################################################################

sourcelist = list['_Source']

# ################################################################################################################################
# ################################################################################################################################

# How often the progress of a test is logged, in seconds
_interval_seconds = 10.0

# ################################################################################################################################
# ################################################################################################################################

def count_messages(engine:'Engine', topic_name:'str', prefix:'str') -> 'int':
    """ Returns how many messages of a topic have a correlation ID that starts with the prefix.
    """
    correl_id_pattern = prefix + '%'

    query = select(func.count())
    query = query.select_from(message_table)
    query = query.where(message_table.c.topic_name == topic_name)
    query = query.where(message_table.c.correl_id.like(correl_id_pattern))

    with engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################
# ################################################################################################################################

class _Source(NamedTuple):
    """ One value that the progress of a test reports, either a count that grows or a level that rises and falls.
    """
    name: 'str'
    read: 'callable_'
    is_level: 'bool'

# ################################################################################################################################
# ################################################################################################################################

class Progress:
    """ Logs the counts of a running test and their rates at regular intervals, and keeps the peak of each level.
    """

    def __init__(self, test_name:'str') -> 'None':
        self.test_name = test_name
        self.sources:'sourcelist' = []
        self.peaks:'strintdict' = {}

# ################################################################################################################################

    def add_count(self, name:'str', read:'callable_') -> 'None':
        source = _Source(name, read, False)
        self.sources.append(source)

# ################################################################################################################################

    def add_level(self, name:'str', read:'callable_') -> 'None':
        source = _Source(name, read, True)
        self.sources.append(source)
        self.peaks[name] = 0

# ################################################################################################################################

    def _read(self) -> 'strintdict':
        out:'strintdict' = {}

        for source in self.sources:
            out[source.name] = source.read()

        return out

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Logs the progress at each interval until the test stops it.
        """
        db_mode = get_db_mode()

        start = time.monotonic()
        previous = self._read()
        previous_time = start

        while not stop.wait(_interval_seconds):

            now = time.monotonic()
            current = self._read()
            seconds = now - previous_time

            parts:'strlist' = []

            for source in self.sources:
                value = current[source.name]

                # A level is reported as it is, with its peak kept ..
                if source.is_level:
                    self.peaks[source.name] = max(self.peaks[source.name], value)
                    parts.append(f'{source.name}={value}')

                # .. and a count with its rate since the previous interval.
                else:
                    growth = value - previous[source.name]
                    rate = growth / seconds
                    parts.append(f'{source.name}={value} ({rate:.0f}/s)')

            elapsed = now - start
            description = ', '.join(parts)

            logger.info('Perf progress %s on %s at %.0fs: %s', self.test_name, db_mode, elapsed, description)

            previous = current
            previous_time = now

# ################################################################################################################################
# ################################################################################################################################

class PerfReport(TrafficReport):
    """ The results of one performance test on the pub/sub database of the run.
    """

    def log(self) -> 'None':
        db_mode = get_db_mode()

        for line in self.lines:
            logger.info('Perf result %s on %s: %s', self.test_name, db_mode, line)

# ################################################################################################################################
# ################################################################################################################################
