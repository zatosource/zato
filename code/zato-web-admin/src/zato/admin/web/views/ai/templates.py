# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps
from logging import getLogger
from shutil import copytree

# Zato
from zato.admin.web.util import get_server_directory
from zato.admin.web.views import method_allowed
from zato.admin.web.views.config_files import build_index_response, ContentInfo, Definition, handle_persist, to_directory
from zato.common.alerting.explain.skill import get_default_skills_dir, Skill_File_Name, Skills_Dir_Name
from zato.common.alerting.rendering import get_default_template_dir, Template_Dir_Name
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpResponse
    from django.template.response import TemplateResponse
    from zato.common.typing_ import any_, anydict, anylist, strlist

    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_template_name = 'zato/ai/templates.html'

# The two kinds of files on this screen - the notification templates and the explanation skills
Kind_Template = 'template'
Kind_Skill = 'skill'

# What a notification template's file name ends with
Template_Suffix = '.j2'

# The Jinja markers a template's contents are counted by
_block_marker = '{%'
_expression_marker = '{{'

# What opens a section of a skill
_section_marker = '#'

# The shipped template a new one starts out as a copy of
_starter_template_name = 'email-body.j2'

# ################################################################################################################################
# ################################################################################################################################

def _get_repo_location() -> 'str':
    """ The config/repo directory of the server whose files the dashboard works with.
    """
    server_directory = get_server_directory()

    out = os.path.join(server_directory, 'config', 'repo')
    return out

# ################################################################################################################################

def get_server_templates_directory() -> 'str':
    """ Where the server keeps its alert notification templates.
    """
    out = os.path.join(_get_repo_location(), Template_Dir_Name)
    return out

# ################################################################################################################################

def get_server_skills_directory() -> 'str':
    """ Where the server keeps its alert explanation skills.
    """
    out = os.path.join(_get_repo_location(), Skills_Dir_Name)
    return out

# ################################################################################################################################

def ensure_directories(templates_directory:'str', skills_directory:'str') -> 'None':
    """ A missing directory is seeded from the shipped defaults, an existing one is left alone.
    """
    if not os.path.exists(templates_directory):
        _ = copytree(get_default_template_dir(), templates_directory)
        logger.info('Templates: created %s', templates_directory)

    if not os.path.exists(skills_directory):
        _ = copytree(get_default_skills_dir(), skills_directory)
        logger.info('Templates: created %s', skills_directory)

# ################################################################################################################################
# ################################################################################################################################

class TemplatesDefinition(Definition):
    """ The Templates screen on the kit - the alert notification templates under the server's
    alert-templates directory, one .j2 file each, and the alert explanation skills under its
    alert-skills directory, one subdirectory with a SKILL.md file per audit source. New files are
    templates and land in the first directory, a skill is one per source and is only ever edited.
    """
    template_name = _template_name
    log_prefix = 'Templates'

    def __init__(self, templates_directory:'str', skills_directory:'str') -> 'None':
        self.templates_directory = to_directory(templates_directory)
        self.skills_directory = to_directory(skills_directory)

# ################################################################################################################################

    def get_directory_list(self) -> 'strlist':

        out = [self.templates_directory, self.skills_directory]
        return out

# ################################################################################################################################

    def get_extra_context(self) -> 'anydict':
        """ A new template starts out as the shipped email body.
        """
        starter_path = os.path.join(get_default_template_dir(), _starter_template_name)

        with open_r(starter_path) as starter_file:
            starter = starter_file.read()

        out = {'new_template_content_json': dumps(starter)}
        return out

# ################################################################################################################################

    def is_skills_directory(self, directory:'str') -> 'bool':

        out = to_directory(directory) == self.skills_directory
        return out

# ################################################################################################################################

    def build_content_info(self, file_name:'str', content:'str') -> 'ContentInfo':
        """ A template is counted by its Jinja blocks and expressions, a skill by its sections.
        """
        if file_name.endswith(Template_Suffix):
            out = ContentInfo(Kind_Template, content.count(_block_marker), content.count(_expression_marker))
            return out

        section_count = 0

        for line in content.split('\n'):
            if line.startswith(_section_marker):
                section_count += 1

        out = ContentInfo(Kind_Skill, section_count, 0)
        return out

# ################################################################################################################################

    def get_full_path(self, directory:'str', file_name:'str') -> 'str':
        """ The full path to a template file, or to the SKILL.md file of the skill directory the name stands for.
        """
        base_name = os.path.basename(file_name)

        if base_name != file_name:
            raise Exception(f'Invalid file name `{file_name}`')

        directory = to_directory(directory)

        if directory not in self.get_directory_list():
            raise Exception(f'Invalid directory `{directory}`')

        if self.is_skills_directory(directory):
            out = os.path.join(directory, base_name, Skill_File_Name)
        else:
            out = os.path.join(directory, base_name)

        return out

# ################################################################################################################################

    def get_file_list(self, directory_list:'strlist') -> 'anylist':
        """ The .j2 files of the templates directory and the skill directories of the skills one,
        each skill under the name of the source it explains.
        """
        out:'anylist' = []

        for directory in directory_list:

            # A directory the screen reads from does not have to exist yet
            if not os.path.exists(directory):
                continue

            is_skills = self.is_skills_directory(directory)

            for name in sorted(os.listdir(directory)):

                if not self.is_listed(name):
                    continue

                if is_skills:
                    full_path = os.path.join(directory, name, Skill_File_Name)
                else:
                    full_path = os.path.join(directory, name)

                    if not name.endswith(Template_Suffix):
                        continue

                if not os.path.isfile(full_path):
                    continue

                item = self.build_file_item(directory, name, full_path)
                out.append(item)

        return out

# ################################################################################################################################

    def create(self, request_data:'anydict') -> 'anydict':
        """ A new file is a template - a skill is one per source and cannot be added here.
        """
        if self.is_skills_directory(request_data['directory']):
            raise Exception('Skills cannot be created, each source has exactly one')

        if not request_data['file_name'].endswith(Template_Suffix):
            raise Exception(f'A template name must end with `{Template_Suffix}`')

        out = super().create(request_data)
        return out

# ################################################################################################################################

    def rename(self, request_data:'anydict') -> 'anydict':
        """ A template can be renamed, a skill is named after the source it explains and cannot.
        """
        if self.is_skills_directory(request_data['directory']):
            raise Exception('Skills cannot be renamed, each is named after the source it explains')

        if not request_data['new_file_name'].endswith(Template_Suffix):
            raise Exception(f'A template name must end with `{Template_Suffix}`')

        out = super().rename(request_data)
        return out

# ################################################################################################################################

    def delete(self, request_data:'anydict') -> 'anydict':
        """ A template can be deleted, a skill cannot - a source without one would go unexplained.
        """
        if self.is_skills_directory(request_data['directory']):
            raise Exception('Skills cannot be deleted, each source has exactly one')

        out = super().delete(request_data)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_definition() -> 'TemplatesDefinition':
    """ The definition over the server's own directories - built per request because
    the server directory is read from the environment.
    """
    out = TemplatesDefinition(get_server_templates_directory(), get_server_skills_directory())
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    definition = _get_definition()
    ensure_directories(definition.templates_directory, definition.skills_directory)

    out = build_index_response(req, definition)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def persist(req:'any_') -> 'HttpResponse':

    out = handle_persist(req, _get_definition())
    return out

# ################################################################################################################################
# ################################################################################################################################
