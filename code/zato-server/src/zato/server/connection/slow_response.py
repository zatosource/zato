# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# anyjson
from anyjson import dumps

# Zato
from zato.common import KVDB
from zato.common.util import TRACE1 # TODO: TRACE1 should be moved over to zato.common

logger = logging.getLogger(__name__)

def store(kvdb, name, **data):
    """ Stores information regarding an invocation that came later than it was allowed.
    """
    key = '{}{}'.format(KVDB.RESP_SLOW, name)
    data = dumps(data)
    
    if logger.isEnabledFor(TRACE1):
        msg = 'key:[{}], name:[{}], data:[{}]'.format(key, name, data)
        logger.log(TRACE1, msg)
        
    kvdb.conn.lpush(key, data)
    kvdb.conn.ltrim(key, 0, 99) # TODO: This should be configurable
