# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

