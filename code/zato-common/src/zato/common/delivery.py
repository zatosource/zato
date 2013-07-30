# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
from logging import getLogger

# anyjson
from anyjson import dumps, loads

# gevent
from gevent import sleep, spawn_later

# Paste
from paste.util.converters import asbool

# retools
from retools.lock import Lock

# Zato
from zato.common import CHANNEL, DATA_FORMAT, KVDB
from zato.common.broker_message import SERVICE
from zato.common.model import DeliveryItem
from zato.common.util import new_cid, TRACE1

class DeliveryStore(object):
    """ Stores messages in a persistent storage until they are confirmed to have been delivered.
    """
    def __init__(self, kvdb=None, broker_client=None, delivery_lock_timeout=None):
        self.kvdb = kvdb
        self.broker_client = broker_client
        self.delivery_lock_timeout = delivery_lock_timeout
        self.logger = getLogger(self.__class__.__name__)
        
# ##############################################################################

    def get_payload_key(self, target_type, target, tx_id):
        return ''.join((KVDB.DELIVERY_PREFIX, target_type, KVDB.SEPARATOR, target, KVDB.SEPARATOR, tx_id))
    
    def get_archive_key(self, target_type, target, target_ok, tx_id):
        return ''.join((KVDB.DELIVERY_ARCHIVE_SUCCESS_PREFIX if target_ok else KVDB.DELIVERY_ARCHIVE_FAILED_PREFIX, 
                        target_type, KVDB.SEPARATOR, target, KVDB.SEPARATOR, tx_id))
        
    def store_check(self, item):
        if not(item.check_after and item.retry_repeats and item.retry_seconds):
            msg = 'check_after:[{}], retry_repeats:[{}] and retry_seconds:[{}] are all required'.format(
                item.check_after, item.retry_repeats, item.retry_seconds)
            self.logger.error(msg)
            raise Exception(msg)

        now = datetime.utcnow().isoformat()

        item.payload_key = self.get_payload_key(item.target_type, item.target, item.tx_id)
        payload_value = {
            'tx_id':item.tx_id,
            'payload':item.payload,
            'target_type': item.target_type,
            'target': item.target,
            'expire_arch_success_after': item.expire_arch_success_after,
            'expire_arch_failed_after': item.expire_arch_failed_after,
            'expires_arch_time_utc': None,
            'check_after': item.check_after,
            'retry_repeats':item.retry_repeats,
            'retry_seconds':item.retry_seconds,
            'attempts_made':0,
            'failed_attempt_list':dumps([]),
            'last_attempt_time_start_utc':None,
            'last_attempt_time_end_utc':None,
            'last_attempt_total_time':None,
            'creation_time_utc': now,
            'last_updated_utc': now,
            'confirmed': False,
            'target_ok': False,
            'target_self_info': None,
            'source_count': 1,
            'target_count': 0,
            'in_doubt':False,
            'in_doubt_created_at_utc':None,
            'in_doubt_created_source_count':None,
            'in_doubt_created_target_count':None,
            'on_delivery_success': dumps(item.on_delivery_success),
            'on_delivery_failed': dumps(item.on_delivery_failed),
        }
        
        item.by_target_type_key = '{}:{}'.format(KVDB.DELIVERY_BY_TARGET_TYPE_PREFIX, item.target_type)
        
        with self.kvdb.conn.pipeline() as p:
            p.hmset(item.payload_key, payload_value)
            p.sadd(item.by_target_type_key, item.payload_key)
    
            if item.expire_after:
                p.expire(item.payload_key, item.expire_after)
                
            p.execute()
        
        self.logger.info(
            'Created delivery key:[%s], expire_after:[%s], check_after:[%s], retry_repeats:[%s], retry_seconds:[%s]',
            item.payload_key, item.expire_after, item.check_after, item.retry_repeats, item.retry_seconds)

        self.spawn_check_target(item)

