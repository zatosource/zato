# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQ of an outgoing connection.

# stdlib
from json import dumps
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.pubsub.outgoing import get_outgoing_topic_name, is_dlq_active, Key_CID, Key_Conn_ID, Key_Conn_Name, \
    Key_Conn_Type, Key_DLQ_Rounds, Key_Msg_ID, Key_Pub_Time, locate_outgoing_conn
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.api import new_msg_id
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.outgoing import DeliveryExhausted
    from zato.common.typing_ import anytuple, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_topic_prefix   = PubSub.Outgoing.DLQ_Topic_Prefix
_sub_key_prefix = PubSub.Outgoing.DLQ_Sub_Key_Prefix

# The section a message gains when it moves to the DLQ and its keys
Key_DLQ = 'dlq'

Header_Reason        = 'reason'
Header_Error         = 'error'
Header_Attempts      = 'attempts'
Header_Moved_Time    = 'moved_time_iso'
Header_Source_Topic  = 'source_topic'
Header_Source_Msg_ID = 'source_msg_id'
Header_Pub_Time      = 'pub_time_iso'
Header_Rounds        = 'rounds'

# ################################################################################################################################
# ################################################################################################################################

def get_dlq_topic_name(conn_type:'str', conn_name:'str') -> 'str':
    """ The name of the topic that is one outgoing connection's DLQ.
    """
    out = f'{_topic_prefix}{conn_type}.{conn_name}'
    out = out.lower()

    validate_topic_name(out)

    return out

# ################################################################################################################################

def get_dlq_sub_key(conn_type:'str', conn_id:'int') -> 'str':
    """ The sub key of one outgoing connection's DLQ.
    """
    out = f'{_sub_key_prefix}{conn_type}.{conn_id}'
    return out

# ################################################################################################################################

def is_dlq_sub_key(sub_key:'str') -> 'bool':
    """ Whether a sub key is that of a DLQ.
    """
    out = sub_key.startswith(_sub_key_prefix)
    return out

# ################################################################################################################################

def parse_dlq_sub_key(sub_key:'str') -> 'anytuple':
    """ Turns a DLQ sub key back into the connection type and connection id it was built from.
    """
    remainder = sub_key[len(_sub_key_prefix):]
    conn_type, _, conn_id = remainder.rpartition('.')

    out = (conn_type, int(conn_id))
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_dlq_header(envelope:'stranydict', source_topic:'str', exhausted:'DeliveryExhausted') -> 'stranydict':
    """ The DLQ header of one message.
    """
    out = {
        Header_Reason: PubSub.Outgoing.DLQ_Reason_Retries_Exhausted,
        Header_Error: exhausted.error,
        Header_Attempts: exhausted.attempts,
        Header_Moved_Time: utcnow().isoformat(),
        Header_Source_Topic: source_topic,
        Header_Source_Msg_ID: envelope[Key_Msg_ID],
        Header_Pub_Time: envelope[Key_Pub_Time],
        Header_Rounds: envelope[Key_DLQ_Rounds],
    }

    return out

# ################################################################################################################################

def strip_dlq_header(document:'stranydict') -> 'stranydict':
    """ The document without its DLQ header.
    """
    out = dict(document)
    del out[Key_DLQ]

    return out

# ################################################################################################################################
# ################################################################################################################################

def move_to_dlq(server:'ParallelServer', cid:'str', envelope:'stranydict', exhausted:'DeliveryExhausted') -> 'bool':
    """ Moves one message to its connection's DLQ if the connection's DLQ switch is on, returning whether it did.
    """
    conn_type = envelope[Key_Conn_Type]
    conn_id = envelope[Key_Conn_ID]
    conn_name = envelope[Key_Conn_Name]

    # The message travels under the correlation id of the service that sent it
    if envelope[Key_CID]:
        cid = envelope[Key_CID]

    _, wrapper = locate_outgoing_conn(server, conn_type, conn_id, conn_name)

    if not is_dlq_active(conn_type, wrapper):
        return False

    config_manager = server.config_manager
    dlq_topic_name, current_name = config_manager.ensure_outgoing_dlq(conn_type, conn_id)

    source_topic = get_outgoing_topic_name(conn_type, current_name)

    document = dict(envelope)
    document[Key_DLQ] = build_dlq_header(envelope, source_topic, exhausted)

    data = dumps(document)
    msg_id = new_msg_id()

    # The DLQ is always in the pub/sub database, so this goes to the backend and not through the facade
    try:
        _ = server.pubsub_backend.publish(
            dlq_topic_name,
            data,
            cid=cid,
            correl_id=cid,
            publisher=PubSub.Outgoing.Delivery_Service,
            msg_id=msg_id,
        )
    except Exception:
        logger.warning('Could not move message `%s` of `%s` to DLQ `%s`, cid `%s`, e:`%s`',
            envelope[Key_Msg_ID], conn_name, dlq_topic_name, cid, format_exc())
        return False

    _insert_dlq_audit_event(server, cid, envelope, dlq_topic_name, msg_id, data, exhausted)

    logger.info('Moved message `%s` of `%s` to DLQ `%s` as `%s` after %d attempts, cid `%s`, reason `%s`',
        envelope[Key_Msg_ID], conn_name, dlq_topic_name, msg_id, exhausted.attempts, cid, exhausted.error)

    return True

# ################################################################################################################################

def _insert_dlq_audit_event(
    server:'ParallelServer',
    cid:'str',
    envelope:'stranydict',
    dlq_topic_name:'str',
    dlq_msg_id:'str',
    data:'str',
    exhausted:'DeliveryExhausted',
    ) -> 'None':
    """ Records the move of one message to the DLQ in the audit log.
    """
    audit_log = server.pubsub_backend.audit_log

    # The backend has no audit log in unit tests only
    if not audit_log:
        return

    _ = audit_log.insert(AuditSource.PubSub, AuditEvent.DLQ, dlq_topic_name,
        cid=cid,
        msg_id=dlq_msg_id,
        correl_id=cid,
        pub_time_iso=envelope[Key_Pub_Time],
        endpoint=envelope[Key_Conn_Name],
        sub_key=get_dlq_sub_key(envelope[Key_Conn_Type], envelope[Key_Conn_ID]),
        size=len(data),
        outcome=AuditOutcome.Error,
        status=exhausted.error,
        data=data,
    )

# ################################################################################################################################
# ################################################################################################################################
