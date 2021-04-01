# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import deque
from datetime import datetime
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import AuditLog as CommonAuditLog, CHANNEL, GENERIC, WEB_SOCKET
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

_sent     = CommonAuditLog.Direction.sent
_received = CommonAuditLog.Direction.received


event_attrs    = 'direction', 'data', 'event_id', 'timestamp', 'msg_id', 'in_reply_to', 'type_', 'object_id', 'conn_id'

transfer_attrs = 'total_bytes_received', 'total_messages_received', 'avg_msg_size_received', 'first_received', 'last_received', \
                 'total_bytes_sent',     'total_messages_sent',     'avg_msg_size_sent',     'first_sent',     'last_sent',     \
                 'data', 'messages'

config_attrs   = 'type_', 'object_id', 'max_len_messages_received',      'max_len_messages_sent',      \
                                       'max_bytes_per_message_received', 'max_bytes_per_message_sent', \
                                       'max_bytes_per_message'

# ################################################################################################################################
# ################################################################################################################################

def new_event_id(prefix='zae', _new_cid=new_cid):
    return '{}{}'.format(prefix, _new_cid())

# ################################################################################################################################
# ################################################################################################################################

class DataEvent:
    def __init__(self, direction, _utcnow=datetime.utcnow, _new_event_id=new_event_id):
        self.direction = direction
        self.event_id = _new_event_id()
        self.data = ''
        self.timestamp = _utcnow()
        self.msg_id = ''
        self.in_reply_to = ''
        self.type_ = ''
        self.object_id = ''
        self.conn_id = ''

        # This will be the other half of a request or response,
        # e.g. it will link DataSent to DataReceived or ther other way around.
        self.counterpart = None # type: DataEvent

# ################################################################################################################################

    def to_dict(self):
        out = {}
        for name in event_attrs:
            out[name] = getattr(self, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class DataSent(DataEvent):
    """ An individual piece of data sent by Zato to a remote end.
    This can be a request or a reply to a previous one sent by an API client.
    """
    __slots__ = event_attrs

    def __init__(self, _direction=_sent):
        super().__init__(_direction)

# ################################################################################################################################
# ################################################################################################################################

class DataReceived(DataEvent):
    """ An individual piece of data received by Zato from a remote end.
    This can be a request or a reply to a previous one sent by an API client.
    """
    __slots__ = event_attrs

    def __init__(self, _direction=_received):
        super().__init__(_direction)

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
    __slots__ = config_attrs + transfer_attrs + ('lock',)

    def __init__(self, config, _sent=_sent, _received=_received):
        # type: (LogContainerConfig)

        # To serialise access to the underlying storage
        self.lock = {
            _sent: RLock(),
            _received: RLock(),
        }

        self.type_ = config.type_
        self.object_id = config.object_id

        self.max_len_messages_sent          = config.max_len_messages_sent
        self.max_len_messages_received      = config.max_len_messages_received

        self.max_bytes_per_message = {
            _sent:     config.max_bytes_per_message_sent,
            _received: config.max_bytes_per_message_received,
        }

        self.total_bytes_sent    = 0
        self.total_messages_sent = 0
        self.avg_msg_size_sent   = 0
        self.first_sent          = None # type: datetime
        self.last_sent           = None # type: datetime

        self.total_bytes_received    = 0
        self.total_messages_received = 0
        self.avg_msg_size_received   = 0
        self.first_received          = None # type: datetime
        self.last_received           = None # type: datetime

        # These two deques are where the actual data is kept
        self.messages = {}
        self.messages[_sent]     = deque(maxlen=self.max_len_messages_sent)
        self.messages[_received] = deque(maxlen=self.max_len_messages_received)

# ################################################################################################################################

    def store(self, data_event):
        with self.lock[data_event.direction]:

            # Make sure we do not exceed our limit of bytes stored
            max_len = self.max_bytes_per_message[data_event.direction]
            data_event.data = data_event.data[:max_len]

            storage = self.messages[data_event.direction] # type: deque
            storage.append(data_event)

# ################################################################################################################################

    def to_dict(self, _sent=_sent, _received=_received):
        out = {
            _sent: [],
            _received: []
        }

        for name in (_sent, _received):
            messages = out[name]
            with self.lock[name]:
                for message in self.messages[name]: # type: DataEvent
                    messages.append(message.to_dict())

        return out

# ################################################################################################################################
# ################################################################################################################################

class AuditLog:
    """ Stores a log of messages for channels, outgoing connections or other objects.
    """
    def __init__(self):

        # Update lock
        self.lock = RLock()

        # The main log - keys are object types, values are dicts mapping object IDs to LogContainer objects
        self._log = {
            CHANNEL.HTTP_SOAP: {},
            CHANNEL.WEB_SOCKET: {},
            GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP: {},
            WEB_SOCKET.AUDIT_KEY: {},
        }

        # Python logging
        self.logger = getLogger('zato')

# ################################################################################################################################

    def get_container(self, type_, object_id):
        # type: (str, str) -> LogContainer

        # Note that below we ignore any key errors, effectively silently dropping invalid requests.
        return self._log.get(type_, {}).get(object_id)

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

    def _delete_container(self, type_, object_id):
        # type: (str, str)

        # Make sure the object ID is a string (it can be an int)
        object_id = str(object_id)

        # Get the mapping of object types to object IDs ..
        try:
            container_dict = self._log[type_] # type: dict
        except KeyError:
            raise ValueError('Container type not found `{}` among `{}` ({})'.format(type_, sorted(self._log), object_id))

        # No KeyError = we recognised that type ..

        # .. so we can now try to delete that container by its object's ID.
        # Note that we use .pop on purpose - e.g. when a server has just started,
        # it may not have any such an object yet but the user may already try to edit
        # the object this log is attached to. Using .pop ignores non-existing keys.
        container_dict.pop(object_id, None)

# ################################################################################################################################

    def delete_container(self, type_, object_id):
        # type: (str, str)
        with self.lock:
            self._delete_container(type_, object_id)

# ################################################################################################################################

    def edit_container(self, config):
        # type: (LogContainerConfig)
        with self.lock:
            self._delete_container(config.type_, config.object_id)
            self._create_container(config)

# ################################################################################################################################

    def store_data(self, data_event):
        # type: (DataEvent) -> None

        # We always store IDs as string objects
        data_event.object_id = str(data_event.object_id)

        # At this point we assume that all the dicts and containers already exist
        container_dict = self._log[data_event.type_]
        container = container_dict[data_event.object_id] # type: LogContainer
        container.store(data_event)

# ################################################################################################################################

    def store_data_received(self, data_event):
        # type: (DataReceived) -> None
        self.store_data(data_event)

# ################################################################################################################################

    def store_data_sent(self, data_event):
        # type: (DataSent) -> None
        self.store_data(data_event)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    pass
