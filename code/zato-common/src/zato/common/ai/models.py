# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from configparser import ConfigParser

# ################################################################################################################################
# ################################################################################################################################

models_ini = """
[claude-opus-4-6]
provider = anthropic
name = Claude Opus 4.6

[claude-sonnet-4-5]
provider = anthropic
name = Claude Sonnet 4.5

[gpt-5.2-pro]
provider = openai
name = GPT-5.2 Pro

[gpt-5.2]
provider = openai
name = GPT-5.2

[gemini-2.5-pro]
provider = google
name = Gemini 2.5 Pro

[gemini-2.5-flash]
provider = google
name = Gemini 2.5 Flash
"""

# ################################################################################################################################
# ################################################################################################################################

def get_models_by_provider(provider):
    """ Returns a list of models for the given provider.
    """
    parser = ConfigParser()
    parser.read_string(models_ini)

    result = []
    for section in parser.sections():
        if parser.get(section, 'provider') == provider:
            result.append({
                'id': section,
                'name': parser.get(section, 'name'),
            })

    return result

# ################################################################################################################################

def get_all_models():
    """ Returns all models grouped by provider.
    """
    parser = ConfigParser()
    parser.read_string(models_ini)

    result = {
        'anthropic': [],
        'openai': [],
        'google': [],
    }

    for section in parser.sections():
        provider = parser.get(section, 'provider')
        if provider in result:
            result[provider].append({
                'id': section,
                'name': parser.get(section, 'name'),
            })

    return result

# ################################################################################################################################
# ################################################################################################################################
