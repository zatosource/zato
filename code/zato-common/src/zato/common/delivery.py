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
from logging import getLogger, DEBUG
from sys import maxint
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep, spawn_later

# Paste
from paste.util.converters import asbool

# retools
from retools.lock import Lock

# SQLAlchemy
from sqlalchemy.orm.query import orm_exc

# WebHelpers
from webhelpers.paginate import Page

# Zato
from zato.common import CHANNEL, DATA_FORMAT, DELIVERY_CALLBACK_INVOKER, DELIVERY_COUNTERS, \
     DELIVERY_HISTORY_ENTRY, DELIVERY_STATE, INVOCATION_TARGET, KVDB
from zato.common.broker_message import SERVICE
from zato.common.odb.model import Delivery, DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ, \
     DeliveryHistory, DeliveryPayload
from zato.common.odb.query import delivery, delivery_list
from zato.common.util import datetime_to_seconds, new_cid, TRACE1
from zato.redis_paginator import ZSetPaginator

NULL_BASIC_DATA = {
    'last_updated_utc':None,
    DELIVERY_COUNTERS.TOTAL:0,
    DELIVERY_COUNTERS.IN_PROGRESS:0, 
    DELIVERY_COUNTERS.IN_DOUBT:0,
    DELIVERY_COUNTERS.CONFIRMED:0,
    DELIVERY_COUNTERS.FAILED:0
}

_target_def_class = {
    INVOCATION_TARGET.OUTCONN_WMQ: DeliveryDefinitionOutconnWMQ
}

DELIVERY_KEYS = ('def_name', 'target_type', 'task_id', 'creation_time_utc', 'last_used_utc', 
            'source_count', 'target_count', 'resubmit_count', 'state', 'retry_repeats', 'check_after', 'retry_seconds')

PAYLOAD_KEYS = DELIVERY_KEYS + ('payload', 'args', 'kwargs')
PAYLOAD_ALL_KEYS = PAYLOAD_KEYS + ('target',)

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

    def _history_from_source(self, delivery, item, now, entry_type):
        history = DeliveryHistory()
        history.task_id = item.task_id
        history.entry_type = entry_type
        history.entry_time = now
        history.entry_ctx = DELIVERY_HISTORY_ENTRY.NONE
        history.delivery = delivery
        history.resubmit_count = delivery.resubmit_count
        
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
        
    def register_invoke_schedule(self, item, is_resubmit=False, is_auto=False):
        """ Registers the task, invokes target and schedules a check to find out if the invocation was OK.
        """
        now = datetime.utcnow()
        
        # Sanity check - did we get everything that was needed?
        self._validate_register(item)

        # First, save everything in the ODB
        with closing(self.odb.session()) as session:
            
            if is_resubmit:
                delivery = session.merge(self.get_delivery(item.task_id))
                delivery.state = DELIVERY_STATE.IN_PROGRESS_RESUBMITTED_AUTO if is_auto else DELIVERY_STATE.IN_PROGRESS_RESUBMITTED
                delivery.resubmit_count += 1
                delivery.last_used = now
                delivery.args = item.args
                delivery.kwargs = item.kwargs
                delivery.payload.payload = item.payload
                
                session.add(
                    self._history_from_source(
                        delivery, item, now, 
                        DELIVERY_HISTORY_ENTRY.SENT_FROM_SOURCE_RESUBMIT_AUTO if is_auto else DELIVERY_HISTORY_ENTRY.SENT_FROM_SOURCE_RESUBMIT))
                
            else:
                delivery = Delivery()
                delivery.task_id = item.task_id
                delivery.name = '{}/{}/{}'.format(item.def_name, item.target, item.target_type)
                delivery.creation_time = now
                delivery.args = item.args
                delivery.kwargs = item.kwargs
                delivery.state = DELIVERY_STATE.IN_PROGRESS_STARTED
                delivery.definition_id = item.def_id
                
                payload = DeliveryPayload()
                payload.task_id = item.task_id
                payload.creation_time = now
                payload.payload = item.payload
                payload.delivery = delivery
                
                session.add(delivery)
                session.add(payload)
                session.add(self._history_from_source(delivery, item, now, DELIVERY_HISTORY_ENTRY.SENT_FROM_SOURCE))
    
                # Flush the session so the newly created delivery's definition can be reached ..
                session.flush()
                
                # .. update time the delivery was last used ..
                delivery.last_used = now
                delivery.definition.last_used = now
                
            resubmit_count = delivery.resubmit_count
            
            # .. and commit the whole transaction.
            session.commit()
            
        self.logger.info(
          'Submitting delivery [%s] for target:[%s] (%s/%s), resubmit:[%s], expire_after:[%s], check_after:[%s], retry_repeats:[%s], retry_seconds:[%s]',
            item.task_id, item.target, item.def_name, item.target_type, resubmit_count, 
            item.expire_after, item.check_after, item.retry_repeats, item.retry_seconds)
        
        # Invoke the target now that things are in the ODB
        self._invoke_delivery_service(item)

        # Spawn a greenlet to check whether target confirmed delivery
        self.spawn_check_target(item, item.check_after)

