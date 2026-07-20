# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import logging
import signal
import sys
import time

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.pubsub.sql.config import get_batch_size, get_delivered_max_days, get_delivered_max_messages, \
    get_pubsub_engine
from zato.common.pubsub.sql.schema import delivery_table, message_table
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import intlist, intnone, strintdict, strlist

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.pubsub.cleanup')

# ################################################################################################################################
# ################################################################################################################################

# How long the cleanup process sleeps between sweeps.
_default_interval_seconds = 60

# How long each slice of the between-sweeps sleep is, in seconds -
# short slices let a stop request take effect without waiting out the whole interval.
_sleep_slice_seconds = 1

# How many milliseconds one second and one day have - timestamp columns hold epoch milliseconds.
_ms_per_second = 1000
_ms_per_day = 24 * 60 * 60 * _ms_per_second

# ################################################################################################################################
# ################################################################################################################################

class PubSubCleanup:
    """ Removes what the pub/sub database does not need anymore - expired messages
    together with their delivery rows, and fully delivered message traces that are
    past their retention age or above their per-topic cap. Every delete runs
    in bounded batches, each its own transaction.
    """

    def __init__(self, interval_seconds:'int'=_default_interval_seconds) -> 'None':
        self.interval_seconds = interval_seconds
        self._should_stop = False

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine behind the current Zato_PubSub_DB_* configuration.
        """
        out = get_pubsub_engine()
        return out

# ################################################################################################################################

    @staticmethod
    def _utc_now_ms() -> 'int':
        """ Returns the current UTC time in milliseconds since the Unix epoch.
        """
        now = utcnow()
        milliseconds = datetime_to_ms(now)

        out = int(milliseconds)
        return out

# ################################################################################################################################

    def _delete_message_batch(self, connection:'Connection', message_ids:'intlist') -> 'None':
        """ Deletes the given messages along with any delivery rows that still reference them.
        """
        delete_deliveries = delivery_table.delete()
        delete_deliveries = delete_deliveries.where(delivery_table.c.message_id.in_(message_ids))
        _ = connection.execute(delete_deliveries)

        delete_messages = message_table.delete()
        delete_messages = delete_messages.where(message_table.c.id.in_(message_ids))
        _ = connection.execute(delete_messages)

# ################################################################################################################################

    def _sweep_expired(self) -> 'int':
        """ Deletes messages whose expiration time has passed, together with their delivery rows.
        Fully delivered traces are exempt. Returns how many messages were deleted.
        """
        batch_size = get_batch_size()
        now_ms = self._utc_now_ms()

        out = 0

        while True:

            # Each batch is its own transaction so other work interleaves between the batches.
            with self.engine.begin() as connection:

                # Only messages with a retained payload can expire ..
                query = select(message_table.c.id)
                query = query.where(and_(
                    message_table.c.expiration_ms < now_ms,
                    message_table.c.payload.isnot(None),
                ))
                query = query.limit(batch_size)

                message_ids:'intlist' = []

                for row in connection.execute(query):
                    message_ids.append(row.id)

                # .. nothing expired is left so the sweep is done ..
                if not message_ids:
                    break

                # .. remove the batch with everything still pending for it.
                self._delete_message_batch(connection, message_ids)

                out += len(message_ids)

        if out:
            logger.info('Expiry sweep -> deleted:%d', out)

        return out

# ################################################################################################################################

    def _sweep_aged_traces(self) -> 'int':
        """ Deletes fully delivered message traces older than the retention age.
        Returns how many traces were deleted.
        """
        batch_size = get_batch_size()
        max_days = get_delivered_max_days()

        # Everything published before this moment is past its retention age.
        cutoff_ms = self._utc_now_ms() - max_days * _ms_per_day

        out = 0

        while True:

            # Each batch is its own transaction so other work interleaves between the batches.
            with self.engine.begin() as connection:

                # A NULL payload is what makes a row a delivered-message trace ..
                query = select(message_table.c.id)
                query = query.where(and_(
                    message_table.c.payload.is_(None),
                    message_table.c.pub_time_ms < cutoff_ms,
                ))
                query = query.limit(batch_size)

                message_ids:'intlist' = []

                for row in connection.execute(query):
                    message_ids.append(row.id)

                # .. no trace is old enough anymore so the sweep is done ..
                if not message_ids:
                    break

                # .. remove the batch.
                self._delete_message_batch(connection, message_ids)

                out += len(message_ids)

        if out:
            logger.info('Aged-trace sweep -> deleted:%d, max_days:%d', out, max_days)

        return out

# ################################################################################################################################

    def _get_trace_topics(self) -> 'strlist':
        """ Returns the names of all the topics that have any delivered-message traces.
        """
        query = select(message_table.c.topic_name).distinct()
        query = query.where(message_table.c.payload.is_(None))

        out:'strlist' = []

        with self.engine.connect() as connection:
            for row in connection.execute(query):
                out.append(row.topic_name)

        return out

# ################################################################################################################################

    def _get_topic_cap_cutoff(self, topic_name:'str', max_messages:'int') -> 'intnone':
        """ Returns the highest trace row id of one topic that is above the retention cap,
        or None when the topic is within its cap. Everything at or below the returned id must go.
        """
        # The row max_messages positions into the newest-first ordering
        # is the newest one that no longer fits the cap.
        query = select(message_table.c.id)
        query = query.where(and_(
            message_table.c.topic_name == topic_name,
            message_table.c.payload.is_(None),
        ))
        query = query.order_by(message_table.c.id.desc())
        query = query.limit(1)
        query = query.offset(max_messages)

        with self.engine.connect() as connection:
            out = connection.execute(query).scalar()

        return out

# ################################################################################################################################

    def _sweep_over_cap_traces(self) -> 'int':
        """ Deletes the oldest delivered-message traces of each topic that holds
        more of them than the per-topic cap allows. Returns how many traces were deleted.
        """
        batch_size = get_batch_size()
        max_messages = get_delivered_max_messages()

        out = 0

        for topic_name in self._get_trace_topics():

            # Everything at or below the cutoff id is above the cap and must go ..
            cutoff_id = self._get_topic_cap_cutoff(topic_name, max_messages)

            # .. this topic is within its cap ..
            if cutoff_id is None:
                continue

            # .. delete the over-cap traces in bounded batches.
            while True:

                with self.engine.begin() as connection:

                    query = select(message_table.c.id)
                    query = query.where(and_(
                        message_table.c.topic_name == topic_name,
                        message_table.c.payload.is_(None),
                        message_table.c.id <= cutoff_id,
                    ))
                    query = query.limit(batch_size)

                    message_ids:'intlist' = []

                    for row in connection.execute(query):
                        message_ids.append(row.id)

                    if not message_ids:
                        break

                    self._delete_message_batch(connection, message_ids)

                    out += len(message_ids)

        if out:
            logger.info('Over-cap-trace sweep -> deleted:%d, max_messages:%d', out, max_messages)

        return out

# ################################################################################################################################

    def sweep_once(self) -> 'strintdict':
        """ Runs one full cleanup sweep - expired messages first, then the delivered-trace
        retention by age and by per-topic cap. Returns the per-sweep deletion counts.
        """
        expired = self._sweep_expired()
        aged = self._sweep_aged_traces()
        over_cap = self._sweep_over_cap_traces()

        out = {
            'expired': expired,
            'aged': aged,
            'over_cap': over_cap,
        }

        return out

# ################################################################################################################################

    def run(self) -> 'None':
        """ Runs the cleanup loop until stopped.
        """
        logger.info('Cleanup started -> interval:%ds', self.interval_seconds)

        while not self._should_stop:

            counts = self.sweep_once()
            logger.info('Sweep completed -> expired:%d, aged:%d, over_cap:%d',
                counts['expired'], counts['aged'], counts['over_cap'])

            # Sleep in short slices so a stop request does not wait out the whole interval.
            slept_seconds = 0

            while slept_seconds < self.interval_seconds and not self._should_stop:
                time.sleep(_sleep_slice_seconds)
                slept_seconds += _sleep_slice_seconds

        logger.info('Cleanup stopped')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Signals the cleanup loop to stop.
        """
        self._should_stop = True

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'int':
    """ Entry point for the cleanup process.
    """

    # Set up the argument parser ..
    parser = argparse.ArgumentParser(description='Zato pub/sub cleanup - expired messages and delivered-trace retention')

    _ = parser.add_argument(
        '--env-file', default='',
        help='Path to a file with environment variables to use')

    _ = parser.add_argument(
        '--interval', type=int, default=_default_interval_seconds,
        help=f'Seconds between cleanup sweeps (default: {_default_interval_seconds})')

    _ = parser.add_argument(
        '--log-level', default='INFO',
        help='Logging level (default: INFO)')

    _ = parser.add_argument(
        '--once', action='store_true',
        help='Run a single sweep and exit')

    # .. parse arguments ..
    args = parser.parse_args()

    # .. set up logging ..
    log_level_name = args.log_level.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

    # .. load the Zato_PubSub_DB_* variables from the environment file if one was given -
    # .. with no file and no variables already set, the default SQLite database is used ..
    if args.env_file:
        from zato.common.util.env import populate_environment_from_file
        _ = populate_environment_from_file(args.env_file)

    # .. create the cleanup instance ..
    cleanup = PubSubCleanup(interval_seconds=args.interval)

    # .. handle signals for graceful shutdown ..
    def _handle_signal(signal_number:'int', frame:'object') -> 'None':
        logger.info('Received signal %d, stopping', signal_number)
        cleanup.stop()

    _ = signal.signal(signal.SIGINT, _handle_signal)
    _ = signal.signal(signal.SIGTERM, _handle_signal)

    logger.info('Cleanup process starting -> interval:%ds', args.interval)

    # .. run.
    if args.once:
        counts = cleanup.sweep_once()
        logger.info('Single sweep completed -> expired:%d, aged:%d, over_cap:%d',
            counts['expired'], counts['aged'], counts['over_cap'])
        return 0

    cleanup.run()
    return 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################
