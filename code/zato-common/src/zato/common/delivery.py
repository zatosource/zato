# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import csv
from contextlib import closing
from datetime import datetime, timedelta
from json import dumps, loads
from logging import getLogger

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep, spawn_later

# memory_profiler
from memory_profiler import profile

# Paste
from paste.util.converters import asbool

# retools
from retools.lock import Lock

# Zato
from zato.common import CHANNEL, DATA_FORMAT, INVOCATION_TARGET, KVDB
from zato.common.broker_message import SERVICE
from zato.common.odb.model import DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ
from zato.common.odb.query import out_jms_wmq
from zato.common.util import datetime_to_seconds, new_cid, TRACE1
from zato.redis_paginator import ZSetPaginator

NULL_BASIC_DATA = {
    'last_updated_utc':None,
    'total_count':0,
    'in_progress_count':0, 
    'in_doubt_count':0,
    'arch_success_count':0,
    'arch_failed_count':0
}

_target_query_by_id = {
    INVOCATION_TARGET.OUTCONN_WMQ: out_jms_wmq
}

_target_def_class = {
    INVOCATION_TARGET.OUTCONN_WMQ: DeliveryDefinitionOutconnWMQ
}

def _item_from_odb(def_base, target, task_id):
    return Bunch({
        'task_id': task_id,
        'def_name': def_base.name,
        'target': target,
        'target_type': def_base.target_type,
        'expire_after': def_base.expire_after,
        'check_after': def_base.check_after,
        'retry_repeats': def_base.retry_repeats,
        'retry_seconds': def_base.retry_seconds,
    })

# ##############################################################################

class DeliveryStore(object):
    """ Stores messages in a persistent storage until they are confirmed to have been delivered.
    """
    def __init__(self, kvdb=None, broker_client=None, odb=None, delivery_lock_timeout=None):
        self.kvdb = kvdb
        self.broker_client = broker_client
        self.odb = odb
        self.delivery_lock_timeout = delivery_lock_timeout
        self.logger = getLogger(self.__class__.__name__)
        
# ##############################################################################

    def _validate_register(self, item):
        if not(item.check_after and item.retry_repeats and item.retry_seconds):
            msg = 'check_after:[{}], retry_repeats:[{}] and retry_seconds:[{}] are all required'.format(
                item.check_after, item.retry_repeats, item.retry_seconds)
            self.logger.error(msg)
            raise ValueError(msg)
        
    def register(self, item):
        self._validate_register(item)

        self.logger.info(
          'Submitted delivery [%s] for target:[%s] (%s/%s), expire_after:[%s], check_after:[%s], retry_repeats:[%s], retry_seconds:[%s]',
            item.task_id, item.target, item.def_name, item.target_type, item.expire_after, item.check_after, item.retry_repeats, item.retry_seconds)

        self.spawn_check_target(item)

