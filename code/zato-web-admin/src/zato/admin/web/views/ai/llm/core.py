# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.views.ai.llm.anthropic import AnthropicClient
from zato.admin.web.views.ai.llm.base import BaseLLMClient
from zato.admin.web.views.ai.llm.google import GoogleClient
from zato.admin.web.views.ai.llm.openai import OpenAIClient

# ################################################################################################################################
# ################################################################################################################################

Provider_To_Client = {
    'anthropic': AnthropicClient,
    'openai': OpenAIClient,
    'google': GoogleClient,
}

# ################################################################################################################################
# ################################################################################################################################

def get_llm_client(provider:'str', api_key:'str', zato_client:'any_'=None, cluster_id:'int'=None) -> 'BaseLLMClient':
    """ Returns an LLM client for the given provider.
    """
    client_class = Provider_To_Client.get(provider)

    if not client_class:
        raise ValueError(f'Unknown provider: {provider}')

    out = client_class(api_key, zato_client, cluster_id)
    return out

# ################################################################################################################################
# ################################################################################################################################
