# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

_prompts_dir = Path(__file__).resolve().parent

# ################################################################################################################################
# ################################################################################################################################

def get_system_prompt() -> 'str':
    """ Loads and returns the system prompt from all prompt files.
    """
    prompt_parts = []

    common_path = _prompts_dir / 'common.md'
    if common_path.exists():
        content = common_path.read_text(encoding='utf-8')
        prompt_parts.append(content.strip())

    enmasse_tools_path = _prompts_dir / 'enmasse_tools.md'
    if enmasse_tools_path.exists():
        content = enmasse_tools_path.read_text(encoding='utf-8')
        prompt_parts.append(content.strip())

    out = '\n\n'.join(prompt_parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
