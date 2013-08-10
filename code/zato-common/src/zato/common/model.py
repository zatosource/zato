# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Unlike zato.common.odb.model - this place is where DB-independent models are kept,
# regardless if they're backed by an SQL database or not.

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
        self.last_updated_utc = None
        self.last_updated = None # In current user's timezone
