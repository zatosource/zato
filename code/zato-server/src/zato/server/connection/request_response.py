# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common import KVDB
from zato.common.util import TRACE1 # TODO: TRACE1 should be moved over to zato.common

logger = logging.getLogger(__name__)

def should_store(kvdb, service_usage, service_name):
    """ Decides whether a service's request/response pair should be kept in the DB.
    """
    key = '{}{}'.format(KVDB.REQ_RESP_SAMPLE, service_name)
    freq = int(kvdb.conn.hget(key, 'freq') or 0)
    
    if freq and service_usage % freq == 0:
        return key, freq
    
    return None, None

def store(kvdb, key, usage, freq, **data):
    """ Stores a service's request/response pair.
    """
    if logger.isEnabledFor(TRACE1):
        msg = 'key:[{}], usage:[{}], freq:[{}], data:[{}]'.format(key, usage, freq, data)
        logger.log(TRACE1, msg)
        
    kvdb.conn.hmset(key, data)
