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

    for md_file in sorted(_prompts_dir.glob('*.md')):
        if md_file.name.startswith('internal'):
            continue
        content = md_file.read_text(encoding='utf-8')
        prompt_parts.append(content.strip())

    out = '\n\n'.join(prompt_parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
