# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explanation skills - one SKILL.md per audit source, teaching the LLM how to read the
# evidence document of that source's alerts and what it may propose. The skills ship with
# the package and are copied into every server's alert-skills directory when the server
# is created, which is where the Dashboard's Templates page edits them and where they are
# read from at explanation time.

# stdlib
import os
from dataclasses import dataclass

# Zato
from zato.common.audit_log.common import AuditSource
from zato.common.skills.api import parse_skill_document
from zato.common.typing_ import list_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The skills shipped with the package live in per-source directories next to this module, one SKILL.md each.
_shipped_skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skills')

# The name of the directory a server keeps its own copies of the skills in, under its config/repo directory.
Skills_Dir_Name = 'alert-skills'

# The file each skill is - the directory it sits in is named after the audit source it explains.
Skill_File_Name = 'SKILL.md'

# The header line naming the remediations a skill allows the LLM to propose, e.g. `remediations: resubmit`.
_remediations_key = 'remediations'
_header_marker = '---'
_remediations_separator = ','

# Which skill explains the alerts of each source - a probe or a health check is explained
# with the skill of the connection it checks, every other source with its own.
explain_source_by_source = {
    AuditSource.REST_Outgoing_Health: AuditSource.REST_Outgoing,
    AuditSource.SOAP_Outgoing_Health: AuditSource.SOAP_Outgoing,
    AuditSource.Test_Transfer:        AuditSource.File_Outgoing,
    AuditSource.Microsoft_Health:     AuditSource.Microsoft_Cloud,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Skill:
    """ One explanation skill - the name, the description and the remediations from its header
    and the markdown instructions that follow it.
    """
    source: str = ''
    name: str = ''
    description: str = ''
    instructions: str = ''

    # The remediation actions the skill lets the LLM propose - a reply naming any other is kept as prose only.
    remediations: 'strlist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

# Skills already read from disk, keyed by the path they were read from and the time the file was
# last modified - an edit on the Dashboard's Templates page is picked up on the next explanation.
_skill_cache:'dict[tuple[str, float], Skill]' = {}

# ################################################################################################################################

def get_default_skills_dir() -> 'str':
    """ Where the skills shipped with the package are - what a new server's alert-skills directory is copied from.
    """
    out = _shipped_skills_dir
    return out

# ################################################################################################################################

def get_skill_source(source:'str') -> 'str':
    """ The source whose skill explains the alerts of the given one.
    """
    if source in explain_source_by_source:
        out = explain_source_by_source[source]
    else:
        out = source

    return out

# ################################################################################################################################

def _read_header_remediations(data:'str') -> 'strlist':
    """ The remediations the header names, in the order it names them - none when the header has no such line.
    """

    # Our response to produce
    out:'strlist' = []

    is_in_header = False

    for line in data.split('\n'):

        if line.strip() == _header_marker:

            # The first marker opens the header, the second one closes it
            if is_in_header:
                break

            is_in_header = True
            continue

        if not is_in_header:
            continue

        key, _, value = line.partition(':')

        if key.strip() != _remediations_key:
            continue

        for item in value.split(_remediations_separator):
            item = item.strip()
            if item:
                out.append(item)

    return out

# ################################################################################################################################

def parse_skill(source:'str', data:'str') -> 'Skill':
    """ Parses one SKILL.md document - the header carries the name, the description and the remediations,
    everything after it is the instructions.
    """

    # The document itself reads the same way for every kind of skill
    document = parse_skill_document(data)

    # Our response to produce - the list is assigned here because init=False means the field factory never runs
    out = Skill()
    out.source = source
    out.name = document.name
    out.description = document.description
    out.instructions = document.instructions
    out.remediations = _read_header_remediations(data)

    return out

# ################################################################################################################################

def load_skill(source:'str', skills_dir:'str'='') -> 'Skill | None':
    """ Returns the explanation skill for an audit source, reading it from disk on first use -
    from the server's own directory when one is given, from the shipped skills otherwise.
    Sources without a skill of their own return None - not every connection type has one yet.
    """
    if not skills_dir:
        skills_dir = _shipped_skills_dir

    skill_path = os.path.join(skills_dir, source, Skill_File_Name)

    # A source without a skill directory has no skill ..
    if not os.path.exists(skill_path):
        return None

    # .. a skill is read once per path and modification time and kept in memory ..
    cache_key = (skill_path, os.path.getmtime(skill_path))

    if cache_key in _skill_cache:
        out = _skill_cache[cache_key]
        return out

    # .. otherwise, read and parse the document ..
    with open(skill_path) as skill_file:
        data = skill_file.read()

    skill = parse_skill(source, data)

    # .. and cache it for all the calls to come.
    _skill_cache[cache_key] = skill

    out = skill
    return out

# ################################################################################################################################
# ################################################################################################################################
