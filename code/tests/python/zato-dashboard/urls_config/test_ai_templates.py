# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The AI -> Templates page - the alert notification templates and the alert explanation skills
# on the config files kit. The URLs resolve, both kinds are listed, a template can be created,
# renamed, edited and deleted, a skill can only be edited.

# stdlib
import os
import tempfile
from shutil import rmtree

# Zato
from zato.admin import urls
from zato.admin.web.views.ai.templates import ensure_directories, Kind_Skill, Kind_Template, TemplatesDefinition
from zato.common.alerting.explain.skill import Skill_File_Name

# ################################################################################################################################
# ################################################################################################################################

_shipped_template_count = 7
_shipped_skill_count = 10

# ################################################################################################################################
# ################################################################################################################################

def _url_names() -> 'list[str]':

    out = []

    for pattern in urls.urlpatterns:

        name = getattr(pattern, 'name', None)

        if name:
            out.append(name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAITemplatesURLs:

    def test_the_page_and_its_persist_endpoint_resolve(self) -> 'None':

        names = _url_names()

        assert 'ai-templates' in names
        assert 'ai-templates-persist' in names

# ################################################################################################################################

    def test_the_page_sits_under_the_ai_path(self) -> 'None':

        paths = {}

        for pattern in urls.urlpatterns:

            name = getattr(pattern, 'name', None)

            if name:
                paths[name] = str(pattern.pattern)

        assert paths['ai-templates'] == '^zato/ai/templates/$'
        assert paths['ai-templates-persist'] == '^zato/ai/templates/persist/$'

# ################################################################################################################################
# ################################################################################################################################

class TestTemplatesDefinition:

    def setup_method(self) -> 'None':
        self.work_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.work_dir, 'alert-templates')
        self.skills_dir = os.path.join(self.work_dir, 'alert-skills')

        ensure_directories(self.templates_dir, self.skills_dir)

        self.definition = TemplatesDefinition(self.templates_dir, self.skills_dir)

    def teardown_method(self) -> 'None':
        rmtree(self.work_dir)

# ################################################################################################################################

    def _file_list(self) -> 'list':
        out = self.definition.get_file_list(self.definition.get_directory_list())
        return out

# ################################################################################################################################

    def test_seeding_copies_the_shipped_templates_and_skills(self) -> 'None':

        assert os.path.isfile(os.path.join(self.templates_dir, 'email-body.j2'))
        assert os.path.isfile(os.path.join(self.skills_dir, 'file-outgoing', Skill_File_Name))

# ################################################################################################################################

    def test_seeding_leaves_existing_directories_alone(self) -> 'None':

        marker = os.path.join(self.templates_dir, 'mine.j2')

        with open(marker, 'w') as f:
            _ = f.write('{{ message }}')

        ensure_directories(self.templates_dir, self.skills_dir)

        assert os.path.isfile(marker)

# ################################################################################################################################

    def test_both_kinds_are_listed(self) -> 'None':

        file_list = self._file_list()

        templates = []
        skills = []

        for item in file_list:
            if item['kind'] == Kind_Template:
                templates.append(item)
            else:
                skills.append(item)

        assert len(templates) == _shipped_template_count
        assert len(skills) == _shipped_skill_count

        # Templates come first, that is where new files land
        assert file_list[0]['kind'] == Kind_Template
        assert file_list[-1]['kind'] == Kind_Skill

# ################################################################################################################################

    def test_a_skill_is_listed_by_its_source_and_reads_its_skill_file(self) -> 'None':

        by_name = {}

        for item in self._file_list():
            by_name[item['name']] = item

        skill = by_name['rest-outgoing']

        assert skill['kind'] == Kind_Skill
        assert skill['file_name'] == 'rest-outgoing'
        assert skill['path'] == os.path.join(self.definition.skills_directory, 'rest-outgoing', Skill_File_Name)
        assert 'remediations: resubmit' in skill['content']
        assert skill['section_count'] > 3

# ################################################################################################################################

    def test_a_template_is_counted_by_its_jinja_markers(self) -> 'None':

        by_name = {}

        for item in self._file_list():
            by_name[item['name']] = item

        template = by_name['email-body.j2']

        assert template['kind'] == Kind_Template
        assert template['section_count'] == template['content'].count('{%')
        assert template['entry_count'] == template['content'].count('{{')

