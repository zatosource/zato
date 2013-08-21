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
from traceback import format_exc

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
from zato.common import CHANNEL, DATA_FORMAT, DELIVERY_HISTORY_ENTRY, DELIVERY_STATE, INVOCATION_TARGET, KVDB
from zato.common.broker_message import SERVICE
from zato.common.odb.model import Delivery, DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ, \
     DeliveryHistory, DeliveryPayload, to_json
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

LOCK_TIMEOUT = 0.2
RETRY_SLEEP = 5

def _item_from_api(delivery_def_base, target, payload, task_id, invoke_func, args, kwargs):
    """ Creates an invocation context. 
    """
    return Bunch({
        'task_id': task_id,
        'def_id': delivery_def_base.id,
        'def_name': delivery_def_base.name,
        'target': target,
        'target_type': delivery_def_base.target_type,
        'expire_after': delivery_def_base.expire_after,
        'check_after': delivery_def_base.check_after,
        'retry_repeats': delivery_def_base.retry_repeats,
        'retry_seconds': delivery_def_base.retry_seconds,
        'payload': payload,
        'invoke_func': invoke_func,
        'args': dumps(args),
        'kwargs': dumps(kwargs),
        'log_name': '{}/{}/{}'.format(delivery_def_base.name, target, task_id),
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

    def _history_sent_from_source(self, delivery, item, now):
        history = DeliveryHistory()
        history.task_id = item.task_id
        history.entry_type = DELIVERY_HISTORY_ENTRY.SENT_FROM_SOURCE
        history.entry_time = now
        history.entry_ctx = DELIVERY_HISTORY_ENTRY.NONE
        history.delivery = delivery
        
        return history

    def _validate_register(self, item):
        if not(item.check_after and item.retry_repeats and item.retry_seconds):
            msg = 'check_after:[{}], retry_repeats:[{}] and retry_seconds:[{}] are all required'.format(
                item.check_after, item.retry_repeats, item.retry_seconds)
            self.logger.error(msg)
            raise ValueError(msg)
        
    def _invoke_delivery_service(self, item):
        """ Invokes the target via a delivery service. 
        """
        delivery_req = {}
        for name in('task_id', 'payload', 'target', 'target_type', 'args', 'kwargs'):
            delivery_req[name] = item[name]
            
        item.invoke_func('zato.pattern.delivery.dispatch', delivery_req)
        
    def register_invoke_schedule(self, item):
        """ Registers the task, invokes target and schedules a check to find out if the invocation was OK.
        """
        now = datetime.utcnow()
        
        # Sanity check - did we get everything that was needed?
        self._validate_register(item)
        
        # First, save everything in the ODB
        with closing(self.odb.session()) as session:
            
            delivery = Delivery()
            delivery.task_id = item.task_id
            delivery.creation_time = now
            delivery.name = '{}/{}/{}'.format(item.def_name, item.target, item.target_type)
            delivery.delivery_def_id = item.def_id
            delivery.state = DELIVERY_STATE.IN_PROGRESS
            
            payload = DeliveryPayload()
            payload.task_id = item.task_id
            payload.creation_time = now
            payload.payload = item.payload
            payload.delivery = delivery
            
            session.add(delivery)
            session.add(payload)
            session.add(self._history_sent_from_source(delivery, item, now))
            
            session.commit()
            
        self.logger.info(
          'Submitting delivery [%s] for target:[%s] (%s/%s), expire_after:[%s], check_after:[%s], retry_repeats:[%s], retry_seconds:[%s]',
            item.task_id, item.target, item.def_name, item.target_type, item.expire_after, item.check_after, item.retry_repeats, item.retry_seconds)
        
        # Invoke the target now that things are in the ODB
        self._invoke_delivery_service(item)

        # Spawn a greenlet to check whether target confirmed delivery
        self.spawn_check_target(item, item.check_after)

# ##############################################################################
        
    def spawn_check_target(self, item, check_after):
        """ Spawns a greenlet that checks whether the target replied and acts accordingly.
        """
        spawn_later(check_after, self.check_target, item)
        
    def _invoke_callbacks(self, item, delivery, target_ok, in_doubt):
        """ Asynchronously notifies all callback services of the outcome of the target's invocation.
        """
        callback_list = delivery.delivery_def.callback_list
        callback_list = callback_list.split(',') or []
        
        payload = dumps({
            'target_ok': target_ok,
            'in_doubt': in_doubt,
            'task_id': delivery.task_id,
            'payload': item.payload,
            'target': item.target,
            'target_type': item.target_type,
        })

        for service in callback_list:
            if service:
                broker_msg = {}
                broker_msg['action'] = SERVICE.PUBLISH
                broker_msg['task_id'] = delivery.task_id
                broker_msg['channel'] = CHANNEL.DELIVERY
                broker_msg['data_format'] = DATA_FORMAT.JSON
                broker_msg['service'] = service
                broker_msg['payload'] = payload
                broker_msg['cid'] = new_cid()
                
                try:
                    self.broker_client.invoke_async(broker_msg)
                except Exception, e:
                    msg = 'Could not invoke callback:[%s], task_id:[%s], e:[%s]'.format(
                        service, delivery.task_id, format_exc(e))
                    self.logger.warn(msg)
        
# ##############################################################################
        
    def _on_in_doubt(self, item, delivery, now):
        """ Delivery enteres an in-doubt state.
        """
        with closing(self.odb.session()) as session:
            delivery = session.merge(delivery)
            delivery.state = DELIVERY_STATE.IN_DOUBT
            
            history = DeliveryHistory()
            history.task_id = delivery.task_id
            history.entry_type = DELIVERY_HISTORY_ENTRY.ENTERED_IN_DOUBT
            history.entry_time = now
            history.entry_ctx = DELIVERY_HISTORY_ENTRY.NONE
            history.delivery = delivery
            
            session.add(delivery)
            session.add(history)
            
            session.commit()
            
            self._invoke_callbacks(item, delivery, False, True)
            
            msg = 'Delivery [%s] is in-doubt (source/target %s/%s)'
            self.logger.warn(msg, item.log_name, delivery.source_count, delivery.target_count)
            
    def finish_delivery(self, delivery, target_ok, now_dt, item):
        """ Called after running out of attempts to deliver the payload.
        """
        with closing(self.odb.session()) as session:
            delivery = session.merge(delivery)
            
            if target_ok:
                msg_prefix = 'Confirmed delivery'
                log_func = self.logger.info
                expires = delivery.delivery_def.expire_arch_succ_after
                delivery_state = DELIVERY_STATE.CONFIRMED
                history_entry_type = DELIVERY_HISTORY_ENTRY.ENTERED_CONFIRMED
            else:
                msg_prefix = 'Delivery failed'
                log_func = self.logger.warn
                expires = delivery.delivery_def.expire_arch_fail_after
                delivery_state = DELIVERY_STATE.FAILED
                history_entry_type = DELIVERY_HISTORY_ENTRY.ENTERED_FAILED
                
            delivery.state = delivery_state
                
            history = DeliveryHistory()
            history.task_id = delivery.task_id
            history.entry_type = history_entry_type
            history.entry_time = now_dt
            history.entry_ctx = DELIVERY_HISTORY_ENTRY.NONE
            history.delivery = delivery
            
            session.add(delivery)
            session.add(history)
            
            session.commit()
                
            msg = '{} [{}] after {}/{} attempts, archive expires in {} hour(s) ({} UTC)'.format(
                msg_prefix, item.log_name, delivery.source_count, delivery.delivery_def.retry_repeats, 
                expires, now_dt + timedelta(hours=expires))
            
            log_func(msg)
            
    def retry(self, delivery, item):
        with closing(self.odb.session()) as session:
            delivery = session.merge(delivery)
            delivery.source_count += 1

            # This is needed as a separate thing because we want to sleep a bit
            # and there's no need to keep the session open in that time.
            source_count = delivery.source_count
            
            session.add(delivery)
            session.add(self._history_sent_from_source(delivery, item, datetime.utcnow()))
            session.commit()
            
            # Sleep a constant time so we're sure any locks related to that task are released
            sleep(RETRY_SLEEP)
            
        self.logger.info('Retrying delivery [%s] (%s/%s)', item.log_name, source_count, item.retry_repeats)
        
        self._invoke_delivery_service(item)
        self.spawn_check_target(item, item.retry_seconds)
                
# ##############################################################################
        
    def check_target(self, item):
        self.logger.debug('Checking name/target/task_id [%s]', item.log_name)
        
        if self.is_deleted(item.def_name):
            self.logger.info('Stopping [%s] (is_deleted->True)', item.log_name)
            return
        
        now_dt = datetime.utcnow()
        now = now_dt.isoformat()
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, item.task_id)
        
        delivery = self.get_delivery(item.task_id)
        
        with Lock(lock_name, self.delivery_lock_timeout, LOCK_TIMEOUT, self.kvdb.conn):

            # Target did not reply at all hence we're entering in-doubt
            if delivery.source_count > delivery.target_count:
                self._on_in_doubt(item, delivery, now)
                
            else:
                # The target has confirmed the invocation in an expected time so we
                # now need to check if it was successful. If it was, this is where it ends,
                # it wasn't, we'll try again as it was originally configured unless
                # it was the last retry.
                
                target_ok = delivery.state == DELIVERY_STATE.TARGET_OK
                
                # All good, we can stop now.
                if target_ok:
                    self.finish_delivery(delivery, target_ok, now_dt, item)
                    
                # Not so good, we know there was an error.
                else:
                    # Can we try again?
                    if delivery.source_count < item.retry_repeats:
                        self.retry(delivery, item)

                    # Nope, that was the last attempt.
                    else:
                        self.finish_delivery(delivery, target_ok, now_dt, item)

# ##############################################################################

    def get_delivery(self, task_id):
        with closing(self.odb.session()) as session:
            delivery = session.query(Delivery).\
                filter(Delivery.task_id==task_id).\
                one()
            
        return delivery

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
        
    def is_deleted(self, name):
        """ Returns a boolean flag indicating whether a given definition has been deleted in between
        a delivery's executions.
        """
        return not self.kvdb.conn.hget('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name), 'deleted')
        
    def set_updated(self, name, is_updated):
        """ Sets a boolean flag indicating whether a definition has been updated.
        Any new instances of check_target consult this flag to see whether they should
        perhaps change their schedule.
        """
        self.kvdb.conn.hset('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name), 'updated', is_updated)

# ##############################################################################

    def deliver(self, cluster_id, def_name, payload, task_id, invoke_func, *args, **kwargs):
        """ A public method to be invoked by services for delivering payload to a target
        through a definition.
        """
        with closing(self.odb.session()) as session:
            delivery_def_base = session.query(DeliveryDefinitionBase).\
                filter(DeliveryDefinitionBase.cluster_id==cluster_id).\
                filter(DeliveryDefinitionBase.name==def_name).\
                    first()
            
            if not delivery_def_base:
                msg = 'Guaranteed delivery definition [{}] does not exist'.format(def_name)
                self.logger.warn(msg)
                raise ValueError(msg)
            
            target_def_class = _target_def_class[delivery_def_base.target_type]
            definition = session.query(target_def_class).\
                filter(target_def_class.id==delivery_def_base.id).\
                one()
            
            target = definition.target.name
            
        self.register_invoke_schedule(_item_from_api(delivery_def_base, target, payload, task_id, invoke_func, args, kwargs))

# ##############################################################################
        
    def on_target_completed(self, target_type, target, delivery, start, end, target_ok, target_self_info, err_info=None):
        now = datetime.utcnow().isoformat()
        task_id = delivery['task_id']
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, task_id)
        total_time = str(end - start)
        
        with Lock(lock_name, self.delivery_lock_timeout, LOCK_TIMEOUT, self.kvdb.conn):
            entry_ctx = dumps({
                'target_self_info': target_self_info,
                'total_time': total_time
            })
            
            with closing(self.odb.session()) as session:
                delivery = self.get_delivery(task_id)
                delivery.state = DELIVERY_STATE.TARGET_OK if target_ok else DELIVERY_STATE.TARGET_FAILURE
                delivery.target_count += 1
                
                history = DeliveryHistory()
                history.task_id = task_id
                history.entry_type = DELIVERY_HISTORY_ENTRY.TARGET_OK if target_ok else DELIVERY_HISTORY_ENTRY.TARGET_FAILURE
                history.entry_time = now
                history.entry_ctx = entry_ctx
                history.delivery = delivery
                
                session.add(delivery)
                session.add(history)
                
                session.commit()

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