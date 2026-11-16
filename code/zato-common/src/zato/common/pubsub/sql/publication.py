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
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.marshal_.api import Model
from zato.common.pubsub.sql.writes import new_pending_publication
from zato.common.typing_ import list_
from zato.common.util.api import new_msg_id
from zato.common.util.time_ import datetime_to_ms, parse_utc
from zato.server.metrics import zato_pubsub_messages_published_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.pubsub.sql.writes import PendingPublication
    from zato.common.typing_ import any_, anydict, intnone, strnone

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

    if pub_time:
        pub_time_iso = pub_time
        pub_time_ms = backend._iso_to_ms(pub_time)
    else:
        pub_time_iso = now_iso
        now_ms_float = datetime_to_ms(now)
        pub_time_ms = int(now_ms_float)

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

    out = BuiltPublication()
    out.pending = new_pending_publication(message_values)
    out.serialized_data = serialized_data

    return out

# ################################################################################################################################

def complete_publication(backend:'SQLPubSubBackend', built:'BuiltPublication') -> 'None':
    """ Runs what follows the commit of a publication - wakes up its subscribers, records the publication
    in the audit log, unless the audit log of its topic is off, and updates the publish counter.
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

    # .. record the publish in the audit log, unless the topic's audit log is off ..
    if backend.audit_log:
        if topic_name not in backend.audit_disabled_topics:

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

            backend.audit_log.insert(AuditSource.PubSub, AuditEvent.Published, topic_name,
                cid=cid,
                msg_id=message_id,
                correl_id=correl_id,
                ext_client_id=ext_client_id,
                pub_time=audit_pub_time,
                endpoint=publisher,
                size=message_values['data_size'],
                priority=message_values['priority'],
                outcome=AuditOutcome.OK,
                data=built.serialized_data,
                is_export_payload_active=backend.is_topic_payload_exported(topic_name),
            )

    # .. and update the publish counter.
    counter = zato_pubsub_messages_published_total.labels(topic_name=topic_name)
    _ = counter.inc()

# ################################################################################################################################
# ################################################################################################################################
