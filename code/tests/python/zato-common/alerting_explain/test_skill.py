# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.audit_log.api import AuditSource
from zato.common.alerting.explain.skill import get_default_skills_dir, get_skill_source, load_skill, parse_skill, \
    Skill_File_Name

# ################################################################################################################################
# ################################################################################################################################

# Every audit source that ships with an explanation skill of its own.
_shipped_sources = (
    AuditSource.REST_Outgoing,
    AuditSource.SQL_Outgoing,
    AuditSource.LLM,
    AuditSource.MCP,
    AuditSource.Microsoft_Cloud,
    AuditSource.Email_SMTP,
    AuditSource.Email_IMAP,
    AuditSource.Odoo,
    AuditSource.File_Outgoing,
    AuditSource.Scheduler,
)

# The sources whose skill may propose resubmitting
_resubmit_sources = (AuditSource.REST_Outgoing, AuditSource.File_Outgoing)

# The four sections every skill teaches the LLM to read
_sections = ('Alert', 'Object', 'Failures', 'Baseline')

# ################################################################################################################################
# ################################################################################################################################

_skill_document = """---
name: test-explanation
description: Explains test connections
remediations: resubmit, restart
---

# Test explanation

The instructions of the skill.
"""

_skill_document_without_remediations = """---
name: test-explanation
description: Explains test connections
---

# Test explanation
"""

# ################################################################################################################################
# ################################################################################################################################

class TestParseSkill:

    def test_the_header_becomes_the_name_and_description(self) -> 'None':
        skill = parse_skill('test-source', _skill_document)

        assert skill.source == 'test-source'
        assert skill.name == 'test-explanation'
        assert skill.description == 'Explains test connections'

    def test_everything_after_the_header_is_the_instructions(self) -> 'None':
        skill = parse_skill('test-source', _skill_document)

        assert skill.instructions.startswith('# Test explanation')
        assert 'The instructions of the skill.' in skill.instructions
        assert 'remediations' not in skill.instructions

    def test_the_header_names_the_remediations_in_order(self) -> 'None':
        skill = parse_skill('test-source', _skill_document)

        assert skill.remediations == ['resubmit', 'restart']

    def test_a_header_without_remediations_allows_none(self) -> 'None':
        skill = parse_skill('test-source', _skill_document_without_remediations)

        assert skill.remediations == []

# ################################################################################################################################
# ################################################################################################################################

class TestGetSkillSource:

    def test_a_health_check_is_explained_with_the_connections_skill(self) -> 'None':
        assert get_skill_source(AuditSource.REST_Outgoing_Health) == AuditSource.REST_Outgoing
        assert get_skill_source(AuditSource.SOAP_Outgoing_Health) == AuditSource.SOAP_Outgoing

    def test_a_probe_is_explained_with_the_connections_skill(self) -> 'None':
        assert get_skill_source(AuditSource.Test_Transfer) == AuditSource.File_Outgoing
        assert get_skill_source(AuditSource.Microsoft_Health) == AuditSource.Microsoft_Cloud

    def test_every_other_source_is_explained_with_its_own(self) -> 'None':
        assert get_skill_source(AuditSource.LLM) == AuditSource.LLM
        assert get_skill_source(AuditSource.Scheduler) == AuditSource.Scheduler

# ################################################################################################################################
# ################################################################################################################################

class TestLoadSkill:

    def test_the_rest_outgoing_skill_ships_with_the_package(self) -> 'None':
        skill = load_skill(AuditSource.REST_Outgoing)

        assert skill is not None
        assert skill.name == 'rest-outgoing-explanation'
        assert skill.remediations == ['resubmit']

    def test_a_source_without_a_skill_returns_none(self) -> 'None':
        skill = load_skill('source-with-no-skill')

        assert skill is None

    def test_the_skill_is_cached_between_calls(self) -> 'None':
        first = load_skill(AuditSource.REST_Outgoing)
        second = load_skill(AuditSource.REST_Outgoing)

        assert first is second

    def test_a_servers_own_directory_wins_over_the_shipped_skills(self, tmp_path:'os.PathLike') -> 'None':

        skills_dir = os.path.join(str(tmp_path), 'alert-skills')
        os.makedirs(os.path.join(skills_dir, AuditSource.LLM))

        with open(os.path.join(skills_dir, AuditSource.LLM, Skill_File_Name), 'w') as f:
            _ = f.write(_skill_document)

        skill = load_skill(AuditSource.LLM, skills_dir)

        assert skill is not None
        assert skill.name == 'test-explanation'
        assert skill.remediations == ['resubmit', 'restart']

        # The shipped one is untouched
        shipped = load_skill(AuditSource.LLM)

        assert shipped is not None
        assert shipped.name == 'llm-explanation'

    def test_an_edited_skill_is_read_again(self, tmp_path:'os.PathLike') -> 'None':

        skills_dir = os.path.join(str(tmp_path), 'alert-skills')
        os.makedirs(os.path.join(skills_dir, AuditSource.Odoo))
        path = os.path.join(skills_dir, AuditSource.Odoo, Skill_File_Name)

        with open(path, 'w') as f:
            _ = f.write(_skill_document)

        first = load_skill(AuditSource.Odoo, skills_dir)

        with open(path, 'w') as f:
            _ = f.write(_skill_document_without_remediations)

        # The file is newer than the cached copy
        os.utime(path, (os.path.getmtime(path) + 10, os.path.getmtime(path) + 10))

        second = load_skill(AuditSource.Odoo, skills_dir)

        assert first is not None
        assert second is not None
        assert first.remediations == ['resubmit', 'restart']
        assert second.remediations == []

    def test_the_default_skills_dir_holds_the_shipped_skills(self) -> 'None':

        for source in _shipped_sources:
            assert os.path.isfile(os.path.join(get_default_skills_dir(), source, Skill_File_Name))

# ################################################################################################################################
# ################################################################################################################################

class TestShippedSkills:

    @pytest.mark.parametrize('source', _shipped_sources)
    def test_every_shipped_skill_loads_with_a_complete_header(self, source:'str') -> 'None':
        skill = load_skill(source)

        assert skill is not None
        assert skill.name == f'{source}-explanation'
        assert skill.description != ''
        assert skill.instructions != ''

    @pytest.mark.parametrize('source', _shipped_sources)
    def test_every_shipped_skill_teaches_the_four_sections(self, source:'str') -> 'None':
        skill = load_skill(source)

        assert skill is not None

        for section in _sections:
            assert f'{section} - ' in skill.instructions, (source, section)

        assert '"confidence": "low | medium | high"' in skill.instructions

    @pytest.mark.parametrize('source', _shipped_sources)
    def test_only_the_transfer_and_rest_skills_may_resubmit(self, source:'str') -> 'None':
        skill = load_skill(source)

        assert skill is not None

        if source in _resubmit_sources:
            assert skill.remediations == ['resubmit']
            assert '"remediation": {"action": "resubmit"}' in skill.instructions
        else:
            assert skill.remediations == []
            assert '"remediation": null' in skill.instructions

# ################################################################################################################################
# ################################################################################################################################
