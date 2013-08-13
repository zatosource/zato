# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Unlike zato.common.odb.model - this place is where DB-independent models are kept,
# regardless if they're backed by an SQL database or not.

# anyjson
from anyjson import loads

class DeliveryItem(object):
    """ A container for config pieces regarding a particular delivery effort.
    """
    def __init__(self):
        self.name = None
        self.target = None
        self.target_type = None
        self.tx_id = None
        self.payload = None
        self.expire_after = None
        self.expire_arch_success_after = None
        self.expire_arch_failed_after = None
        self.special_case_weekends = False
        self.check_after = None
        self.retry_repeats = None
        self.retry_seconds = None
        self.invoke_func = None
        self.invoke_args = None
        self.invoke_kwargs = None
        self.payload_key = None
        self.by_target_type_key = None
        self.uq_by_target_type_key = None
        self.on_delivery_success = []
        self.on_delivery_failed = []
        
        self.source_count = None
        self.target_count = None
        
        self.creation_time_utc = None
        self.creation_time = None # In current user's timezone
        
        self.in_doubt_created_at_utc = None
        self.in_doubt_created_at = None # In current user's timezone
        self.in_doubt_history = []
        
        self.last_updated_utc = None
        self.last_updated = None # In current user's timezone

    @staticmethod
    def from_in_doubt_payload(payload):
        """
        {
          u'on_delivery_failed': u'[]',
          u'failed_attempt_list': u'[]',
          u'retry_seconds': u'1',
          u'expire_arch_success_after': u'212000',
          u'retry_repeats': u'2',
          u'target': u'My MQ app2',
          u'expire_arch_failed_after': u'248000',
          
          u'on_delivery_success': u'[]',
          u'tx_id': u'K227565965020125164468072876391937359452',
          
          u'name': u'anon-outconn-wmq-My MQ app2-2-1-3-26000-212000-248000',
          u'check_after': u'3',
          u'target_type': u'outconn-wmq',
          
          u'payload': 
           u"{u'body': 'my-message', u'priority': None, u'args': (), 
              u'name': 'My MQ app2', u'delivery_mode': None,
              u'confirm_delivery': True, u'queue': 'Q1',
              u'tx_id': u'K227565965020125164468072876391937359452',
              u'max_chars_printed': None, u'expiration': None,
              u'kwargs': {}, u'action': '10607'}", 
          
          u'in_doubt_created_source_count': 1L,
          u'last_attempt_time_end_utc': u'None',
          u'last_updated_utc': u'2013-08-12T21:37:46.887253',
          u'attempts_made': u'0',
          u'last_attempt_total_time': u'None',
          u'confirmed': u'False',
          u'in_doubt_created_at_utc': u'2013-08-12T21:37:49.889139',
          u'creation_time_utc': u'2013-08-12T21:37:46.887253',
          u'in_doubt_created_target_count': 0L,
          u'source_count': u'1',
          u'target_ok': u'False',
          u'target_count': u'0',
          u'in_doubt': True,
          u'target_self_info': u'None',
          u'expires_arch_time_utc': u'None',
          u'last_attempt_time_start_utc': u'None'
        }
        """
        item = DeliveryItem()
        
        item.tx_id = payload['tx_id']
        item.name = payload['name']
        item.target = payload['target']
        item.target_type = payload['target_type']
        
        item.expire_arch_success_after = int(payload['expire_arch_success_after'])
        item.expire_arch_failed_after = int(payload['expire_arch_failed_after'])
        
        item.check_after = int(payload['check_after'])
        item.retry_repeats = int(payload['retry_repeats'])
        item.retry_seconds = int(payload['retry_seconds'])
        
        item.payload = loads(payload['payload'])
        item.failed_attempt_list = loads(payload['failed_attempt_list'])
        item.on_delivery_success = loads(payload['on_delivery_success'])
        item.on_delivery_failed = loads(payload['on_delivery_failed'])
        
        return item