# ################################################################################################################################

    def test_only_j2_files_are_listed_as_templates(self) -> 'None':

        with open(os.path.join(self.templates_dir, 'notes.txt'), 'w') as f:
            _ = f.write('not a template')

        names = []

        for item in self._file_list():
            names.append(item['name'])

        assert 'notes.txt' not in names

# ################################################################################################################################

    def test_creating_a_template_lands_in_the_templates_directory(self) -> 'None':

        result = self.definition.create({
            'directory': self.definition.templates_directory,
            'file_name': 'pager.j2',
            'data': '{{ message }}',
        })

        assert result['path'] == os.path.join(self.definition.templates_directory, 'pager.j2')
        assert os.path.isfile(result['path'])

# ################################################################################################################################

    def test_creating_a_template_without_the_suffix_is_refused(self) -> 'None':

        try:
            _ = self.definition.create({
                'directory': self.definition.templates_directory,
                'file_name': 'pager',
                'data': '{{ message }}',
            })
        except Exception as e:
            assert '.j2' in str(e)
        else:
            raise AssertionError('Expected the create to be refused')

# ################################################################################################################################

    def test_creating_a_skill_is_refused(self) -> 'None':

        try:
            _ = self.definition.create({
                'directory': self.definition.skills_directory,
                'file_name': 'new-source',
                'data': '# New',
            })
        except Exception as e:
            assert 'cannot be created' in str(e)
        else:
            raise AssertionError('Expected the create to be refused')

        assert not os.path.exists(os.path.join(self.skills_dir, 'new-source'))

# ################################################################################################################################

    def test_renaming_a_skill_is_refused(self) -> 'None':

        try:
            _ = self.definition.rename({
                'directory': self.definition.skills_directory,
                'file_name': 'llm',
                'new_file_name': 'llm2',
            })
        except Exception as e:
            assert 'cannot be renamed' in str(e)
        else:
            raise AssertionError('Expected the rename to be refused')

        assert os.path.isdir(os.path.join(self.skills_dir, 'llm'))

# ################################################################################################################################

    def test_deleting_a_skill_is_refused(self) -> 'None':

        try:
            _ = self.definition.delete({
                'directory': self.definition.skills_directory,
                'file_name': 'llm',
            })
        except Exception as e:
            assert 'cannot be deleted' in str(e)
        else:
            raise AssertionError('Expected the delete to be refused')

        assert os.path.isfile(os.path.join(self.skills_dir, 'llm', Skill_File_Name))

# ################################################################################################################################

    def test_a_template_can_be_renamed_and_deleted(self) -> 'None':

        result = self.definition.rename({
            'directory': self.definition.templates_directory,
            'file_name': 'slack.j2',
            'new_file_name': 'slack-old.j2',
        })

        assert os.path.isfile(result['path'])
        assert not os.path.exists(os.path.join(self.templates_dir, 'slack.j2'))

        _ = self.definition.delete({
            'directory': self.definition.templates_directory,
            'file_name': 'slack-old.j2',
        })

        assert not os.path.exists(result['path'])

# ################################################################################################################################

    def test_an_edit_is_saved_to_each_kind(self) -> 'None':

        _ = self.definition.save({
            'directory': self.definition.templates_directory,
            'file_name': 'teams.j2',
            'data': 'teams edited',
        })

        _ = self.definition.save({
            'directory': self.definition.skills_directory,
            'file_name': 'odoo',
            'data': '# Odoo edited',
        })

        with open(os.path.join(self.templates_dir, 'teams.j2')) as f:
            assert f.read() == 'teams edited'

        with open(os.path.join(self.skills_dir, 'odoo', Skill_File_Name)) as f:
            assert f.read() == '# Odoo edited'

# ################################################################################################################################

    def test_the_starter_template_is_the_shipped_email_body(self) -> 'None':

        extra = self.definition.get_extra_context()

        assert '{{ message }}' in extra['new_template_content_json']

# ################################################################################################################################

    def test_a_path_outside_the_directories_is_refused(self) -> 'None':

        try:
            _ = self.definition.get_full_path(self.work_dir, 'email-body.j2')
        except Exception as e:
            assert 'Invalid directory' in str(e)
        else:
            raise AssertionError('Expected the path to be refused')

# ################################################################################################################################
# ################################################################################################################################
