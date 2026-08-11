# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from pathlib import Path

# Zato
from zato.admin.web.util import get_server_user_conf_directory
from zato.admin.web.views import method_allowed
from zato.admin.web.views.config_files import build_index_response, ContentInfo, Definition, handle_persist, to_directory
from zato.common.api import EnvFile, HotDeploy
from zato.common.user_config import ModuleCtx as UserConfigCtx
from zato.common.util.api import get_user_config_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpResponse
    from django.template.response import TemplateResponse
    from zato.common.typing_ import any_, strlist, strtuple

    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

_template_name = 'zato/service/config-tables.html'

# The environment variables that point to user configuration directories
_user_conf_env_keys = ('Zato_User_Conf_Dir', 'ZATO_USER_CONF_DIR')

# The environment variables that point to the projects a server hot-deploys from, by their
# exact names and by the prefixes that any number of them may be named with
_project_env_keys = ('Zato_Project_Root', 'Zato_Hot_Deploy_Dir', 'ZATO_HOT_DEPLOY_DIR')
_project_env_prefixes = ('Zato_Project_Root_', 'Zato_Hot_Deploy_Dir_')

# What a project calls the directory it keeps user configuration in, at any depth inside it
_project_user_conf_directory = HotDeploy.User_Conf_Directory

# What separates one directory from another in the environment variables above
_env_separator = ':'

# A file with a section of this name lists the values that are accepted, a file without one
# maps the codes of a single party, per section, to such values
_codes_section = UserConfigCtx.Codes_Section

_kind_codes = 'codes'
_kind_mappings = 'mappings'

# A yaml file is edited here as text and read by whatever component named it,
# not through self.config, so what it holds is not counted the way an ini file is
_kind_yaml = 'yaml'
_yaml_suffixes = ('.yaml', '.yml')

# What a file is of until it reads as user configuration at all
_kind_error = 'error'

# ################################################################################################################################
# ################################################################################################################################

def _add_directory(directory_list:'strlist', path:'str') -> 'None':
    """ Adds the directory to the list unless the same directory is in it already, which is
    what a path named twice, or named once under a symlink of its own, comes to.
    """
    directory = to_directory(path)
    real_path = os.path.realpath(directory)

    for item in directory_list:
        if os.path.realpath(item) == real_path:
            return

    directory_list.append(directory)

# ################################################################################################################################

def _get_env_path_list(keys:'strtuple', prefixes:'strtuple') -> 'strlist':
    """ The paths that the environment names, both under the exact variable names given and
    under any variable whose name starts with one of the prefixes given. One variable may name
    any number of paths.
    """
    out:'strlist' = []
    value_list:'strlist' = []

    for key in keys:
        value = os.environ.get(key, '')
        if value:
            value_list.append(value)

    for key, value in os.environ.items():
        if key.startswith(prefixes) and value:
            value_list.append(value)

    for value in value_list:
        for path in value.split(_env_separator):
            path = path.strip()
            if path:
                out.append(path)

    return out

# ################################################################################################################################

def _get_project_directory_list(project_root:'str') -> 'strlist':
    """ The user configuration directories inside the project. A project keeps its own under
    config/user-conf and the root that the environment names may be above several projects,
    so the directory is looked up at any depth under it, which is what the server does too.
    """
    out:'strlist' = []

    for path in Path(project_root).rglob(_project_user_conf_directory):
        if path.is_dir():
            out.append(str(path))

    out.sort()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _read_content_info(content:'str') -> 'ContentInfo':
    """ What a file holds, that is, the kind of file it is, how many sections it has and how many
    entries there are under them. Counting stops at the first line that reads as neither, just as
    the reader of the file stops at it, and such a file is of no kind at all until that line is
    seen to. A section written in double brackets belongs to the one above it. A file with a codes
    section is a code list, whether the codes are in it yet or not, unless that section is there
    only to group other sections under it.
    """
    section_count = 0
    entry_count = 0
    has_codes_section = False
    codes_has_entries = False
    codes_has_children = False
    is_in_codes = False
    has_section = False
    is_readable = True
    top_name = ''

    for line in content.splitlines():

        line = line.strip()

        # Empty lines and comments say nothing about what the file holds ..
        if not line:
            continue

        if line.startswith(('#', ';')):
            continue

        # .. a section is what the entries under it belong to ..
        if line.startswith('['):

            depth = len(line) - len(line.lstrip('['))

            if len(line) - len(line.rstrip(']')) != depth:
                is_readable = False
                break

            name = line[depth:-depth].strip()
            section_count += 1
            has_section = True

            if depth == 1:
                top_name = name

            # Only the file's own codes section counts, not one that another section keeps
            is_in_codes = depth == 1 and name == _codes_section

            if is_in_codes:
                has_codes_section = True

            # A section nested under codes makes codes a group of sections rather than a
            # section of codes
            if depth > 1 and top_name == _codes_section:
                codes_has_children = True

            continue

        # .. and everything else is an entry, which needs both a section above it
        # .. and a sign that says what it maps to.
        if '=' not in line:
            is_readable = False
            break

        if not has_section:
            is_readable = False
            break

        entry_count += 1

        if is_in_codes:
            codes_has_entries = True

    is_codes_group = codes_has_children and not codes_has_entries

    if not is_readable:
        kind = _kind_error

    elif has_codes_section and not is_codes_group:
        kind = _kind_codes

    else:
        kind = _kind_mappings

    out = ContentInfo(kind, section_count, entry_count)
    return out

# ################################################################################################################################
# ################################################################################################################################

class ConfigTablesDefinition(Definition):
    """ The Config tables screen on the kit - the user configuration files that services read
    through self.config, in the directories that the server reads them from.
    """
    template_name = _template_name
    log_prefix = 'Config tables'

# ################################################################################################################################

    def get_directory_list(self) -> 'strlist':
        """ The server's own directory, the directories named in the environment, and the ones
        inside the projects that the server hot-deploys.
        """
        out:'strlist' = []

        _add_directory(out, get_server_user_conf_directory())

        for path in _get_env_path_list(_user_conf_env_keys, ()):
            _add_directory(out, path)

        for project_root in _get_env_path_list(_project_env_keys, _project_env_prefixes):
            for path in _get_project_directory_list(project_root):
                _add_directory(out, path)

        return out

# ################################################################################################################################

    def build_content_info(self, file_name:'str', content:'str') -> 'ContentInfo':

        # A yaml file is of its own kind by name alone, everything else says what it is by its contents
        file_name_lower = file_name.lower()

        if file_name_lower.endswith(_yaml_suffixes):
            out = ContentInfo(_kind_yaml, 0, 0)
        else:
            out = _read_content_info(content)

        return out

# ################################################################################################################################

    def get_display_name(self, file_name:'str') -> 'str':

        out = get_user_config_name(file_name)
        return out

# ################################################################################################################################

    def is_listed(self, file_name:'str') -> 'bool':
        """ Everything in a directory is a file the page lists, whether it reads as user
        configuration yet or not, the one exception being the environment file, which keeps secrets.
        """
        file_name_lower = file_name.lower()

        if file_name_lower == EnvFile.Default:
            return False

        out = not file_name.startswith('.')
        return out

# ################################################################################################################################
# ################################################################################################################################

_definition = ConfigTablesDefinition()

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

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
