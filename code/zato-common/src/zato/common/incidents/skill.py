# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# Zato
from zato.common.skills.api import parse_skill_document

# ################################################################################################################################
# ################################################################################################################################

# Skills live in per-source directories next to this module, one SKILL.md each.
_skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skills')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Skill:
    """ One diagnostic skill - the name and description from its frontmatter
    and the markdown instructions that follow it.
    """
    source: str = ''
    name: str = ''
    description: str = ''
    instructions: str = ''

# ################################################################################################################################
# ################################################################################################################################

# Skills already read from disk, keyed by the audit source they diagnose.
_skill_cache:'dict[str, Skill]' = {}

# ################################################################################################################################

def parse_skill(source:'str', data:'str') -> 'Skill':
    """ Parses one SKILL.md document - the frontmatter carries the name and description,
    everything after it is the instructions.
    """

    # The document itself reads the same way for every kind of skill
    document = parse_skill_document(data)

    # Our response to produce
    out = Skill()
    out.source = source
    out.name = document.name
    out.description = document.description
    out.instructions = document.instructions

    return out

# ################################################################################################################################

def load_skill(source:'str') -> 'Skill | None':
    """ Returns the diagnostic skill for an audit source, reading it from disk on first use.
    Sources without a skill of their own return None - not every connection type has one yet.
    """

    # Skills are read once and kept in memory ..
    if source in _skill_cache:
        out = _skill_cache[source]
        return out

    # .. a source without a skill directory has no skill ..
    skill_path = os.path.join(_skills_dir, source, 'SKILL.md')

    if not os.path.exists(skill_path):
        return None

    # .. otherwise, read and parse the document ..
    with open(skill_path) as skill_file:
        data = skill_file.read()

    skill = parse_skill(source, data)

    # .. and cache it for all the calls to come.
    _skill_cache[source] = skill

    out = skill
    return out

# ################################################################################################################################
# ################################################################################################################################
