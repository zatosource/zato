# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from dataclasses import dataclass
from datetime import timedelta
from logging import getLogger
from zlib import crc32

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, is_audit_log_enabled
from zato.common.marshal_.api import Model
from zato.common.pubsub.sql.config import get_dedup_window_days
from zato.common.pubsub.sql.pending import new_pending_publication
from zato.common.typing_ import cast_, list_
from zato.common.util.api import new_msg_id
from zato.common.util.time_ import datetime_to_ms, parse_utc
from zato.server.metrics import zato_pubsub_messages_published_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.pubsub.sql.pending import PendingPublication
    from zato.common.typing_ import any_, anydict, intnone, strnone

    AuditLog = AuditLog
    PendingPublication = PendingPublication
    SQLPubSubBackend = SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

_default_priority   = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration
_data_preview_len   = PubSub.Message.Data_Preview_Len

# How many milliseconds one day has - the dedup window is given in days.
_ms_per_day = 24 * 60 * 60 * 1000

built_publication_list = list_['BuiltPublication']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BuiltPublication:
    """ A publication that is ready to be written, with the serialized data that its audit event records.
    """
    pending: 'PendingPublication'
    serialized_data: 'str'

# ################################################################################################################################
# ################################################################################################################################

def build_publication(
    backend:'SQLPubSubBackend',
    topic_name:'str',
    data:'any_',
    *,
    priority:'int'=_default_priority,
    expiration:'int'=_default_expiration,
    correl_id:'strnone'=None,
    in_reply_to:'strnone'=None,
    ext_client_id:'strnone'=None,
    publisher:'strnone'=None,
    pub_time:'strnone'=None,
    cid:'strnone'=None,
    msg_id:'strnone'=None,
    max_retries:'intnone'=None,
    retry_sleep_time:'intnone'=None,
    retry_backoff_threshold:'intnone'=None,
    retry_backoff_multiplier:'intnone'=None,
) -> 'BuiltPublication':
    """ Builds the message row of one publication. A caller that needs to know the message's id before the message is
    stored, e.g. because the id travels inside the message itself, gives its own, otherwise one is generated.
    """

    # Normalize topic name to lowercase for case-insensitivity ..
    topic_name = topic_name.lower()

    # .. the message ID is the caller's own or a new one ..
    if msg_id:
        message_id = msg_id
    else:
        message_id = new_msg_id()

    # .. build timestamps on the time of the database ..
    clock = backend.clock
    now = clock.now()
    now_iso = now.isoformat()

    now_ms_float = datetime_to_ms(now)
    received_ms = int(now_ms_float)

    if pub_time:
        pub_time_iso = pub_time
        pub_time_ms = backend._iso_to_ms(pub_time)
    else:
        pub_time_iso = now_iso
        pub_time_ms = received_ms

    expiration_delta = timedelta(seconds=expiration)
    expiration_time = now + expiration_delta
    expiration_time_iso = expiration_time.isoformat()
    expiration_ms_float = datetime_to_ms(expiration_time)
    expiration_ms = int(expiration_ms_float)

    # .. serialize data ..
    data_class = ''

    if isinstance(data, str):
        serialized_data = data

    elif isinstance(data, Model):
        data_module = data.__class__.__module__
        data_class_name = data.__class__.__qualname__
        data_class = f'{data_module}.{data_class_name}'
        serialized_data = data.to_json().decode()

    else:
        serialized_data = json.dumps(data)

    data_size = len(serialized_data)
    data_preview = serialized_data[:_data_preview_len]

    # .. a publication repeated under the same identifier is recognized by its checksum ..
    serialized_bytes = serialized_data.encode('utf8')
    payload_crc32 = crc32(serialized_bytes)

    # .. encrypt the payload at rest when configured to ..
    if backend.encrypt_at_rest:
        payload = backend._encrypt_payload(serialized_data)
        payload_encrypted = True
    else:
        payload = serialized_data
        payload_encrypted = False

    # .. and build the message row, with optional values stored as NULLs.
    message_values:'anydict' = {
        'msg_id': message_id,
        'topic_name': topic_name,
        'payload': payload,
        'payload_encrypted': payload_encrypted,
        'payload_crc32': payload_crc32,
        'data_class': data_class if data_class else None,
        'data_size': data_size,
        'data_preview': data_preview if data_preview else None,
        'priority': priority,
        'expiration': expiration,
        'pub_time_iso': pub_time_iso,
        'recv_time_iso': now_iso,
        'expiration_time_iso': expiration_time_iso,
        'pub_time_ms': pub_time_ms,
        'expiration_ms': expiration_ms,
        'publisher': publisher,
        'cid': cid,
        'correl_id': correl_id,
        'in_reply_to': in_reply_to,
        'ext_client_id': ext_client_id,
        _retry.Field_Max_Retries: max_retries,
        _retry.Field_Sleep_Time: retry_sleep_time,
        _retry.Field_Backoff_Threshold: retry_backoff_threshold,
        _retry.Field_Backoff_Multiplier: retry_backoff_multiplier,
    }

    # .. the message ID is recognized as a repeat for the window that counts from the time of the database.
    dedup_window_days = get_dedup_window_days()
    dedup_window_ms = dedup_window_days * _ms_per_day

    out = BuiltPublication()
    out.pending = new_pending_publication(message_values, received_ms, dedup_window_ms)
    out.serialized_data = serialized_data

    return out