# ##############################################################################

    def get_target_basic_data(self, name):
        """ Returns counters for a given delivery by its name along with info when the delivery
        was last time used. Does not hold onto any locks so the results are precise
        yet may be off by the time caller receives them.
        """
        return self.kvdb.conn.hgetall('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name)) or NULL_BASIC_DATA
    
    def set_deleted(self, name, is_deleted):
        """ Sets a boolean flag indicating whether a definition has been deleted.
        Any new instances of check_target consult this flag to see whether they should
        keep running.
        """
        self.kvdb.conn.hset('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name), 'deleted', is_deleted)
        
    def set_updated(self, name, is_updated):
        """ Sets a boolean flag indicating whether a definition has been updated.
        Any new instances of check_target consult this flag to see whether they should
        perhaps change their schedule.
        """
        self.kvdb.conn.hset('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name), 'updated', is_updated)

# ##############################################################################

    def deliver(self, cluster_id, def_name, request, task_id):
        """ A public method to be invoked by services for delivering a request to a target
        through a definition.
        """
        with closing(self.odb.session()) as session:
            def_base = session.query(DeliveryDefinitionBase).\
                filter(DeliveryDefinitionBase.cluster_id==cluster_id).\
                filter(DeliveryDefinitionBase.name==def_name).\
                    first()
            
            if not def_base:
                msg = 'Guaranteed delivery definition [{}] does not exist'.format(def_name)
                self.logger.warn(msg)
                raise ValueError(msg)
            
            target_def_class = _target_def_class[def_base.target_type]
            definition = session.query(target_def_class).\
                filter(target_def_class.id==def_base.id).\
                one()
            
            self.register(_item_from_odb(def_base, definition.target.name, task_id))

'''
    def _on_in_doubt(self, item, delivery, now, now_dt, source_count, target_count):
        pass
        
    def _move_payload_to_odb(self, item, business_payload):
        """ Moves business payload to ODB and deletes it from Redis.
        """
        with closing(self.odb.session()) as session:
            self.kvdb.conn.delete(item.payload_key)

    def check_target(self, item):
        self.logger.debug('Checking name/target [%s]/[%s]', item.name, item.delivery_key)
        
        now_dt = datetime.utcnow()
        now = now_dt.isoformat()
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, item.tx_id)
        
        attempts_made = int(delivery['attempts_made'])
        retry_repeats = int(delivery['retry_repeats'])
        
        with Lock(lock_name, self.delivery_lock_timeout, 0.2, self.kvdb.conn):

            if source_count > target_count:
                
                # STATE - in-doubt
                self._on_in_doubt(item, delivery, now, now_dt, source_count, target_count)
                
            else:
                # The target has confirmed the invocation in an expected time so we
                # now need to check if it was successful. If it was, this is where it ends,
                # we move the delivery to the archive and that's it. If it wasn't, we'll try again
                # as it was originally configured unless it was the last retry.

                
                # All good, we can stop now.
                if target_ok:
                    self.finish_delivery(target_ok, delivery, now, item)
                    
                # Not so good, we know there was an error.
                else:
                    # Can we try again?
                    if attempts_made < retry_repeats:
                        self.retry()

                    # Nope, that was the last attempt.
                    else:
                        self.finish_delivery(target_ok, delivery, now, item)
                    
    def spawn_invoke_func(self, invoke_func, invoke_args, invoke_kwargs):
        """ Spawns a greenlet that invokes a target after a short delay - we want to sleep a bit
        so whoever called us has a chance to release a delivery lock.
        """
        spawn_later(0.1, invoke_func, invoke_args, **invoke_kwargs)
        
    def spawn_check_target(self, item):
        """ Spawns a greenlet that checks whether the target replied and acts accordingly.
        """
        spawn_later(item.check_after, self.check_target, item)
        
    def finish_delivery(self, target_ok, delivery, now, item):
        
        if target_ok:
            delivery['confirmed'] = True
            msg_prefix = 'Confirmed delivery'
            log_func = self.logger.info
            callback_list = item.on_delivery_success
        else:
            delivery['confirmed'] = False
            msg_prefix = 'Delivery failed'
            log_func = self.logger.warn
            callback_list = item.on_delivery_failed.split(KVDB.SEPARATOR)
            
        msg = '{} after {}/{} attempts, [{}], delivery moved to archive:[{}], expires in {}s ({} UTC)'.format(
            msg_prefix, delivery['attempts_made'], delivery['retry_repeats'], item.delivery_key, 
            arch_key, expire_arch_after, expires_arch_time)
        log_func(msg)
        
        cid = new_cid()
            
        if callback_list:
            broker_msg = {}
            broker_msg['action'] = SERVICE.PUBLISH
            broker_msg['delivery'] = delivery
            broker_msg['channel'] = CHANNEL.DELIVERY
            broker_msg['data_format'] = DATA_FORMAT.JSON
            
            for service in callback_list:
                broker_msg['service'] = service
                broker_msg['cid'] = new_cid()
                self.broker_client.invoke_async(broker_msg)
                    
# ##############################################################################
        
    def on_target_completed(self, target_type, target, delivery, start, end, target_ok, target_self_info, err_info=None):
        now = datetime.utcnow().isoformat()
        tx_id = delivery['tx_id']
        delivery_key = self.get_delivery_key(target_type, target, tx_id)
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, tx_id)
        total_time = str(end - start)
        
        with Lock(lock_name, self.delivery_lock_timeout, 0.2, self.kvdb.conn):

            delivery = self.kvdb.conn.hgetall(delivery_key)
            attempts_made = int(delivery['attempts_made']) + 1
                        
            delivery['attempts_made'] = attempts_made
            delivery['last_attempt_time_start_utc'] = start.isoformat()
            delivery['last_attempt_time_end_utc'] = end.isoformat()
            delivery['last_attempt_total_time'] = total_time
            delivery['last_updated_utc'] = now
            delivery['target_ok'] = target_ok
            delivery['target_self_info'] = target_self_info
            delivery['target_count'] = int(delivery['attempts_made']) + 1
            
            if target_ok:
                self.logger.info('Delivery target OK [{}] in {} after {} attempt(s)'.format(delivery_key, total_time, attempts_made))
            else:
                #failed_attempt_list = loads(delivery['failed_attempt_list'])
                #failed_attempt_list.append(err_info)
                #delivery['failed_attempt_list'] = dumps(failed_attempt_list)
                # 
                # TODO - notify_failure
                #
                pass

            self.kvdb.conn.hmset(delivery_key, delivery)            
                
            if self.logger.isEnabledFor(TRACE1):
                self.logger.log(TRACE1, delivery)

# ##############################################################################

    def resubmit(self, tx_id, ignore_missing):
        """ Resubmits given each task from the list.
        """ 
        if not self.kvdb.conn.hexists(KVDB.DELIVERY_IN_DOUBT_LIST_IDX, tx_id):
            msg = 'Could not find task {} in {}'.format(tx_id, KVDB.DELIVERY_IN_DOUBT_LIST_IDX)
            raise ValueError(msg)
        
        in_doubt_member = self.kvdb.conn.hget(KVDB.DELIVERY_IN_DOUBT_LIST_IDX, tx_id)
        in_doubt_info = in_doubt_info_from_member(in_doubt_member)
        
        in_doubt_details_key = self.get_in_doubt_details_key(in_doubt_info['name'])
        delivery_key = self.get_delivery_key(in_doubt_info['target_type'], in_doubt_info['target'], tx_id)
        
        in_doubt_details = self.kvdb.conn.hmget(in_doubt_details_key, delivery_key)[0]
        if not in_doubt_details:
            msg = 'Could not resubmit [{}], delivery under [{}] is missing'.format(tx_id, in_doubt_details_key)
            raise Exception(msg)
        else:
            item = DeliveryItem.from_in_doubt_delivery(loads(in_doubt_details))
            self.register(item, True, in_doubt_details_key, delivery_key, self.get_in_doubt_list_key(item.name), in_doubt_member)
                
    def get_batch_info(self, name, batch_size, current_batch, score_min, score_max):
        """ Returns information regarding how given set of data will be split into
        smaller batches given maximum number of items on a single batch and min/max member score
        of the set. Also returns information regarding a current batch - whether it has prev/next batches.
        """
        p = ZSetPaginator(self.kvdb.conn, self.get_in_doubt_list_key(name), batch_size, score_min=score_min, score_max=score_max)
        current = p.page(current_batch)
        return {
            'total_results': p.count,
            'num_batches': p.num_pages,
            'has_previous': current.has_previous(),
            'has_next': current.has_next(),
            'next_batch_number': current.next_page_number(),
            'previous_batch_number': current.previous_page_number(),
        }
    
# ##############################################################################

    def get_by_target_type(self, target_type):
        """ Returns delivery names and basic information for a given target type.
        """
        return self.kvdb.conn.hgetall('{}{}'.format(KVDB.DELIVERY_BY_TARGET_TYPE_PREFIX, target_type))
    
    def get_counts(self, name):
        """ Returns counters for a given delivery by its name. Does not hold onto
        any locks so the results are precise yet may be off by the time caller receives them.
        """
        in_progress_count = 0
        in_doubt_count = self.kvdb.conn.zcard(self.get_in_doubt_list_key(name))
        arch_success_count = 0
        arch_failed_count = 0
        
        return in_progress_count, in_doubt_count, arch_success_count, arch_failed_count
    
    def get_in_doubt_instance_list(self, name, batch_size, current_batch, score_min, score_max):
        """ Returns a page from a list of in-doubt delivery tasks.
        """
        p = ZSetPaginator(self.kvdb.conn, self.get_in_doubt_list_key(name), batch_size, score_min=score_min, score_max=score_max)
        current = p.page(current_batch)

        for member in current.object_list:
            yield in_doubt_info_from_member(member)
'''