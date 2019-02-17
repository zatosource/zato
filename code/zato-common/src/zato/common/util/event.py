# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from collections import deque
from datetime import datetime
from itertools import count

# gevent
from gevent.lock import RLock

# ################################################################################################################################

class default:
    max_size = 1000

# ################################################################################################################################

class Event(object):
    """ An individual event emitted to an event log.
    """
    __slots__ = 'log_id', 'event_id', 'name', 'timestamp', 'ctx'

    def __init__(self, log_id, event_id, name, ctx, _utcnow=datetime.utcnow):
        self.log_id = log_id
        self.event_id = event_id
        self.name = name
        self.ctx = ctx
        self.timestamp = _utcnow()

    def __repr__(self):
        return '<{} at {} log:{} id:{} n:{} t:{}>'.format(self.__class__.__name__, hex(id(self)),
            self.log_id, self.event_id, self.name, self.timestamp)

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'event_id': self.event_id,
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'ctx': None if self.ctx is None else repr(self.ctx)
        }

# ################################################################################################################################

class EventLog(object):
    """ A backlog of max_size events of arbitrary nature described by attributes such as ID, name, timestamp and opaque context.
    """
    def __init__(self, log_id, max_size=default.max_size):
        self.log_id = log_id
        self.event_id_counter = count(1)
        self.lock = RLock()
        self.events = deque(maxlen=max_size)

# ################################################################################################################################

    def emit(self, name, ctx=None):
        self.events.append(Event(self.log_id, next(self.event_id_counter), name, ctx))

# ################################################################################################################################

    def get_event_list(self):
        return [elem.to_dict() for elem in self.events]

# ################################################################################################################################

if __name__ == '__main__':

    el = EventLog('aaa')

    for x in range(1, 50):
        el.emit('aaa-{}'.format(x))

    print(list(reversed(el.events)))
