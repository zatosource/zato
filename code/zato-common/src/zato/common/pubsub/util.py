# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timezone
from logging import getLogger

# Zato
from zato.common.api import PubSub
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)
_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Max_Length = PubSub.Topic.Name_Max_Len

# ################################################################################################################################
# ################################################################################################################################

def validate_topic_name(topic_name:'str') -> 'None':
    """ Validate topic name according to pub/sub rules.

    Raises ValueError if validation fails.
    """
    if not topic_name:
        raise ValueError('Topic name cannot be empty')

    if len(topic_name) > ModuleCtx.Max_Length:
        raise ValueError(f'Topic name exceeds maximum length of {ModuleCtx.Max_Length} characters: {len(topic_name)}')

    if '#' in topic_name:
        raise ValueError('Topic name cannot contain "#" character')

    if not _is_ascii_only(topic_name):
        raise ValueError(f'Topic name contains non-ASCII characters: {topic_name}')

# ################################################################################################################################

def validate_pattern(pattern:'str') -> 'None':
    """ Validate pattern according to pub/sub rules.

    Raises ValueError if validation fails.
    """
    if not pattern:
        raise ValueError('Pattern cannot be empty')

    if len(pattern) > ModuleCtx.Max_Length:
        raise ValueError(f'Pattern exceeds maximum length of {ModuleCtx.Max_Length} characters: {len(pattern)}')

    if _contains_reserved_name(pattern):
        raise ValueError(f'Pattern contains reserved name: {pattern}')

    if not _is_ascii_only(pattern):
        raise ValueError(f'Pattern contains non-ASCII characters: {pattern}')

# ################################################################################################################################

def _contains_reserved_name(pattern:'str') -> 'bool':
    """ Check if pattern contains reserved names case-insensitively.
    """
    pattern_lower = pattern.lower()
    return 'zato' in pattern_lower or 'zpsk' in pattern_lower

# ################################################################################################################################

def _is_ascii_only(text:'str') -> 'bool':
    """ Check if text contains only ASCII characters.
    """
    try:
        _ = text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False

# ################################################################################################################################

def get_permissions_for_sec_base(session, sec_base_id:'int', cluster_id:'int') -> 'list':
    """ Get all active permissions for a security definition.
    Returns a list of permission dictionaries with pattern and access_type.
    """
    from zato.common.odb.model import PubSubPermission

    permissions = session.query(PubSubPermission).filter(
        PubSubPermission.sec_base_id == sec_base_id,
        PubSubPermission.cluster_id == cluster_id,
        PubSubPermission.is_active == True
    ).all()

    result = []
    sub_prefix = 'sub='
    pub_prefix = 'pub='

    for perm in permissions:

        # Split patterns on newlines since service layer joins them
        patterns = [elem.strip() for elem in perm.pattern.splitlines() if elem.strip()]

        for individual_pattern in patterns:
            for prefix in [sub_prefix, pub_prefix]:
                if individual_pattern.startswith(prefix):
                    clean_pattern = individual_pattern[len(prefix):]
                    result.append({
                        'pattern': clean_pattern,
                        'access_type': perm.access_type
                    })
                    break

    return result

# ################################################################################################################################

def evaluate_pattern_match(session, sec_base_name:'str', sec_base_id:'int', cluster_id:'int', topic_name:'str') -> 'str':
    """ Evaluate which pattern matches the given topic name for a security definition.
    Returns the matched pattern or raises an exception if no pattern matches.
    """
    # Zato
    from zato.common.pubsub.matcher import PatternMatcher

    permissions = get_permissions_for_sec_base(session, sec_base_id, cluster_id)

    if not permissions:
        msg = f'No permissions defined for security definition {sec_base_id} ({sec_base_name})'
        raise ValueError(msg)

    # Create temporary matcher
    matcher = PatternMatcher()

    # Add client to matcher
    client_id = f'eval.{sec_base_id}.{topic_name}'
    matcher.add_client(client_id, permissions)

    # Evaluate for subscribe operation (subscriptions are for subscribers)
    result = matcher.evaluate(client_id, topic_name, 'subscribe')

    if result.is_ok and result.matched_pattern:
        return result.matched_pattern
    else:
        msg = f'Topic "{topic_name}" does not match any subscription patterns for security definition {sec_base_id} ({sec_base_name})'
        raise ValueError(msg)

# ################################################################################################################################

def get_security_definition(session, cluster_id, username=None, sec_name=None):
    """ Get security definition by username or sec_name.

    Returns tuple of (sec_def, lookup_field, lookup_value).
    Raises Exception if not found or if neither username nor sec_name provided.
    """
    # Zato
    from zato.common.odb.model import SecurityBase

    if username:
        sec_def = session.query(SecurityBase).\
            filter(SecurityBase.cluster_id==cluster_id).\
            filter(SecurityBase.username==username).\
            first()
        lookup_field = 'username'
        lookup_value = username
    elif sec_name:
        sec_def = session.query(SecurityBase).\
            filter(SecurityBase.cluster_id==cluster_id).\
            filter(SecurityBase.name==sec_name).\
            first()
        lookup_field = 'sec_name'
        lookup_value = sec_name
    else:
        raise Exception('Either username or sec_name must be provided')

    if not sec_def:
        raise Exception(f'Security definition not found for {lookup_field} `{lookup_value}`')

    return sec_def, lookup_field, lookup_value

# ################################################################################################################################

def set_time_since(message:'dict', pub_time_iso:'str', recv_time_iso:'str', current_time:'datetime') -> 'None':
    """ Calculate and set time_since_pub and time_since_recv on the message.
    """
    pub_timestamp = datetime.fromisoformat(pub_time_iso)
    if pub_timestamp.tzinfo is None:
        pub_timestamp = pub_timestamp.replace(tzinfo=timezone.utc)
    time_since_pub = str(current_time - pub_timestamp)

    recv_timestamp = datetime.fromisoformat(recv_time_iso)
    if recv_timestamp.tzinfo is None:
        recv_timestamp = recv_timestamp.replace(tzinfo=timezone.utc)
    time_since_recv = str(current_time - recv_timestamp)

    message['time_since_pub'] = time_since_pub
    message['time_since_recv'] = time_since_recv

# ################################################################################################################################
# ################################################################################################################################
