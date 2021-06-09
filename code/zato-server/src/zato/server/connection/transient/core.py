# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.ext.dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ObjectCtx:

    # A unique identifer assigned to this event by Zato
    id: str

    # A correlation ID assigned by Zato - multiple events may have the same CID
    cid: str

    # Timestamp of this event, as assigned by Zato
    timestamp: str

    # The actual business data
    data: object

# ################################################################################################################################
# ################################################################################################################################

class TransientAPI:
    """ Manages named transient repositories.
    """
    def __init__(self):
        self.repo = {} # str -> TransientRepository objects
        self.lock = RLock()

# ################################################################################################################################

    def get(self, name):
        # type: (str) -> TransientRepository
        pass

# ################################################################################################################################

    def push(self, name):
        pass

# ################################################################################################################################

    def get(self, name, object_id):
        # type: (str, str) -> None
        pass

# ################################################################################################################################

    def get_list(self, name):
        # type: (str) -> None
        pass

# ################################################################################################################################

    def delete(self, name, object_id):
        # type: (str) -> None
        pass

# ################################################################################################################################

    def clear(self, name):
        # type: (str) -> None
        pass

# ################################################################################################################################
# ################################################################################################################################

class TransientRepository:
    """ Stores arbitrary objects, as a list, in RAM only, without backing persistent storage.
    """
    def __init__(self, name='<TransientRepository-name>', max_size=1000):
        # type: (str, int) -> None

        # Our user-visible name
        self.name = name

        # How many objects we will keep at most
        self.max_size = max_size

        # In-RAM database of objects
        self.in_ram_store = [] # type: list[ObjectCtx]

        # Used to synchronise updates
        self.lock = RLock()

# ################################################################################################################################

    def push(self, ctx):
        # type: (ObjectCtx)
        with self.lock:

            # Push new data ..
            self.in_ram_store.append(ctx)

            # .. and ensure our max_size is not exceeded ..
            if len(self.in_ram_store) > self.max_size:

                # .. we maintain a FIFO list, deleting the oldest entriest first.
                del self.in_ram_store[self.max_size:]

# ################################################################################################################################

    def get_size(self):
        with self.lock:
            return len(self.in_ram_store)

# ################################################################################################################################

    def get(self, object_id):
        # type: (str) -> None
        with self.lock:
            for item in self.in_ram_store: # type: ObjectCtx
                if item.id == object_id:
                    return item
            else:
                raise KeyError('Object not found `{}`'.format(object_id))

# ################################################################################################################################

    def get_list(self):
        pass

# ################################################################################################################################

    def delete(self, object_id):
        # type: (str) -> None
        with self.lock:
            for item in self.in_ram_store: # type: ObjectCtx
                if item.id == object_id:
                    self.in_ram_store.remove(item)
                    break

# ################################################################################################################################

    def clear(self):
        with self.lock:
            self.in_ram_store[:] = []

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    transient = TransientStorage()

# ################################################################################################################################
# ################################################################################################################################
