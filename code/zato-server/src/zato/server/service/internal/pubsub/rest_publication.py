# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from dataclasses import dataclass
from http.client import BAD_REQUEST, FORBIDDEN, UNAUTHORIZED

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.util import validate_topic_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anytuple
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# A message ID that a client supplies, whose length is bounded by the column that stores it
Msg_ID_Pattern = re.compile(r'^[A-Za-z0-9._:-]{1,200}$')

_min_priority = PubSub.Message.Priority_Min
_max_priority = PubSub.Message.Priority_Max
_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

_status_bad_request = PubSub.Status.Bad_Request
_status_unauthorized = PubSub.Status.Unauthorized
_status_forbidden = PubSub.Status.Forbidden

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RESTPublication:
    """ One publication that a REST client requested, with its optional fields resolved.
    """
    topic_name: 'str'
    data: 'any_'
    priority: 'int'
    expiration: 'int'
    correl_id: 'str'
    in_reply_to: 'str'
    ext_client_id: 'str'
    pub_time: 'str'

    # The message ID that the client supplied, or an empty string if a new one is generated
    msg_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

def is_valid_msg_id(value:'any_') -> 'bool':
    """ Whether a value is a message ID that a client may supply.
    """
    if not isinstance(value, str):
        return False

    match = Msg_ID_Pattern.match(value)

    out = match is not None
    return out

# ################################################################################################################################

def _get_optional(fields:'anydict', name:'str') -> 'any_':
    """ Returns the value of an optional field, or None for a field that the client did not send,
    which the input of a service represents as an empty string.
    """
    if name not in fields:
        return None

    out = fields[name]

    if out == '':
        return None

    return out

# ################################################################################################################################

def _parse_int(value:'any_', default:'int') -> 'int':
    """ Returns an optional integer field, or the default for one that is absent or not an integer.
    """
    if value is None:
        return default

    try:
        out = int(value)
    except (ValueError, TypeError):
        out = default

    return out

# ################################################################################################################################

def _get_text(fields:'anydict', name:'str', default:'str') -> 'str':
    """ Returns an optional text field, or the default for one that is absent.
    """
    out = _get_optional(fields, name)

    if out is None:
        out = default

    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_publication(
    server:'ParallelServer',
    username:'str',
    cid:'str',
    fields:'anydict',
) -> 'tuple[RESTPublication | None, anytuple | None]':
    """ Validates one publication of a REST client and checks that the client may publish to its topic,
    which is active. Returns the publication, or the details, status and status code of the error.
    """

    # The topic is what everything else is checked against ..
    topic_name = _get_optional(fields, 'topic_name')

    if topic_name is None:
        return None, ("Invalid input: 'topic_name' element missing", _status_bad_request, BAD_REQUEST)

    try:
        validate_topic_name(topic_name)
    except Exception as e:
        return None, (str(e), _status_bad_request, BAD_REQUEST)

    # .. the client needs the permission to publish to it ..
    matcher = server.pubsub_pattern_matcher
    permission_result = matcher.evaluate(username, topic_name, 'publish')

    if not permission_result.is_ok:
        return None, ('Permission denied', _status_unauthorized, UNAUTHORIZED)

    # .. and the topic needs to be active ..
    if not server.config_manager.is_pubsub_topic_active(topic_name):
        return None, (f'Topic {topic_name} is inactive', _status_forbidden, FORBIDDEN)

    # .. a message without data is not one ..
    data = _get_optional(fields, 'data')

    if data is None:
        return None, ("Invalid input: 'data' element missing", _status_bad_request, BAD_REQUEST)

    # .. a message ID of the client's own follows the rules of every message ID ..
    msg_id = _get_optional(fields, 'msg_id')

    if msg_id is None:
        msg_id = ''

    elif not is_valid_msg_id(msg_id):
        return None, (f'Invalid msg_id, it must match {Msg_ID_Pattern.pattern}', _status_bad_request, BAD_REQUEST)

    # .. a priority out of range and an expiration below one second are replaced ..
    priority = _parse_int(_get_optional(fields, 'priority'), _default_priority)
    expiration = _parse_int(_get_optional(fields, 'expiration'), _default_expiration)

    if priority < _min_priority or priority > _max_priority:
        priority = _default_priority

    if expiration < 1:
        expiration = 1

    # .. and the correlation ID of a message is the CID of its request unless the client gave its own.
    out = RESTPublication()
    out.topic_name = topic_name
    out.data = data
    out.priority = priority
    out.expiration = expiration
    out.correl_id = _get_text(fields, 'correl_id', cid)
    out.in_reply_to = _get_text(fields, 'in_reply_to', '')
    out.ext_client_id = _get_text(fields, 'ext_client_id', '')
    out.pub_time = _get_text(fields, 'pub_time', '')
    out.msg_id = msg_id

    return out, None

# ################################################################################################################################
# ################################################################################################################################
