# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import os
import sys
import time
from datetime import datetime
from logging import basicConfig, getLogger, INFO

# redis
from redis import Redis

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Stream_Prefix = 'zato:pubsub:stream:'
    Expiration_Key = 'zato:pubsub:expiration:'
    Default_Batch_Size = 100
    Default_Sleep_Seconds = 60

# ################################################################################################################################
# ################################################################################################################################

class MessageExpirationCleanup:
    """ Standalone process that cleans up expired messages from Redis pub/sub streams.
    """

    def __init__(
        self,
        redis_host:'str'='localhost',
        redis_port:'int'=6379,
        redis_db:'int'=0,
        redis_password:'str | None'=None,
        batch_size:'int'=ModuleCtx.Default_Batch_Size,
        sleep_seconds:'int'=ModuleCtx.Default_Sleep_Seconds,
    ) -> 'None':

        self.redis = Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True
        )
        self.batch_size = batch_size
        self.sleep_seconds = sleep_seconds
        self._running = False

# ################################################################################################################################

    def _get_all_streams(self) -> 'list[str]':
        """ Get all pub/sub stream keys.
        """
        pattern = f'{ModuleCtx.Stream_Prefix}*'
        keys = self.redis.keys(pattern)
        return keys

# ################################################################################################################################

    def _cleanup_stream(self, stream_key:'str') -> 'int':
        """ Clean up expired messages from a single stream.
        Returns the number of messages deleted.
        """
        deleted_count = 0
        now = datetime.utcnow()

        # Read messages from the stream
        messages = self.redis.xrange(stream_key, count=self.batch_size)

        for msg_id, msg_data in messages:
            expiration_time_iso = msg_data.get('expiration_time_iso')

            if expiration_time_iso:
                try:
                    expiration_time = datetime.fromisoformat(expiration_time_iso)
                    if now > expiration_time:
                        self.redis.xdel(stream_key, msg_id)
                        deleted_count += 1
                except ValueError:
                    pass

        return deleted_count

# ################################################################################################################################

    def run_once(self) -> 'dict':
        """ Run a single cleanup pass over all streams.
        Returns statistics about the cleanup.
        """
        stats = {
            'streams_processed': 0,
            'messages_deleted': 0,
            'errors': []
        }

        streams = self._get_all_streams()
        stats['streams_processed'] = len(streams)

        for stream_key in streams:
            try:
                deleted = self._cleanup_stream(stream_key)
                stats['messages_deleted'] += deleted
            except Exception as e:
                stats['errors'].append(f'{stream_key}: {e}')

        return stats

# ################################################################################################################################

    def run(self) -> 'None':
        """ Run the cleanup process continuously.
        """
        self._running = True
        logger.info(f'Starting message expiration cleanup (batch_size={self.batch_size}, sleep={self.sleep_seconds}s)')

        while self._running:
            try:
                stats = self.run_once()

                if stats['messages_deleted'] > 0:
                    logger.info(f"Cleanup pass: deleted {stats['messages_deleted']} messages from {stats['streams_processed']} streams")

                if stats['errors']:
                    for error in stats['errors']:
                        logger.warning(f'Cleanup error: {error}')

            except Exception as e:
                logger.error(f'Error in cleanup loop: {e}')

            time.sleep(self.sleep_seconds)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stop the cleanup process.
        """
        self._running = False
        logger.info('Stopping message expiration cleanup')

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'int':
    """ Main entry point for the cleanup process.
    """
    parser = argparse.ArgumentParser(description='Zato PubSub Message Expiration Cleanup')
    _ = parser.add_argument('--redis-host', default=os.environ.get('Zato_Redis_Host', 'localhost'), help='Redis host')
    _ = parser.add_argument('--redis-port', type=int, default=int(os.environ.get('Zato_Redis_Port', '6379')), help='Redis port')
    _ = parser.add_argument('--redis-db', type=int, default=int(os.environ.get('Zato_Redis_DB', '0')), help='Redis database')
    _ = parser.add_argument('--redis-password', default=os.environ.get('Zato_Redis_Password'), help='Redis password')
    _ = parser.add_argument('--batch-size', type=int, default=ModuleCtx.Default_Batch_Size, help='Messages to process per stream per pass')
    _ = parser.add_argument('--sleep', type=int, default=ModuleCtx.Default_Sleep_Seconds, help='Seconds to sleep between passes')
    _ = parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    basicConfig(
        level=INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    cleanup = MessageExpirationCleanup(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        redis_db=args.redis_db,
        redis_password=args.redis_password,
        batch_size=args.batch_size,
        sleep_seconds=args.sleep,
    )

    try:
        if args.once:
            stats = cleanup.run_once()
            logger.info(f"Cleanup complete: {stats}")
            return 0
        else:
            cleanup.run()
            return 0
    except KeyboardInterrupt:
        cleanup.stop()
        return 0
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())
