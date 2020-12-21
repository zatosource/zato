# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import deque
from datetime import datetime, timedelta

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import GENERIC

# ################################################################################################################################
# ################################################################################################################################

event_attrs    = 'data', 'timestamp', 'msg_id', 'in_reply_to', 'type_', 'object_id', 'conn_id'

transfer_attrs = 'total_bytes_received', 'total_messages_received', 'avg_msg_size_received', 'first_received', 'last_received', \
                 'total_bytes_sent',     'total_messages_sent',     'avg_msg_size_sent',     'first_sent',     'last_sent'

config_attrs   = 'type_', 'object_id', 'max_len_messages_received',      'max_len_messages_sent',     \
                                       'max_bytes_per_message_received', 'max_bytes_per_message_sent'

# ################################################################################################################################
# ################################################################################################################################

class _DataEvent:
    def __init__(self):
        self.data = ''
        self.timestamp = None # type: datetime
        self.msg_id = ''
        self.in_reply_to = ''
        self.type_ = ''
        self.object_id = ''
        self.conn_id = ''

# ################################################################################################################################

    def to_dict(self):
        out = {}
        for name in event_attrs:
            out[name] = getattr(self, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class DataSent(_DataEvent):
    """ An individual piece of data sent by Zato to a remote end.
    This can be a request or a reply to a previous one sent by an API client.
    """
    __slots__ = event_attrs

# ################################################################################################################################
# ################################################################################################################################

class DataReceived(_DataEvent):
    """ An individual piece of data received by Zato from a remote end.
    This can be a request or a reply to a previous one sent by an API client.
    """
    __slots__ = event_attrs

# ################################################################################################################################
# ################################################################################################################################

class LogContainerConfig:
    """ Data retention configuration for a specific object.
    """
    __slots__ = config_attrs

    def __init__(self):
        self.type_ = '<log-container-config-type_-not-set>'
        self.object_id = '<log-container-config-object_id-not-set>'
        self.max_len_messages_received = 0
        self.max_len_messages_sent = 0
        self.max_bytes_per_message_received = 0
        self.max_bytes_per_message_sent = 0

# ################################################################################################################################
# ################################################################################################################################

class LogContainer:
    """ Stores messages for a specific object, e.g. an individual REST or HL7 channel.
    """
    __slots__ = config_attrs +  transfer_attrs

    def __init__(self, config):
        # type: (LogContainerConfig)

        self.type_ = config.type_
        self.object_id = config.object_id

        self.max_len_messages_received      = config.max_len_messages_received
        self.max_len_messages_sent          = config.max_len_messages_sent
        self.max_bytes_per_message_received = config.max_bytes_per_message_received
        self.max_bytes_per_message_sent     = config.max_len_messages_sent

        self.total_bytes_received    = 0
        self.total_messages_received = 0
        self.avg_msg_size_received   = 0
        self.first_received          = None # type: datetime
        self.last_received           = None # type: datetime

        self.total_bytes_sent    = 0
        self.total_messages_sent = 0
        self.avg_msg_size_sent   = 0
        self.first_sent          = None # type: datetime
        self.last_sent           = None # type: datetime

        # These two deques are where the actual data is kept
        self.messages_received = deque(maxlen=self.max_len_messages_received)
        self.messages_sent     = deque(maxlen=self.max_len_messages_sent)

# ################################################################################################################################
# ################################################################################################################################

class MessageLog:
    """ Stores a log of messages for channels, outgoing connections or other objects.
    """
    def __init__(self):

        # Update lock
        self.lock = RLock()

        # The main log - keys are object types, values are dicts mapping object IDs to LogContainer objects
        self._log = {
            'rest': {
                '1': LogContainer()
            }
        }

# ################################################################################################################################

    def _create_container(self, config):
        # type: (LogContainerConfig)

        # Make sure the object ID is a string (it can be an int)
        config.object_id = str(config.object_id)

        # Get the mapping of object types to object IDs ..
        container_dict = self._log.setdefault(config.type_, {})

        # .. make sure we do not have such an object already ..
        if config.object_id in container_dict:
            raise ValueError('Container already found `{}` ({})'.format(config.object_id, config.type_))

        # .. if we are here, it means that we are really adding a new container ..
        container = LogContainer(config)

        # .. finally, we can attach it to the log by the object's ID.
        container_dict[config.object_id] = container

# ################################################################################################################################

    def create_container(self, config):
        # type: (LogContainerConfig)
        with self.lock:
            self._create_container(config)

# ################################################################################################################################

    def _delete_container(self, config):
        # type: (LogContainerConfig)

        # Make sure the object ID is a string (it can be an int)
        config.object_id = str(config.object_id)

        # Get the mapping of object types to object IDs ..
        try:
            container_dict = self._log[config.type_]
        except KeyError:
            raise ValueError('Container type not found `{}` ({})'.format(config.type_, config.object_id))

        # No KeyError = we recognised that type ..

        # .. so we can now try to delete that container by its object's ID
        try:
            del container_dict[config.object_id]
        except KeyError:
            raise ValueError('Object container not found `{}` ({})'.format(config.type_, config.object_id))

# ################################################################################################################################

    def delete_container(self, config):
        # type: (LogContainerConfig)
        with self.lock:
            self._delete_container(config)

# ################################################################################################################################

    def edit_container(self, config):
        # type: (LogContainerConfig)
        with self.lock:
            self._delete_container(config)
            self._create_container(config)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    pass
