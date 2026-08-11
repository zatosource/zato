# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads
from tempfile import TemporaryDirectory

# pytest
import pytest

# Zato
from zato.admin.web.views.ai.skills import _ensure_skills_directory, SkillsDefinition
from zato.admin.web.views.config_files import handle_persist
from zato.common.skills.api import example_skill_name, skill_file_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anydict

    strgen = Iterator[str]

# ################################################################################################################################
# ################################################################################################################################

_skill_contents = """---
name: invoice-mapping
description: How invoices map between systems
---

Map the invoice number to the reference field.
"""

# ################################################################################################################################
# ################################################################################################################################

class _FakeRequest:
    """ Carries just what handle_persist reaches for on the real Django request.
    """
    def __init__(self, payload:'anydict') -> 'None':
        serialized = dumps(payload)
        self.body = serialized.encode('utf-8')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def server_directory(monkeypatch:'any_') -> 'strgen':
    """ A temporary server directory the view works with, named by the same environment
    variable the dashboard reads.
    """
    with TemporaryDirectory() as directory:
        monkeypatch.setenv('ZATO_SERVER_BASE_DIR', directory)
        yield directory

# ################################################################################################################################

def _persist(action:'str', data:'anydict') -> 'anydict':
    """ Runs one persist action through the kit's handler the way the page sends it.
    """
    request = _FakeRequest({'action': action, 'data': data})
    response = handle_persist(request, SkillsDefinition())

    response_text = response.content.decode('utf-8')
    out = loads(response_text)
    return out

# ################################################################################################################################

def _write_skill(server_directory:'str', name:'str') -> 'None':
    skill_directory = os.path.join(server_directory, 'config', 'repo', 'skills', name)
    os.makedirs(skill_directory)

    with open(os.path.join(skill_directory, skill_file_name), 'w') as skill_file:
        _ = skill_file.write(_skill_contents)

# ################################################################################################################################
# ################################################################################################################################

class TestEnsureSkillsDirectory:

    def test_first_visit_creates_the_example_skill(self, server_directory:'str') -> 'None':

        _ensure_skills_directory()

        example_path = os.path.join(server_directory, 'config', 'repo', 'skills', example_skill_name, skill_file_name)
        assert os.path.isfile(example_path)

    def test_existing_directory_is_left_alone(self, server_directory:'str') -> 'None':

        # An empty skills directory, as after the user deleted every skill ..
        skills_directory = os.path.join(server_directory, 'config', 'repo', 'skills')
        os.makedirs(skills_directory)

        _ensure_skills_directory()

        # .. is not repopulated with the example.
        assert os.listdir(skills_directory) == []

# ################################################################################################################################
# ################################################################################################################################

class TestSkillsListing:

    def test_each_skill_directory_is_one_entry(self, server_directory:'str') -> 'None':

        _write_skill(server_directory, 'invoice-mapping')
        _write_skill(server_directory, 'order-lookup')

        # A subdirectory without a SKILL.md file is not a skill
        os.makedirs(os.path.join(server_directory, 'config', 'repo', 'skills', 'not-a-skill'))

        definition = SkillsDefinition()
        file_list = definition.get_file_list(definition.get_directory_list())

        names = []
        for item in file_list:
            names.append(item['name'])

        assert names == ['invoice-mapping', 'order-lookup']

        first_item = file_list[0]
        assert first_item['kind'] == 'skill'
        assert first_item['is_editable'] is True
        assert 'Map the invoice number' in first_item['content']

# ################################################################################################################################
# ################################################################################################################################

class TestSkillsPersist:

    def test_add_and_save(self, server_directory:'str') -> 'None':

        definition = SkillsDefinition()
        directory = definition.get_directory_list()[0]

        # A new skill lands as a directory with a SKILL.md file inside ..
        result = _persist('add', {'directory': directory, 'file_name': 'new-skill', 'data': _skill_contents})
        assert result['success'] is True

        skill_path = os.path.join(directory, 'new-skill', skill_file_name)
        assert os.path.isfile(skill_path)

        # .. and a save replaces that file's contents.
        result = _persist('save', {'directory': directory, 'file_name': 'new-skill', 'data': 'changed'})
        assert result['success'] is True

        with open(skill_path) as skill_file:
            assert skill_file.read() == 'changed'

    def test_rename_moves_the_directory(self, server_directory:'str') -> 'None':

        _write_skill(server_directory, 'invoice-mapping')

        definition = SkillsDefinition()
        directory = definition.get_directory_list()[0]

        result = _persist('rename', {
            'directory': directory,
            'file_name': 'invoice-mapping',
            'new_file_name': 'order-lookup',
        })
        assert result['success'] is True

        assert not os.path.exists(os.path.join(directory, 'invoice-mapping'))
        assert os.path.isfile(os.path.join(directory, 'order-lookup', skill_file_name))

    def test_delete_removes_the_directory(self, server_directory:'str') -> 'None':

        _write_skill(server_directory, 'invoice-mapping')

        definition = SkillsDefinition()
        directory = definition.get_directory_list()[0]

        result = _persist('delete', {'directory': directory, 'file_name': 'invoice-mapping'})
        assert result['success'] is True

        assert not os.path.exists(os.path.join(directory, 'invoice-mapping'))

    def test_a_name_reaching_outside_is_refused(self, server_directory:'str') -> 'None':

        definition = SkillsDefinition()
        directory = definition.get_directory_list()[0]

        result = _persist('add', {'directory': directory, 'file_name': '../outside', 'data': 'x'})
        assert result['success'] is False

        assert not os.path.exists(os.path.join(directory, '..', 'outside'))

# ################################################################################################################################
# ################################################################################################################################
