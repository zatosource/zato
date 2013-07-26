# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from logging import getLogger

# anyjson
from anyjson import dumps, loads

# gevent
from gevent import spawn_later

# retools
from retools.lock import Lock

# Zato
from zato.common import KVDB
from zato.common.util import TRACE1

class DeliveryStore(object):
    """ Stores messages in a persistent storage until they are confirmed to have been delivered.
    """
    def __init__(self, kvdb=None, delivery_lock_timeout=None):
        self.kvdb = kvdb
        self.delivery_lock_timeout = delivery_lock_timeout
        self.logger = getLogger(self.__class__.__name__)
        
# ##############################################################################

    def get_payload_key(self, target_type, target, tx_id):
        return ''.join((KVDB.DELIVERY_PREFIX, target_type, KVDB.SEPARATOR, target, KVDB.SEPARATOR, tx_id))
        
    def store_check(self, target_type, target, tx_id, payload, expire_after, check_after, retry_repeats, retry_seconds):
        if not(check_after and retry_repeats and retry_seconds):
            msg = 'check_after:[{}], retry_repeats:[{}] and retry_seconds:[{}] are all required'.format(
                check_after, retry_repeats, retry_seconds)
            self.logger.error(msg)
            raise Exception(msg)

        now = datetime.utcnow().isoformat()

        payload_key = self.get_payload_key(target_type, target, tx_id)
        payload_value = {
            'tx_id':tx_id,
            'payload':payload,
            'check_after': check_after,
            'retry_repeats':retry_repeats,
            'retry_seconds':retry_seconds,
            'attempts_made':0,
            'failed_attempt_list':[],
            'last_attempt_time_start_utc':None,
            'last_attempt_time_end_utc':None,
            'last_attempt_total_time':None,
            'planned_next_retry_time_utc':None,
            'actual_next_retry_time_utc':None,
            'creation_time_utc': now,
            'last_updated_utc': now,
            'confirmed': False,
            'send_side_count': 1,
            'confirm_side_count': 0,
            'in_doubt':False,
            'in_doubt_created_at_utc':None,
            'in_doubt_created_send_side_count':None,
            'in_doubt_created_confirm_side_count':None
        }
        
        by_target_type_key = '{}:{}'.format(KVDB.DELIVERY_BY_TARGET_TYPE_PREFIX, target_type)
        
        with self.kvdb.conn.pipeline() as p:
            p.hmset(payload_key, payload_value)
            p.sadd(by_target_type_key, payload_key)
    
            if expire_after:
                p.expire(payload_key, expire_after)
                
            p.execute()
        
        self.logger.info(
            'Created delivery key:[%s], expire_after:[%s], check_after:[%s], retry_repeats:[%s], retry_seconds:[%s]',
            payload_key, expire_after, check_after, retry_repeats, retry_seconds)
        
        spawn_later(check_after, self.check_target, payload_key, target_type, by_target_type_key, tx_id)

# ##############################################################################

    def check_target(self, payload_key, target_type, by_target_type_key, tx_id):
        self.logger.info('Checking target [%s]' , payload_key)
        
        now = datetime.utcnow().isoformat()
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, tx_id)
        
        with Lock(lock_name, self.delivery_lock_timeout, 0.2, self.kvdb.conn):
            payload = self.kvdb.conn.hgetall(payload_key)
            
            send_side_count = int(payload['send_side_count'])
            confirm_side_count = int(payload['confirm_side_count'])
            
            if send_side_count > confirm_side_count:
                
                # We're in a retry function and apparently the target has not replied yet.
                # We cannot retry just like that because we don't know what happened to target,
                # maybe it crashed or maybe it still hangs and will complete its jobs in a moment.
                # In any case, we can't invoke it again. We are in doubt as to what has happened.
                payload['in_doubt'] = True
                payload['in_doubt_created_at_utc'] = now
                payload['in_doubt_created_send_side_count'] = send_side_count
                payload['in_doubt_created_confirm_side_count'] = confirm_side_count
                
                with self.kvdb.conn.pipeline() as p:
                    
                    # There's a separate in-doubt key for each type of target so each outgoing
                    # connection or wrapper has its own key. The key stores a hashmap whose
                    # keys are concrete deliveries that are in doubt and values are payload
                    # that was to be delivered. So we add an in-doubt context and remove any 
                    # other information regarding this tx_id from other places.
                    in_doubt_key = '{}:{}'.format(KVDB.DELIVERY_IN_DOUBT_PREFIX, target_type)

                    data = {
                        'payload': dumps(payload),
                        'overtime_info': None # This is populated by target if it doesn't make it in the expected time
                                              # but still manages to confirm /something/ at all (but we still treat it as in-doubt).
                    }
                    
                    p.hset(in_doubt_key, payload_key, data)
                    p.delete(payload_key)
                    p.srem(by_target_type_key, payload_key)
                    
                    p.execute()
                    
                msg = 'tx_id:[{}] is in-doubt, details stored in [{}] under key [{}] (send/confirm {}/{})'.format(
                    tx_id, in_doubt_key, payload_key, send_side_count, confirm_side_count)
                #self.logger.warn(msg)
                
            else:
                # The target has confirmed the invocation in an expected time so we
                # now need to check if it was successful. If it was, this is where it ends.
                # If it wasn't, we'll try it again as it was originally configured
                # unless it was the last retry.
                pass

# ##############################################################################
        
    def confirm(self, target_type, target, payload, start, end):
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
            payload['confirmed'] = True
            payload['confirm_side_count'] = int(payload['attempts_made']) + 1
            
            self.logger.info('Confirmed delivery [{}] in {} after {} attempt(s)'.format(
                payload_key, total_time, attempts_made))
            
            if self.logger.isEnabledFor(TRACE1):
                self.logger.log(TRACE1, payload)

# ##############################################################################
