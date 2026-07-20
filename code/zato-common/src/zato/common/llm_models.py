# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The catalog of models offered by the dashboard - Claude first, then OpenAI, then Gemini,
# with ids being what each provider's API expects on the wire.
model_list = [
    {'provider': 'claude', 'id': 'claude-fable-5', 'name': 'Fable 5'},
    {'provider': 'claude', 'id': 'claude-opus-4-8', 'name': 'Opus 4.8'},
    {'provider': 'claude', 'id': 'claude-sonnet-5', 'name': 'Sonnet 5'},
    {'provider': 'openai', 'id': 'gpt-5.6-terra', 'name': 'GPT-5.6 Terra'},
    {'provider': 'openai', 'id': 'gpt-5.6-sol', 'name': 'GPT-5.6 Sol'},
    {'provider': 'openai', 'id': 'gpt-5.6-luna', 'name': 'GPT-5.6 Luna'},
    {'provider': 'gemini', 'id': 'gemini-2.5-pro', 'name': 'Gemini 2.5 Pro'},
    {'provider': 'gemini', 'id': 'gemini-3.5-flash', 'name': 'Gemini 3.5 Flash'},
    {'provider': 'gemini', 'id': 'gemini-3.1-flash-lite', 'name': 'Gemini 3.1 Flash Lite'},
]

# ################################################################################################################################
# ################################################################################################################################
