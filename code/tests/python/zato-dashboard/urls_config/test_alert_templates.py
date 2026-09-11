# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Monitoring -> Alert templates page - the alert notification templates on the config files kit.
# The URLs resolve, only .j2 files are listed, and a template can be created, renamed, edited and deleted.

# stdlib
import os
import tempfile
from shutil import rmtree

# Zato
from zato.admin import urls
from zato.admin.web.views.monitoring.alert_templates import AlertTemplatesDefinition, ensure_directory, Kind_Template

# ################################################################################################################################
# ################################################################################################################################

_shipped_template_count = 7

# ################################################################################################################################
# ################################################################################################################################

def _url_paths() -> 'dict[str, str]':

    out = {}

    for pattern in urls.urlpatterns:

        name = getattr(pattern, 'name', None)

        if name:
            out[name] = str(pattern.pattern)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAlertTemplatesURLs:

    def test_the_page_and_its_persist_endpoint_sit_under_the_monitoring_path(self) -> 'None':

        paths = _url_paths()

        assert paths['alert-templates'] == '^zato/monitoring/alert-templates/$'
        assert paths['alert-templates-persist'] == '^zato/monitoring/alert-templates/persist/$'

# ################################################################################################################################

    def test_the_old_ai_page_is_gone(self) -> 'None':

        paths = _url_paths()

        assert 'ai-templates' not in paths
        assert 'ai-templates-persist' not in paths

# ################################################################################################################################
# ################################################################################################################################

class TestAlertTemplatesDefinition:

    def setup_method(self) -> 'None':
        self.work_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.work_dir, 'alert-templates')

        ensure_directory(self.templates_dir)

        self.definition = AlertTemplatesDefinition(self.templates_dir)

    def teardown_method(self) -> 'None':
        rmtree(self.work_dir)

# ################################################################################################################################

    def _file_list(self) -> 'list':
        out = self.definition.get_file_list(self.definition.get_directory_list())
        return out

# ################################################################################################################################

    def test_seeding_copies_the_shipped_templates(self) -> 'None':

        assert os.path.isfile(os.path.join(self.templates_dir, 'email-body.j2'))

# ################################################################################################################################

    def test_seeding_leaves_an_existing_directory_alone(self) -> 'None':

        marker = os.path.join(self.templates_dir, 'mine.j2')

        with open(marker, 'w') as f:
            _ = f.write('{{ message }}')

        ensure_directory(self.templates_dir)

        assert os.path.isfile(marker)

# ################################################################################################################################

    def test_only_the_templates_directory_is_read(self) -> 'None':

        assert self.definition.get_directory_list() == [self.definition.templates_directory]

# ################################################################################################################################

    def test_every_shipped_template_is_listed_as_a_template(self) -> 'None':

        file_list = self._file_list()

        assert len(file_list) == _shipped_template_count

        for item in file_list:
            assert item['kind'] == Kind_Template
            assert item['name'].endswith('.j2')

# ################################################################################################################################

    def test_a_template_is_counted_by_its_jinja_markers(self) -> 'None':

        by_name = {}

        for item in self._file_list():
            by_name[item['name']] = item

        template = by_name['email-body.j2']

        assert template['section_count'] == template['content'].count('{%')
        assert template['entry_count'] == template['content'].count('{{')

# ################################################################################################################################

    def test_only_j2_files_are_listed(self) -> 'None':

        with open(os.path.join(self.templates_dir, 'notes.txt'), 'w') as f:
            _ = f.write('not a template')

        os.makedirs(os.path.join(self.templates_dir, 'a-directory'))

        names = []

        for item in self._file_list():
            names.append(item['name'])

        assert 'notes.txt' not in names
        assert 'a-directory' not in names

# ################################################################################################################################

    def test_creating_a_template(self) -> 'None':

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

    def test_renaming_a_template_away_from_the_suffix_is_refused(self) -> 'None':

        try:
            _ = self.definition.rename({
                'directory': self.definition.templates_directory,
                'file_name': 'slack.j2',
                'new_file_name': 'slack.txt',
            })
        except Exception as e:
            assert '.j2' in str(e)
        else:
            raise AssertionError('Expected the rename to be refused')

        assert os.path.isfile(os.path.join(self.templates_dir, 'slack.j2'))

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

    def test_an_edit_is_saved(self) -> 'None':

        _ = self.definition.save({
            'directory': self.definition.templates_directory,
            'file_name': 'teams.j2',
            'data': 'teams edited',
        })

        with open(os.path.join(self.templates_dir, 'teams.j2')) as f:
            assert f.read() == 'teams edited'

# ################################################################################################################################

    def test_the_starter_template_is_the_shipped_email_body(self) -> 'None':

        extra = self.definition.get_extra_context()

        assert '{{ message }}' in extra['new_template_content_json']

# ################################################################################################################################

    def test_a_path_outside_the_directory_is_refused(self) -> 'None':

        try:
            _ = self.definition.get_full_path(self.work_dir, 'email-body.j2')
        except Exception as e:
            assert 'Invalid directory' in str(e)
        else:
            raise AssertionError('Expected the path to be refused')

# ################################################################################################################################
# ################################################################################################################################
