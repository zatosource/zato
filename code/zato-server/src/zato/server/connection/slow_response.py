# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import KVDB, TRACE1
from zato.common.json_internal import dumps

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
