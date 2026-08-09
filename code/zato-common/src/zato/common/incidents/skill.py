# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The frontmatter block of a skill file opens and closes with this marker.
_frontmatter_marker = '---'

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

    # Our response to produce
    out = Skill()
    out.source = source

    # Split the document into the frontmatter and the body ..
    lines = data.split('\n')
    body_start_index = 0
    is_in_frontmatter = False

    for index, line in enumerate(lines):

        # .. the first marker opens the frontmatter ..
        if line.strip() == _frontmatter_marker:

            if not is_in_frontmatter:
                is_in_frontmatter = True
                continue

            # .. and the second one closes it, with the body starting right after.
            body_start_index = index + 1
            break

        # .. each frontmatter line is a key and a value around the first colon ..
        if is_in_frontmatter:

            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()

            if key == 'name':
                out.name = value
            elif key == 'description':
                out.description = value

    # .. everything after the frontmatter is the instructions.
    body_lines:'strlist' = lines[body_start_index:]
    out.instructions = '\n'.join(body_lines).strip()

    return out

# ################################################################################################################################

def load_skill(source:'str') -> 'Skill | None':
    """ Returns the diagnostic skill for an audit source, reading it from disk on first use.
    Sources without a skill of their own return None - not every connection family has one yet.
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
