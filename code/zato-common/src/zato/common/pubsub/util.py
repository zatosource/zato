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
# ################################################################################################################################
