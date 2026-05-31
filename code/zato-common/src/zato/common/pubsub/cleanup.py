# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import logging
import os
import signal
import sys
import time

# redis
from redis import Redis

# Zato
from zato.common.pubsub.disk_store import DiskMessageStore
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.pubsub.cleanup')

# ################################################################################################################################
# ################################################################################################################################

_Default_Interval_Seconds = 60
_Default_Batch_Size       = 1000
_Default_Redis_Host       = 'localhost'
_Default_Redis_Port       = 6379
_Default_Redis_DB         = 0

_Pending_Prefix      = 'zato:pubsub:pending:'
_Pending_Expiry_Key  = 'zato:pubsub:pending_expiry'
_Sub_Pending_Prefix  = 'zato:pubsub:sub_pending:'

# Atomically cleans up a single expired message's Redis state:
# removes the data_ref from each subscriber's reverse index,
# deletes the pending set, and removes the expiry entry.
# Returns 1 if this call owned the cleanup (pending_key existed), 0 if already cleaned.
_lua_sweep_cleanup = """
local pending_key = KEYS[1]
local expiry_key = KEYS[2]

local data_ref = ARGV[1]
local sub_pending_prefix = ARGV[2]

-- Check whether the pending set still exists ..
local subscriber_keys = redis.call('SMEMBERS', pending_key)
local had_pending = #subscriber_keys > 0

-- .. remove this data_ref from each subscriber's reverse index ..
for _, subscriber_key in ipairs(subscriber_keys) do
    local sub_pending_key = sub_pending_prefix .. subscriber_key
    redis.call('SREM', sub_pending_key, data_ref)
end

-- .. delete the pending set ..
redis.call('DEL', pending_key)

-- .. remove from the expiry index ..
redis.call('ZREM', expiry_key, data_ref)

-- .. return whether this call owned the cleanup.
if had_pending then
    return 1
end

return 0
"""

# ################################################################################################################################
# ################################################################################################################################

class PubSubCleanup:
    """ Periodically scans the Redis expiry index for messages whose TTL has passed
    and deletes the corresponding disk files, pending sets, and expiry entries.
    """

    def __init__(
        self,
        redis_client:'Redis', # type: ignore[type-arg]
        disk_store:'DiskMessageStore',
        interval_seconds:'int'=_Default_Interval_Seconds,
        batch_size:'int'=_Default_Batch_Size,
    ) -> 'None':
        self.redis = redis_client
        self.disk_store = disk_store
        self.interval_seconds = interval_seconds
        self.batch_size = batch_size
        self._should_stop = False

        # Load the Lua script for atomic per-message cleanup ..
        self._lua_sweep_cleanup_sha:'str' = cast_('str', self.redis.script_load(_lua_sweep_cleanup))

# ################################################################################################################################

    def _get_pending_key(self, data_ref:'str') -> 'str':
        """ Returns the Redis key for the pending subscriber set of a given message.
        """
        out = f'{_Pending_Prefix}{data_ref}'
        return out

# ################################################################################################################################

    def sweep_once(self) -> 'int':
        """ Runs a single cleanup sweep. Returns the number of expired entries removed.
        """

        # Get current time as a Unix timestamp ..
        now = time.time()

        # .. find all expired entries, capped by batch size ..
        expired_refs:'strlist' = cast_('strlist', self.redis.zrangebyscore(
            _Pending_Expiry_Key, 0, now,
            start=0, num=self.batch_size))

        if not expired_refs:
            return 0

        deleted_count = 0

        _sweep_num_keys = 2

        for data_ref in expired_refs:

            # Build the pending key for this message ..
            pending_key = self._get_pending_key(data_ref)

            # .. atomically clean up all Redis state for this expired message ..
            owned_cleanup:'int' = cast_('int', self.redis.evalsha(
                self._lua_sweep_cleanup_sha,
                _sweep_num_keys,
                pending_key,
                _Pending_Expiry_Key,
                data_ref,
                _Sub_Pending_Prefix,
            ))

            # .. only delete the disk file if this call owned the cleanup -
            # .. a concurrent ack_message may have already cleaned it ..
            if owned_cleanup:
                self.disk_store.delete(data_ref)

            deleted_count += 1
            logger.info('Cleaned up expired message -> data_ref:%s, owned_cleanup:%s', data_ref, owned_cleanup)

        return deleted_count

# ################################################################################################################################

    def run(self) -> 'None':
        """ Runs the cleanup loop until stopped.
        """
        logger.info('Cleanup started -> interval:%ds, batch_size:%d', self.interval_seconds, self.batch_size)

        while not self._should_stop:
            time.sleep(self.interval_seconds)

            deleted_count = self.sweep_once()
            logger.info('Sweep completed -> deleted:%d', deleted_count)

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
    parser = argparse.ArgumentParser(description='Zato pub/sub expired message cleanup')

    _ = parser.add_argument('server_directory', help='Path to the Zato server directory')

    _ = parser.add_argument(
        '--interval', type=int, default=_Default_Interval_Seconds,
        help=f'Seconds between cleanup sweeps (default: {_Default_Interval_Seconds})')

    _ = parser.add_argument(
        '--batch-size', type=int, default=_Default_Batch_Size,
        help=f'Maximum expired entries per sweep (default: {_Default_Batch_Size})')

    _ = parser.add_argument(
        '--redis-host', default=_Default_Redis_Host,
        help=f'Redis host (default: {_Default_Redis_Host})')

    _ = parser.add_argument(
        '--redis-port', type=int, default=_Default_Redis_Port,
        help=f'Redis port (default: {_Default_Redis_Port})')

    _ = parser.add_argument(
        '--redis-db', type=int, default=_Default_Redis_DB,
        help=f'Redis database (default: {_Default_Redis_DB})')

    _ = parser.add_argument(
        '--redis-password', default=None,
        help='Redis password')

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

    # .. resolve the server directory ..
    server_directory = os.path.abspath(args.server_directory)

    if not os.path.isdir(server_directory):
        logger.error('Server directory does not exist -> %s', server_directory)
        return 1

    # .. connect to Redis ..
    redis_client:'Redis' = Redis( # type: ignore[type-arg]
        host=args.redis_host,
        port=args.redis_port,
        db=args.redis_db,
        password=args.redis_password,
        decode_responses=True,
    )

    # .. set up the disk store ..
    disk_store_base_dir = os.path.join(server_directory, 'work', 'pubsub-messages')
    disk_store = DiskMessageStore(disk_store_base_dir)

    # .. create the cleanup instance ..
    cleanup = PubSubCleanup(
        redis_client=redis_client,
        disk_store=disk_store,
        interval_seconds=args.interval,
        batch_size=args.batch_size,
    )

    # .. handle signals for graceful shutdown ..
    def _handle_signal(signal_number:'int', frame:'object') -> 'None':
        logger.info('Received signal %d, stopping', signal_number)
        cleanup.stop()

    _ = signal.signal(signal.SIGINT, _handle_signal)
    _ = signal.signal(signal.SIGTERM, _handle_signal)

    logger.info(
        'Cleanup process starting -> server_directory:%s, redis:%s:%d, interval:%ds, batch_size:%d',
        server_directory, args.redis_host, args.redis_port, args.interval, args.batch_size)

    # .. run.
    if args.once:
        deleted_count = cleanup.sweep_once()
        logger.info('Single sweep completed -> deleted:%d', deleted_count)
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
