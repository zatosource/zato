# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from shutil import rmtree

# Zato
from zato.admin.web.util import get_server_directory
from zato.admin.web.views import method_allowed
from zato.admin.web.views.config_files import build_index_response, ContentInfo, Definition, handle_persist, to_directory
from zato.common.skills.api import example_skill_contents, example_skill_name, get_skills_directory, skill_file_name
from zato.common.util.open_ import open_w

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

_template_name = 'zato/ai/skills.html'

# Every file of this screen is a skill, there is no other kind here
_kind_skill = 'skill'

# ################################################################################################################################
# ################################################################################################################################

def _get_server_skills_directory() -> 'str':
    """ Where the server whose files the dashboard works with keeps its user-authored skills.
    """
    server_directory = get_server_directory()
    repo_location = os.path.join(server_directory, 'config', 'repo')

    out = get_skills_directory(repo_location)
    return out

# ################################################################################################################################

def _ensure_skills_directory() -> 'None':
    """ A missing skills directory is created with the starter skill in it, an existing one,
    with or without any skills in it, is left alone.
    """
    skills_directory = _get_server_skills_directory()

    if os.path.exists(skills_directory):
        return

    example_directory = os.path.join(skills_directory, example_skill_name)
    os.makedirs(example_directory)

    example_path = os.path.join(example_directory, skill_file_name)

    with open_w(example_path) as example_file:
        _ = example_file.write(example_skill_contents)

    logger.info('Skills: created %s', example_path)

# ################################################################################################################################
# ################################################################################################################################

class SkillsDefinition(Definition):
    """ The Skills screen on the kit - the user-authored skills under the server's
    config/repo/skills directory, one subdirectory with a SKILL.md file per skill,
    listed and edited by the directory's name.
    """
    template_name = _template_name
    log_prefix = 'Skills'

# ################################################################################################################################

    def get_directory_list(self) -> 'strlist':

        out = [to_directory(_get_server_skills_directory())]
        return out

# ################################################################################################################################

    def build_content_info(self, file_name:'str', content:'str') -> 'ContentInfo':

        out = ContentInfo(_kind_skill, 0, 0)
        return out

# ################################################################################################################################

    def get_full_path(self, directory:'str', file_name:'str') -> 'str':
        """ The full path to the skill's SKILL.md file. The name names a skill directory
        and nothing else.
        """
        base_name = os.path.basename(file_name)

        if base_name != file_name:
            raise Exception(f'Invalid skill name `{file_name}`')

        directory = to_directory(directory)

        if directory not in self.get_directory_list():
            raise Exception(f'Invalid directory `{directory}`')

        out = os.path.join(directory, base_name, skill_file_name)
        return out

# ################################################################################################################################

    def get_file_list(self, directory_list:'strlist') -> 'anylist':
        """ One entry per skill - every subdirectory that holds a SKILL.md file,
        under the directory's own name.
        """
        out:'anylist' = []

        for directory in directory_list:

            # The directory may not exist yet
            if not os.path.exists(directory):
                continue

            for name in sorted(os.listdir(directory)):

                if not self.is_listed(name):
                    continue

                full_path = os.path.join(directory, name, skill_file_name)

                if not os.path.isfile(full_path):
                    continue

                item = self.build_file_item(directory, name, full_path)
                out.append(item)

        return out

# ################################################################################################################################

    def rename(self, request_data:'anydict') -> 'anydict':
        """ Renames the skill's directory, its SKILL.md file riding along inside it.
        """
        directory = request_data['directory']

        full_path = self.get_full_path(directory, request_data['file_name'])
        new_full_path = self.get_full_path(directory, request_data['new_file_name'])

        skill_directory = os.path.dirname(full_path)
        new_skill_directory = os.path.dirname(new_full_path)

        if os.path.exists(new_skill_directory):
            raise Exception(f'Skill already exists `{new_skill_directory}`')

        os.rename(skill_directory, new_skill_directory)

        logger.info('%s: renamed %s to %s', self.log_prefix, skill_directory, new_skill_directory)

        out = {'path': new_full_path}
        return out

# ################################################################################################################################

    def delete(self, request_data:'anydict') -> 'anydict':
        """ Removes the whole skill directory, not only the SKILL.md file in it.
        """
        full_path = self.get_full_path(request_data['directory'], request_data['file_name'])
        skill_directory = os.path.dirname(full_path)

        if os.path.exists(skill_directory):
            rmtree(skill_directory)
            logger.info('%s: deleted %s', self.log_prefix, skill_directory)

        out = {'path': full_path}
        return out

# ################################################################################################################################
# ################################################################################################################################

_definition = SkillsDefinition()

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    _ensure_skills_directory()

    out = build_index_response(req, _definition)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def persist(req:'any_') -> 'HttpResponse':

    out = handle_persist(req, _definition)
    return out

# ################################################################################################################################
# ################################################################################################################################