# ##############################################################################
        
    def spawn_check_target(self, item, check_after):
        """ Spawns a greenlet that checks whether the target replied and acts accordingly.
        """
        spawn_later(check_after, self.check_target, item)
        
    def _invoke_callbacks(self, target, target_type, delivery, target_ok, in_doubt, invoker):
        """ Asynchronously notifies all callback services of the outcome of the target's invocation.
        """
        callback_list = delivery.definition.callback_list
        callback_list = callback_list.split(',') or []
        
        payload = dumps({
            'target_ok': target_ok,
            'in_doubt': in_doubt,
            'task_id': delivery.task_id,
            'target': target,
            'target_type': target_type,
            'invoker': invoker
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
            delivery.last_used = now
            delivery.definition.last_used = now
            
            history = DeliveryHistory()
            history.task_id = delivery.task_id
            history.entry_type = DELIVERY_HISTORY_ENTRY.ENTERED_IN_DOUBT
            history.entry_time = now
            history.entry_ctx = DELIVERY_HISTORY_ENTRY.NONE
            history.delivery = delivery
            history.resubmit_count = delivery.resubmit_count
            
            session.add(delivery)
            session.add(history)
            
            session.commit()
            
            self._invoke_callbacks(item.target, item.target_type, delivery, False, True, DELIVERY_CALLBACK_INVOKER.SOURCE)
            
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
                expires = delivery.definition.expire_arch_succ_after
                delivery_state = DELIVERY_STATE.CONFIRMED
                history_entry_type = DELIVERY_HISTORY_ENTRY.ENTERED_CONFIRMED
            else:
                msg_prefix = 'Delivery failed'
                log_func = self.logger.warn
                expires = delivery.definition.expire_arch_fail_after
                delivery_state = DELIVERY_STATE.FAILED
                history_entry_type = DELIVERY_HISTORY_ENTRY.ENTERED_FAILED
            
            delivery.state = delivery_state
            delivery.last_used = now_dt
            delivery.definition.last_used = now_dt
                
            history = DeliveryHistory()
            history.task_id = delivery.task_id
            history.entry_type = history_entry_type
            history.entry_time = now_dt
            history.entry_ctx = DELIVERY_HISTORY_ENTRY.NONE
            history.delivery = delivery
            history.resubmit_count = delivery.resubmit_count
            
            session.add(delivery)
            session.add(history)
            
            session.commit()
            
            self._invoke_callbacks(item.target, item.target_type, delivery, target_ok, False, DELIVERY_CALLBACK_INVOKER.SOURCE)
                
            msg = '{} [{}] after {}/{} attempts, archive expires in {} hour(s) ({} UTC)'.format(
                msg_prefix, item.log_name, delivery.source_count, delivery.definition.retry_repeats, 
                expires, now_dt + timedelta(hours=expires))
            
            log_func(msg)
            
    def retry(self, delivery, item, now):
        with closing(self.odb.session()) as session:
            delivery = session.merge(delivery)
            delivery.last_used = now
            delivery.definition.last_used = now
            delivery.source_count += 1

            # 'source_count' is needed outside of the 'with' statement because
            # we want to sleep a bit and there's no need to keep the session open in that time.
            source_count = delivery.source_count
            
            session.add(delivery)
            session.add(self._history_from_source(delivery, item, datetime.utcnow(), DELIVERY_HISTORY_ENTRY.ENTERED_RETRY))
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
            self.logger.info('Stopping [%s] (definition.is_deleted->True)', item.log_name)
            return
        
        now_dt = datetime.utcnow()
        now = now_dt.isoformat()
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY, item.task_id)
        
        with closing(self.odb.session()) as session:
            try:
                delivery = session.merge(self.get_delivery(item.task_id))
                payload = delivery.payload.payload
            except orm_exc.NoResultFound, e:
                # Apparently the delivery was deleted since the last time we were scheduled to run
                self.logger.info('Stopping [%s] (NoResultFound->True)', item.log_name)
                return
        
        # Fetch new values because it's possible they have been changed since the last time we were invoked
        item['payload'] = payload
        item['args'] = delivery.args
        item['kwargs'] = delivery.kwargs
        
        with Lock(lock_name, self.delivery_lock_timeout, LOCK_TIMEOUT, self.kvdb.conn):

            # Target did not reply at all hence we're entering in-doubt
            if delivery.source_count > delivery.target_count:
                self._on_in_doubt(item, delivery, now)
                
            else:
                # The target has confirmed the invocation in an expected time so we
                # now need to check if it was successful. If it was, this is where it ends,
                # it wasn't, we'll try again as it was originally configured unless
                # it was the last retry.
                
                target_ok = delivery.state == DELIVERY_STATE.IN_PROGRESS_TARGET_OK
                
                # All good, we can stop now.
                if target_ok:
                    self.finish_delivery(delivery, target_ok, now_dt, item)
                    
                # Not so good, we know there was an error.
                else:
                    # Can we try again?
                    if delivery.source_count < item.retry_repeats:
                        self.retry(delivery, item, now)

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
        
    def update_counters(self, name, in_progress, in_doubt, confirmed, failed):
        """ Updates counters of a given delivery definition.
        """
        counters = {
            DELIVERY_COUNTERS.IN_PROGRESS: in_progress,
            DELIVERY_COUNTERS.IN_DOUBT: in_doubt,
            DELIVERY_COUNTERS.CONFIRMED: confirmed,
            DELIVERY_COUNTERS.FAILED: failed,
            DELIVERY_COUNTERS.TOTAL: in_progress + in_doubt + confirmed + failed,
            'last_updated_utc': datetime.utcnow().isoformat(),
        }
        
        self.kvdb.conn.hmset('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name), counters)
        
    def get_counters(self, name):
        """ Returns usage counters for a given delivery definition.
        """
        keys = [DELIVERY_COUNTERS.IN_PROGRESS, DELIVERY_COUNTERS.IN_DOUBT, DELIVERY_COUNTERS.CONFIRMED,
                     DELIVERY_COUNTERS.FAILED, DELIVERY_COUNTERS.TOTAL]
        values = self.kvdb.conn.hmget('{}{}'.format(KVDB.DELIVERY_BY_TARGET_PREFIX, name), keys)
        
        return dict(zip(keys, values))

# ##############################################################################

    def deliver(self, cluster_id, def_name, payload, task_id, invoke_func, is_resubmit=False, is_auto=False, *args, **kwargs):
        """ A public method to be invoked by services for delivering payload to target through a definition.
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
            
        self.register_invoke_schedule(
            _item_from_api(delivery_def_base, target, payload, task_id, invoke_func, args, kwargs),
            is_resubmit, is_auto)

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
                delivery = session.merge(self.get_delivery(task_id))
                delivery.state = DELIVERY_STATE.IN_PROGRESS_TARGET_OK if target_ok else DELIVERY_STATE.IN_PROGRESS_TARGET_FAILURE
                delivery.last_used = now
                delivery.definition.last_used = now
                delivery.target_count += 1
                
                history = DeliveryHistory()
                history.task_id = task_id
                history.entry_type = DELIVERY_HISTORY_ENTRY.TARGET_OK if target_ok else DELIVERY_HISTORY_ENTRY.TARGET_FAILURE
                history.entry_time = now
                history.entry_ctx = entry_ctx
                history.delivery = delivery
                history.resubmit_count = delivery.resubmit_count
                
                session.add(delivery)
                session.add(history)
                
                session.commit()
                
                self._invoke_callbacks(target, target_type, delivery, target_ok, False, DELIVERY_CALLBACK_INVOKER.TARGET)

# ##############################################################################

    def _get_page(self, session, cluster_id, params, state):
        return Page(delivery_list(session, cluster_id, params.def_name, state, params.start, params.stop, params.get('needs_payload', False)),
             page=params.current_batch,
             items_per_page=params.batch_size)

    def get_batch_info(self, cluster_id, params, state):
        """ Returns information regarding how given set of data will be split into
        smaller batches given maximum number of items on a single batch and min/max member score
        of the set. Also returns information regarding a current batch - whether it has prev/next batches.
        """
        with closing(self.odb.session()) as session:
            page = self._get_page(session, cluster_id, params, state)
            return {
                'total_results': page.item_count,
                'num_batches': page.page_count,
                'has_previous': page.previous_page is not None,
                'has_next': page.next_page is not None,
                'next_batch_number': page.next_page,
                'previous_batch_number': page.previous_page,
            }

    def get_delivery_instance_list(self, cluster_id, params, state):
        """ Returns a batch of instances that are in the in-doubt state.
        """
        with closing(self.odb.session()) as session:
            page = self._get_page(session, cluster_id, params, state)
            for values in page.items:
                out = dict(zip((PAYLOAD_KEYS if params.get('needs_payload') else DELIVERY_KEYS), values))
                for name in('creation_time_utc', 'last_used_utc'):
                    out[name] = out[name].isoformat()
                    
                yield out
                
    def get_delivery_instance(self, task_id, target_def_class):
        """ Returns an instance by its task's ID.
        """
        with closing(self.odb.session()) as session:
            out = delivery(session, task_id, target_def_class).\
                   one()
            out = dict(zip(PAYLOAD_ALL_KEYS, out))
            for name in('creation_time_utc', 'last_used_utc'):
                out[name] = out[name].isoformat()
                
            return out

# ##############################################################################

    def update_delivery(self, task_id, payload, args, kwargs):
        with closing(self.odb.session()) as session:
            now = datetime.utcnow().isoformat()
            delivery = session.merge(self.get_delivery(task_id))
            
            old_payload = delivery.payload.payload
            old_args = delivery.args
            old_kwargs = delivery.kwargs
            
            delivery.payload.payload = payload
            delivery.args = args
            delivery.kwargs = kwargs
            
            delivery.definition.last_used = now
            delivery.target_count += 1
            
            entry_ctx = dumps({
                'old_payload': old_payload,
                'old_args': old_args,
                'old_kwargs': old_kwargs,
                })
            
            history = DeliveryHistory()
            history.task_id = task_id
            history.entry_type = DELIVERY_HISTORY_ENTRY.UPDATED
            history.entry_time = now
            history.entry_ctx = entry_ctx
            history.delivery = delivery
            history.resubmit_count = delivery.resubmit_count
            
            session.add(delivery)
            session.add(history)
            
            session.commit()
            
            self.logger.info('Updated delivery [%s], history.id [%s]', task_id, history.id)

# ##############################################################################

    def get_delivery_list_for_auto_resubmit(self, cluster_id, def_name, stop):
        params = Bunch({
            'def_name': def_name,
            'start': None,
            'stop': stop,
            'current_batch': 1,
            'batch_size': maxint,
            'needs_payload': True,
        })
        for item in self.get_delivery_instance_list(
                cluster_id, params, [DELIVERY_STATE.IN_PROGRESS_STARTED, 
                                      DELIVERY_STATE.IN_PROGRESS_RESUBMITTED,
                                      DELIVERY_STATE.IN_PROGRESS_RESUBMITTED_AUTO,
                                      DELIVERY_STATE.IN_PROGRESS_TARGET_OK, 
                                      DELIVERY_STATE.IN_PROGRESS_TARGET_FAILURE]):
            yield item
