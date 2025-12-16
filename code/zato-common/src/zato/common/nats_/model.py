# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass, field

# Zato
from zato.common.typing_ import any_, anydict, anydictnone, anylist, boolnone, intnone, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ServerInfo:
    """ Information received from NATS server in the INFO message.
    """
    server_id: str = ''
    server_name: str = ''
    version: str = ''
    proto: int = 0
    go: str = ''
    host: str = ''
    port: int = 0
    headers: bool = False
    max_payload: int = 1048576
    jetstream: bool = False
    auth_required: bool = False
    tls_required: bool = False
    tls_verify: bool = False
    tls_available: bool = False
    connect_urls: 'anylist' = field(default_factory=list)
    ws_connect_urls: 'anylist' = field(default_factory=list)
    ldm: bool = False
    client_id: 'intnone' = None
    client_ip: 'strnone' = None
    nonce: 'strnone' = None
    cluster: 'strnone' = None
    domain: 'strnone' = None
    xkey: 'strnone' = None
    git_commit: 'strnone' = None

    @staticmethod
    def from_dict(data:'anydict') -> 'ServerInfo':
        info = ServerInfo()
        for key, value in data.items():
            if hasattr(info, key):
                setattr(info, key, value)
        return info

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConnectOptions:
    """ Options sent to NATS server in the CONNECT message.
    """
    verbose: bool = False
    pedantic: bool = False
    tls_required: bool = False
    name: 'strnone' = None
    lang: str = 'python3'
    version: str = '1.0.0'
    protocol: int = 1
    echo: bool = True
    no_responders: bool = True
    headers: bool = True
    auth_token: 'strnone' = None
    user: 'strnone' = None
    password: 'strnone' = None
    nkey: 'strnone' = None
    sig: 'strnone' = None
    jwt: 'strnone' = None

    def to_dict(self) -> 'anydict':
        result = {
            'verbose': self.verbose,
            'pedantic': self.pedantic,
            'tls_required': self.tls_required,
            'lang': self.lang,
            'version': self.version,
            'protocol': self.protocol,
            'echo': self.echo,
            'no_responders': self.no_responders,
            'headers': self.headers,
        }
        if self.name:
            result['name'] = self.name
        if self.auth_token:
            result['auth_token'] = self.auth_token
        if self.user:
            result['user'] = self.user
        if self.password:
            result['pass'] = self.password
        if self.nkey:
            result['nkey'] = self.nkey
        if self.sig:
            result['sig'] = self.sig
        if self.jwt:
            result['jwt'] = self.jwt
        return result

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Msg:
    """ A message received from NATS.
    """
    subject: str = ''
    reply: str = ''
    data: bytes = b''
    headers: 'anydictnone' = None
    sid: int = 0

    @property
    def header(self) -> 'anydictnone':
        return self.headers

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubAck:
    """ Acknowledgment received after publishing to JetStream.
    """
    stream: str = ''
    seq: int = 0
    domain: 'strnone' = None
    duplicate: 'boolnone' = None

    @staticmethod
    def from_dict(data:'anydict') -> 'PubAck':
        return PubAck(
            stream=data['stream'],
            seq=data['seq'],
            domain=data.get('domain'),
            duplicate=data.get('duplicate'),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class StreamConfig:
    """ Configuration for a JetStream stream.
    """
    name: 'strnone' = None
    description: 'strnone' = None
    subjects: 'anylist' = field(default_factory=list)
    retention: str = 'limits'
    max_consumers: int = -1
    max_msgs: int = -1
    max_bytes: int = -1
    max_age: int = 0
    max_msg_size: int = -1
    storage: str = 'file'
    num_replicas: int = 1
    duplicate_window: int = 120000000000
    discard: str = 'old'
    deny_delete: bool = False
    deny_purge: bool = False

    def to_dict(self) -> 'anydict':
        result = {}
        if self.name:
            result['name'] = self.name
        if self.description:
            result['description'] = self.description
        if self.subjects:
            result['subjects'] = self.subjects
        result['retention'] = self.retention
        result['max_consumers'] = self.max_consumers
        result['max_msgs'] = self.max_msgs
        result['max_bytes'] = self.max_bytes
        result['max_age'] = self.max_age
        result['max_msg_size'] = self.max_msg_size
        result['storage'] = self.storage
        result['num_replicas'] = self.num_replicas
        result['duplicate_window'] = self.duplicate_window
        result['discard'] = self.discard
        result['deny_delete'] = self.deny_delete
        result['deny_purge'] = self.deny_purge
        return result

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class StreamState:
    """ State of a JetStream stream.
    """
    messages: int = 0
    bytes: int = 0
    first_seq: int = 0
    last_seq: int = 0
    consumer_count: int = 0

    @staticmethod
    def from_dict(data:'anydict') -> 'StreamState':
        return StreamState(
            messages=data['messages'],
            bytes=data['bytes'],
            first_seq=data['first_seq'],
            last_seq=data['last_seq'],
            consumer_count=data['consumer_count'],
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class StreamInfo:
    """ Information about a JetStream stream.
    """
    config: 'StreamConfig | None' = None
    state: 'StreamState | None' = None

    @staticmethod
    def from_dict(data:'anydict') -> 'StreamInfo':
        config = None
        state = None
        if 'config' in data:
            config = StreamConfig()
            for key, value in data['config'].items():
                if hasattr(config, key):
                    setattr(config, key, value)
        if 'state' in data:
            state = StreamState.from_dict(data['state'])
        return StreamInfo(config=config, state=state)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConsumerConfig:
    """ Configuration for a JetStream consumer.
    """
    name: 'strnone' = None
    durable_name: 'strnone' = None
    description: 'strnone' = None
    deliver_policy: str = 'all'
    opt_start_seq: 'intnone' = None
    ack_policy: str = 'explicit'
    ack_wait: int = 30000000000  # 30 seconds in nanoseconds
    max_deliver: int = -1
    filter_subject: 'strnone' = None
    replay_policy: str = 'instant'
    max_waiting: int = 512
    max_ack_pending: int = 1000
    deliver_subject: 'strnone' = None
    deliver_group: 'strnone' = None
    inactive_threshold: int = 0

    def to_dict(self) -> 'anydict':
        result = {}
        if self.name:
            result['name'] = self.name
        if self.durable_name:
            result['durable_name'] = self.durable_name
        if self.description:
            result['description'] = self.description
        result['deliver_policy'] = self.deliver_policy
        if self.opt_start_seq is not None:
            result['opt_start_seq'] = self.opt_start_seq
        result['ack_policy'] = self.ack_policy
        result['ack_wait'] = self.ack_wait
        result['max_deliver'] = self.max_deliver
        if self.filter_subject:
            result['filter_subject'] = self.filter_subject
        result['replay_policy'] = self.replay_policy
        result['max_waiting'] = self.max_waiting
        result['max_ack_pending'] = self.max_ack_pending
        if self.deliver_subject:
            result['deliver_subject'] = self.deliver_subject
        if self.deliver_group:
            result['deliver_group'] = self.deliver_group
        if self.inactive_threshold:
            result['inactive_threshold'] = self.inactive_threshold
        return result

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConsumerInfo:
    """ Information about a JetStream consumer.
    """
    name: str = ''
    stream_name: str = ''
    config: 'ConsumerConfig | None' = None
    num_ack_pending: int = 0
    num_redelivered: int = 0
    num_waiting: int = 0
    num_pending: int = 0

    @staticmethod
    def from_dict(data:'anydict') -> 'ConsumerInfo':
        config = None
        if 'config' in data:
            config = ConsumerConfig()
            for key, value in data['config'].items():
                if hasattr(config, key):
                    setattr(config, key, value)
        return ConsumerInfo(
            name=data['name'],
            stream_name=data['stream_name'],
            config=config,
            num_ack_pending=data['num_ack_pending'],
            num_redelivered=data['num_redelivered'],
            num_waiting=data['num_waiting'],
            num_pending=data['num_pending'],
        )

# ################################################################################################################################
# ################################################################################################################################
