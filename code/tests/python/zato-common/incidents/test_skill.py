# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditSource
from zato.common.incidents.skill import load_skill, parse_skill

# ################################################################################################################################
# ################################################################################################################################

_skill_document = """---
name: test-diagnostics
description: Diagnoses test connections
---

# Test diagnostics

The instructions of the skill.
"""

# ################################################################################################################################
# ################################################################################################################################

class TestParseSkill:

    def test_the_frontmatter_becomes_the_name_and_description(self) -> 'None':
        skill = parse_skill('test-source', _skill_document)

        assert skill.source == 'test-source'
        assert skill.name == 'test-diagnostics'
        assert skill.description == 'Diagnoses test connections'

    def test_everything_after_the_frontmatter_is_the_instructions(self) -> 'None':
        skill = parse_skill('test-source', _skill_document)

        assert skill.instructions.startswith('# Test diagnostics')
        assert 'The instructions of the skill.' in skill.instructions

# ################################################################################################################################
# ################################################################################################################################

class TestLoadSkill:

    def test_the_rest_outgoing_skill_ships_with_the_package(self) -> 'None':
        skill = load_skill(AuditSource.REST_Outgoing)

        assert skill is not None
        assert skill.name == 'rest-outgoing-diagnostics'
        assert 'resubmit' in skill.instructions

    def test_a_source_without_a_skill_returns_none(self) -> 'None':
        skill = load_skill('source-with-no-skill')

        assert skill is None

    def test_the_skill_is_cached_between_calls(self) -> 'None':
        first = load_skill(AuditSource.REST_Outgoing)
        second = load_skill(AuditSource.REST_Outgoing)

        assert first is second

# ################################################################################################################################
# ################################################################################################################################
