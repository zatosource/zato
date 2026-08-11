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

# The frontmatter block of a skill file opens and closes with this marker
_frontmatter_marker = '---'

# The directory under a server's config/repo that keeps the user-authored skills,
# one subdirectory per skill
skills_directory_name = 'skills'

# The one file each skill directory holds
skill_file_name = 'SKILL.md'

# The starter skill a new environment comes with - it spells out the format a skill is written in
example_skill_name = 'example'

example_skill_contents = """---
name: example
description: An example skill that shows the format every skill is written in
---

# Example skill

A skill is one directory under config/repo/skills with a SKILL.md file in it, and this
is such a file. The block between the two `---` markers above is the frontmatter - its
`name` names the skill and its `description` says what the skill is for. Everything
under the frontmatter, this text included, is the instructions.

## How skills are used

* A service passes the directory name to an LLM connection, as in
  `self.llm['My Claude'].invoke(text, skill='example')`, and the instructions become
  the system context of that call.
* An MCP gateway with this skill on its list serves it as a prompt of the same name,
  and MCP clients read it with `prompts/get`.

## Writing your own

Create a new file on the Skills screen, put the frontmatter first, then write the
instructions in plain markdown - the steps to follow, the formats to keep to and
the examples to work from.
"""

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SkillDocument:
    """ One SKILL.md document - the name and description from its frontmatter
    and the markdown instructions that follow it.
    """
    name: str = ''
    description: str = ''
    instructions: str = ''

# ################################################################################################################################
# ################################################################################################################################

def parse_skill_document(data:'str') -> 'SkillDocument':
    """ Parses one SKILL.md document - the frontmatter carries the name and description,
    everything after it is the instructions.
    """

    # Our response to produce
    out = SkillDocument()

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
# ################################################################################################################################

def get_skills_directory(repo_location:'str') -> 'str':
    """ Where a server keeps the user-authored skills, under its config/repo directory.
    """
    out = os.path.join(repo_location, skills_directory_name)
    return out

# ################################################################################################################################

def get_skill_name_list(repo_location:'str') -> 'strlist':
    """ The names of all the user-authored skills - every subdirectory of the skills
    directory that holds a SKILL.md file, sorted by name.
    """
    out:'strlist' = []
    skills_directory = get_skills_directory(repo_location)

    # The skills directory may not exist yet
    if not os.path.exists(skills_directory):
        return out

    for name in sorted(os.listdir(skills_directory)):

        skill_path = os.path.join(skills_directory, name, skill_file_name)

        if os.path.isfile(skill_path):
            out.append(name)

    return out

# ################################################################################################################################

def load_skill(repo_location:'str', name:'str') -> 'SkillDocument | None':
    """ Returns the user-authored skill of this name, read from disk on each call, never cached.
    A name without a skill returns None.
    """

    # A name reaches a skill directory and nothing else
    base_name = os.path.basename(name)

    if base_name != name:
        return None

    skill_path = os.path.join(get_skills_directory(repo_location), name, skill_file_name)

    if not os.path.isfile(skill_path):
        return None

    with open(skill_path) as skill_file:
        data = skill_file.read()

    out = parse_skill_document(data)
    return out

# ################################################################################################################################
# ################################################################################################################################