# ################################################################################################################################

def _announce_publication(backend:'SQLPubSubBackend', built:'BuiltPublication') -> 'None':
    """ Wakes up the subscribers of a committed publication and updates the publish counter.
    """
    message_values = built.pending.message_values
    subscriber_keys = built.pending.subscriber_keys

    message_id = message_values['msg_id']
    topic_name = message_values['topic_name']

    # Wake up the subscribers now that the transaction is committed ..
    if subscriber_keys:
        backend.notify_sub_keys(subscriber_keys)

    subscriber_count = len(subscriber_keys)

    logger.info('Published message -> msg_id:%s, topic_name:%s, subscriber_count:%d',
        message_id, topic_name, subscriber_count)

    # .. and update the publish counter.
    counter = zato_pubsub_messages_published_total.labels(topic_name=topic_name)
    _ = counter.inc()

# ################################################################################################################################

def _is_audited(backend:'SQLPubSubBackend', built:'BuiltPublication') -> 'bool':
    """ Whether the audit log records a publication, which it does unless it is not in use or is off for its topic.
    """
    topic_name = built.pending.message_values['topic_name']

    if is_audit_log_enabled():
        out = topic_name not in backend.audit_disabled_topics
    else:
        out = False

    return out

# ################################################################################################################################

def _get_published_event_fields(backend:'SQLPubSubBackend', built:'BuiltPublication') -> 'anydict':
    """ Returns the fields of the audit event of a publication.
    """
    message_values = built.pending.message_values
    topic_name = message_values['topic_name']

    # These are all optional on input so they are normalized to strings here.
    cid = message_values['cid']
    correl_id = message_values['correl_id']
    ext_client_id = message_values['ext_client_id']
    publisher = message_values['publisher']

    if cid is None:
        cid = ''
    if correl_id is None:
        correl_id = ''
    if ext_client_id is None:
        ext_client_id = ''
    if publisher is None:
        publisher = ''

    audit_pub_time = parse_utc(message_values['pub_time_iso'])
    is_export_payload_active = backend.is_topic_payload_exported(topic_name)

    out:'anydict' = {
        'cid': cid,
        'msg_id': message_values['msg_id'],
        'correl_id': correl_id,
        'ext_client_id': ext_client_id,
        'pub_time': audit_pub_time,
        'endpoint': publisher,
        'size': message_values['data_size'],
        'priority': message_values['priority'],
        'outcome': AuditOutcome.OK,
        'data': built.serialized_data,
        'is_export_payload_active': is_export_payload_active,
    }

    return out

# ################################################################################################################################

def add_published_event(backend:'SQLPubSubBackend', built:'BuiltPublication') -> 'None':
    """ Adds to a publication the audit event that records it, which commits with its message,
    unless the audit log of its topic is off.
    """
    if _is_audited(backend, built):
        audit_log = cast_('AuditLog', backend.audit_log)
        topic_name = built.pending.message_values['topic_name']
        fields = _get_published_event_fields(backend, built)

        audit_event = audit_log.new_pending_event(AuditSource.PubSub, AuditEvent.Published, topic_name, **fields)
        built.pending.audit_events.append(audit_event)

# ################################################################################################################################

def complete_publication(backend:'SQLPubSubBackend', built:'BuiltPublication') -> 'None':
    """ Runs what follows the commit of a publication - wakes up its subscribers and updates the publish counter.
    """
    _announce_publication(backend, built)

# ################################################################################################################################

def complete_publications(backend:'SQLPubSubBackend', built_list:'built_publication_list') -> 'None':
    """ Runs what follows the commit of publications that one transaction committed together,
    as complete_publication does for each of them.
    """
    for built in built_list:
        _announce_publication(backend, built)

# ################################################################################################################################
# ################################################################################################################################