# ##############################################################################

    def check_target(self, item):
        self.logger.debug('Checking target [%s]', item.payload_key)
        
        now = datetime.utcnow().isoformat()
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, item.tx_id)
        
        with Lock(lock_name, self.delivery_lock_timeout, 0.2, self.kvdb.conn):
            payload = self.kvdb.conn.hgetall(item.payload_key)
            
            source_count = int(payload['source_count'])
            target_count = int(payload['target_count'])
            
            if source_count > target_count:
                
                # We're already in a retry function and apparently the target has not replied yet.
                # We cannot retry just like that because we don't know what happened to target,
                # maybe it crashed or maybe it still hangs and will complete its jobs in a moment.
                # In any case, we can't invoke it again. We are in doubt as to what has happened.
                payload['in_doubt'] = True
                payload['in_doubt_created_at_utc'] = now
                payload['in_doubt_created_source_count'] = source_count
                payload['in_doubt_created_target_count'] = target_count
                
                with self.kvdb.conn.pipeline() as p:
                    
                    # There's a separate in-doubt key for each type of target so each outgoing
                    # connection or wrapper has its own key. The key stores a hashmap whose
                    # keys are concrete deliveries that are in doubt and values are payload
                    # that was to be delivered. So we add an in-doubt context and remove any 
                    # other information regarding this tx_id from other places.
                    in_doubt_key = '{}:{}'.format(KVDB.DELIVERY_IN_DOUBT_PREFIX, item.target_type)

                    data = {
                        'payload': dumps(payload),
                        'overtime_info': None # This is populated by target if it doesn't make it in the expected time
                                              # but still manages to confirm /something/ at all (but we still treat it as in-doubt).
                    }
                    
                    p.hset(in_doubt_key, item.payload_key, data)
                    p.delete(item.payload_key)
                    p.srem(item.by_target_type_key, item.payload_key)
                    
                    p.execute()
                    
                msg = 'tx_id:[{}] is in-doubt, details stored in hash [{}] under key [{}] (send/confirm {}/{})'.format(
                    item.tx_id, in_doubt_key, item.payload_key, source_count, target_count)
                self.logger.warn(msg)
                
            else:
                # The target has confirmed the invocation in an expected time so we
                # now need to check if it was successful. If it was, this is where it ends,
                # we move the payload to the archive and that's it. If it wasn't, we'll try again
                # as it was originally configured unless it was the last retry.
                
                # This is common regardless of whether we had a success or not
                target_ok = asbool(payload['target_ok'])
                now = datetime.utcnow()
                payload['last_updated_utc'] = now.isoformat()
                
                # All good, we can stop now.
                if target_ok:
                    self.finish_delivery(target_ok, payload, now, item)
                    
                # Not so good, we know there was an error.
                else:
                    attempts_made = int(payload['attempts_made'])
                    retry_repeats = int(payload['retry_repeats'])
                    failed_attempt_list = loads(payload['failed_attempt_list'])
                    
                    fail_info = failed_attempt_list[attempts_made-1] # -1 because lists are indexed from 0
                    needs_reconnect = fail_info.get('needs_reconnect')
                    inner_exc = fail_info.get('inner_exc')
                    
                    keep_retrying = attempts_made < retry_repeats
                    
                    # Can we try again?
                    if keep_retrying:
                        self.spawn_invoke_func(item.invoke_func, item.invoke_args, item.invoke_kwargs)
                        self.spawn_check_target(item)
                        self.logger.info('Delivery attempt failed ({}/{}) [{}], needs_reconnect:[{}], inner_exc:[{}]'.format(
                            attempts_made, retry_repeats, item.payload_key, needs_reconnect, inner_exc))

                    # Nope, that was the last attempt.
                    else:
                        self.finish_delivery(target_ok, payload, now, item)
                    
    def spawn_invoke_func(self, invoke_func, invoke_args, invoke_kwargs):
        """ Spawns a greenlet that invokes a target after a short delay - we want to sleep a bit
        so whoever called us has a chance to release a delivery lock.
        """
        spawn_later(0.1, invoke_func, invoke_args, **invoke_kwargs)
        
    def spawn_check_target(self, item):
        """ Spawns a greenlet that checks whether the target replied and acts accordingly.
        """
        spawn_later(item.check_after, self.check_target, item)
        
    def finish_delivery(self, target_ok, payload, now, item):
        expire_arch_after_key = 'expire_arch_success_after' if target_ok else 'expire_arch_failed_after'
        expire_arch_after = int(payload[expire_arch_after_key])
        expires_arch_time = now + timedelta(seconds=expire_arch_after)
        
        arch_key = self.get_archive_key(item.target_type, item.target, target_ok, item.tx_id)
        payload['confirmed'] = True
        payload['expires_arch_time_utc'] = expires_arch_time.isoformat()
        
        with self.kvdb.conn.pipeline() as p:
            p.hmset(arch_key, payload)
            p.expire(arch_key, expire_arch_after)
            p.delete(item.payload_key)
            p.execute()
            
        if target_ok:
            msg_prefix = 'Confirmed delivery'
            log_func = self.logger.info
            callback_list = item.on_delivery_success
        else:
            msg_prefix = 'Delivery failed'
            log_func = self.logger.warn
            callback_list = item.on_delivery_failed
            
        msg = '{} after {}/{} attempts, [{}], payload moved to archive:[{}], expires in {}s ({} UTC)'.format(
            msg_prefix, payload['attempts_made'], payload['retry_repeats'], item.payload_key, 
            arch_key, expire_arch_after, expires_arch_time)
        log_func(msg)
        
        cid = new_cid()
            
        if callback_list:
            broker_msg = {}
            broker_msg['action'] = SERVICE.PUBLISH
            broker_msg['payload'] = payload
            broker_msg['channel'] = CHANNEL.DELIVERY
            broker_msg['data_format'] = DATA_FORMAT.JSON
            
            for service in callback_list:
                broker_msg['service'] = service
                broker_msg['cid'] = new_cid()
                self.broker_client.invoke_async(broker_msg)
                    
# ##############################################################################
        
    def on_target_completed(self, target_type, target, payload, start, end, target_ok, target_self_info, err_info=None):
        now = datetime.utcnow().isoformat()
        tx_id = payload['tx_id']
        payload_key = self.get_payload_key(target_type, target, tx_id)
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, tx_id)
        total_time = str(end - start)
        
        with Lock(lock_name, self.delivery_lock_timeout, 0.2, self.kvdb.conn):

            payload = self.kvdb.conn.hgetall(payload_key)
            attempts_made = int(payload['attempts_made']) + 1
                        
            payload['attempts_made'] = attempts_made
            payload['last_attempt_time_start_utc'] = start.isoformat()
            payload['last_attempt_time_end_utc'] = end.isoformat()
            payload['last_attempt_total_time'] = total_time
            payload['last_updated_utc'] = now
            payload['target_ok'] = target_ok
            payload['target_self_info'] = target_self_info
            payload['target_count'] = int(payload['attempts_made']) + 1
            
            if target_ok:
                self.logger.info('Delivery target OK [{}] in {} after {} attempt(s)'.format(payload_key, total_time, attempts_made))
            else:
                failed_attempt_list = loads(payload['failed_attempt_list'])
                failed_attempt_list.append(err_info)
                payload['failed_attempt_list'] = dumps(failed_attempt_list)

            self.kvdb.conn.hmset(payload_key, payload)            
                
            if self.logger.isEnabledFor(TRACE1):
                self.logger.log(TRACE1, payload)

# ##############################################################################
