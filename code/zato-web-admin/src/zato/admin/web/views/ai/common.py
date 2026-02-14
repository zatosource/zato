# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redis
import redis

# ################################################################################################################################
# ################################################################################################################################

Providers = ('anthropic', 'openai', 'google')

Redis_Key_Prefix_API_Key = 'zato.ai-chat.api-key.'

# ################################################################################################################################
# ################################################################################################################################

def get_redis_client() -> 'redis.Redis':
    """ Returns a Redis client instance.
    """
    out = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    return out

# ################################################################################################################################

def is_valid_provider(provider:'str') -> 'bool':
    """ Returns True if the provider is valid.
    """
    out = provider in Providers
    return out

# ################################################################################################################################

def get_api_key(provider:'str') -> 'str | None':
    """ Returns the API key for a provider or None if not set.
    """
    client = get_redis_client()
    out = client.get(Redis_Key_Prefix_API_Key + provider)
    return out

# ################################################################################################################################

def set_api_key(provider:'str', api_key:'str') -> 'None':
    """ Sets the API key for a provider.
    """
    client = get_redis_client()
    client.set(Redis_Key_Prefix_API_Key + provider, api_key)

# ################################################################################################################################

def delete_api_key(provider:'str') -> 'None':
    """ Deletes the API key for a provider.
    """
    client = get_redis_client()
    client.delete(Redis_Key_Prefix_API_Key + provider)

# ################################################################################################################################

def get_all_api_key_status() -> 'dict':
    """ Returns a dict of provider -> bool indicating if key exists.
    """
    out = {}
    for provider in Providers:
        key = get_api_key(provider)
        out[provider] = bool(key)
    return out

# ################################################################################################################################
# ################################################################################################################################
