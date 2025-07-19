# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.pubsub.common import BrokerConfig

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Max_Length = 200

# ################################################################################################################################
# ################################################################################################################################

def get_broker_config() -> 'BrokerConfig':

    config = BrokerConfig()

    config.protocol = os.environ['Zato_Broker_Protocol']
    config.address = os.environ['Zato_Broker_Address']
    config.vhost = os.environ['Zato_Broker_Virtual_Host']
    config.username = os.environ['Zato_Broker_Username']
    config.password = os.environ['Zato_Broker_Password']

    return config

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
    import logging
    logger = logging.getLogger(__name__)

    from zato.common.odb.model import PubSubPermission

    logger.info('DEBUG get_permissions_for_sec_base - querying for sec_base_id=%s, cluster_id=%s', sec_base_id, cluster_id)

    permissions = session.query(PubSubPermission).filter(
        PubSubPermission.sec_base_id == sec_base_id,
        PubSubPermission.cluster_id == cluster_id,
        PubSubPermission.is_active == True
    ).all()

    logger.info('DEBUG get_permissions_for_sec_base - found %d permissions', len(permissions))
    for perm in permissions:
        logger.info('DEBUG get_permissions_for_sec_base - permission: id=%s, pattern=%s, access_type=%s, is_active=%s',
                   perm.id, perm.pattern, perm.access_type, perm.is_active)

    result = []
    for perm in permissions:
        # Only include subscription patterns (sub= prefix) for subscription evaluation
        if perm.pattern.startswith('sub='):
            # Strip the sub= prefix to get the actual pattern
            pattern = perm.pattern.replace('sub=', '')
            result.append({
                'pattern': pattern,
                'access_type': perm.access_type
            })
        # For patterns without prefix, assume they are subscription patterns
        elif not perm.pattern.startswith('pub='):
            result.append({
                'pattern': perm.pattern,
                'access_type': perm.access_type
            })

    logger.info('DEBUG get_permissions_for_sec_base - returning subscription permissions: %s', result)
    return result

# ################################################################################################################################

def evaluate_pattern_match(session, sec_base_id:'int', cluster_id:'int', topic_name:'str') -> 'str':
    """ Evaluate which pattern matches the given topic name for a security definition.
    Returns the matched pattern or raises an exception if no pattern matches.
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info('DEBUG evaluate_pattern_match - sec_base_id=%s, cluster_id=%s, topic_name=%s', sec_base_id, cluster_id, topic_name)

    # Zato
    from zato.common.pubsub.matcher import PatternMatcher

    permissions = get_permissions_for_sec_base(session, sec_base_id, cluster_id)
    logger.info('DEBUG evaluate_pattern_match - permissions found: %s', permissions)

    if not permissions:
        logger.error('DEBUG evaluate_pattern_match - no permissions found for sec_base_id %s', sec_base_id)
        raise ValueError(f'No permissions defined for security definition {sec_base_id}')

    # Create temporary matcher
    matcher = PatternMatcher()

    # Add client to matcher
    client_id = f'eval.{sec_base_id}.{topic_name}'
    logger.info('DEBUG evaluate_pattern_match - adding client %s with permissions: %s', client_id, permissions)
    matcher.add_client(client_id, permissions)

    # Evaluate for subscribe operation (subscriptions are for subscribers)
    logger.info('DEBUG evaluate_pattern_match - evaluating client_id=%s, topic_name=%s, operation=subscribe', client_id, topic_name)
    result = matcher.evaluate(client_id, topic_name, 'subscribe')
    logger.info('DEBUG evaluate_pattern_match - result: is_ok=%s, matched_pattern=%s, result_type=%s', result.is_ok, result.matched_pattern, type(result))

    if result.is_ok and result.matched_pattern:
        logger.info('DEBUG evaluate_pattern_match - returning matched pattern: %s', result.matched_pattern)
        return result.matched_pattern
    else:
        logger.error('DEBUG evaluate_pattern_match - no pattern matched, raising ValueError')
        raise ValueError(f'Topic "{topic_name}" does not match any subscription patterns for security definition {sec_base_id}')

# ################################################################################################################################
# ################################################################################################################################
