# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# PyYAML
from yaml import safe_load

# Zato
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

# The file the model catalog is kept in, inside a server's user-conf directory,
# where the dashboard's config tables page edits it.
models_file_name = 'default-models.yaml'

# The catalog of models offered by the dashboard - Claude first, then OpenAI, then Gemini,
# with ids being what each provider's API expects on the wire. This is what a new environment
# starts default-models.yaml with and what environments without that file read.
default_models_yaml = """models:

  - provider: claude
    id: claude-fable-5-1
    name: Fable 5.1

  - provider: claude
    id: claude-fable-5
    name: Fable 5

  - provider: claude
    id: claude-opus-5
    name: Opus 5

  - provider: claude
    id: claude-sonnet-5
    name: Sonnet 5

  - provider: claude
    id: claude-opus-4-8
    name: Opus 4.8

  - provider: openai
    id: gpt-5.6-sol
    name: GPT-5.6 Sol

  - provider: openai
    id: gpt-5.6-terra
    name: GPT-5.6 Terra

  - provider: openai
    id: gpt-5.6-luna
    name: GPT-5.6 Luna

  - provider: gemini
    id: gemini-3.6-flash
    name: Gemini 3.6 Flash

  - provider: gemini
    id: gemini-3.5-flash
    name: Gemini 3.5 Flash

  - provider: gemini
    id: gemini-3.5-flash-lite
    name: Gemini 3.5 Flash Lite

  - provider: gemini
    id: gemini-3.1-flash-lite
    name: Gemini 3.1 Flash Lite

  - provider: gemini
    id: gemini-2.5-pro
    name: Gemini 2.5 Pro
"""

# The default catalog in its parsed form, for the consumers that need a default model
# without reading any file.
_default_models = safe_load(default_models_yaml)

default_model_list:'dictlist' = _default_models['models']

# ################################################################################################################################
# ################################################################################################################################

def get_model_list(user_conf_dir:'str') -> 'dictlist':
    """ The model catalog from default-models.yaml in the given directory,
    or the default catalog if the directory does not have the file.
    """

    # Where the catalog is kept in this directory ..
    full_path = os.path.join(user_conf_dir, models_file_name)

    # .. environments created before the file existed read the default catalog ..
    if not os.path.exists(full_path):
        return default_model_list

    # .. and everyone else reads the file afresh, so the catalog is always what the file says now.
    with open_r(full_path) as opened:
        contents = opened.read()

    data = safe_load(contents)

    out = data['models']
    return out

# ################################################################################################################################
# ################################################################################################################################
