# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads
from logging import getLogger
from pathlib import Path
from traceback import format_exc
from typing import NamedTuple

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.util import get_server_user_conf_directory
from zato.admin.web.views import method_allowed
from zato.common.api import EnvFile, HotDeploy
from zato.common.user_config import ModuleCtx as UserConfigCtx
from zato.common.util.api import get_user_config_name
from zato.common.util.open_ import open_r, open_w

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strtuple

    anydict = anydict
    anylist = anylist
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_template_name = 'zato/service/config-tables.html'

# A file larger than this is edited outside the dashboard so its contents are not sent to the browser
_max_editable_size = 256 * 1024

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

class ContentInfo(NamedTuple):
    kind: str
    section_count: int
    entry_count: int

# ################################################################################################################################
# ################################################################################################################################

def _to_directory(path:'str') -> 'str':
    """ A directory in the form all the directories here are kept and compared in, that is,
    an absolute path with a trailing separator.
    """
    out = os.path.abspath(os.path.expanduser(path)) + os.sep
    return out

# ################################################################################################################################

def _get_directory_list() -> 'strlist':
    """ The directories the page reads and writes user configuration in, which are the same
    ones that the server reads it from - the server's own directory, the directories named
    in the environment, and the ones inside the projects that the server hot-deploys.
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

def _add_directory(directory_list:'strlist', path:'str') -> 'None':
    """ Adds the directory to the list unless the same directory is in it already, which is
    what a path named twice, or named once under a symlink of its own, comes to.
    """
    directory = _to_directory(path)
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

def _get_full_path(directory:'str', file_name:'str') -> 'str':
    """ The full path to the file that the request names. A file name names a file and nothing else,
    and the directory it is in is one of the directories that user configuration is kept in. What
    the file is called beyond that is not this function's business, a file brought in to be worked
    on here being a file that does not read as user configuration yet.
    """
    base_name = os.path.basename(file_name)

    if base_name != file_name:
        raise Exception(f'Invalid file name `{file_name}`')

    directory = _to_directory(directory)

    if directory not in _get_directory_list():
        raise Exception(f'Invalid directory `{directory}`')

    out = os.path.join(directory, base_name)
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

def _build_file_item(directory:'str', file_name:'str', full_path:'str') -> 'anydict':
    """ One file as the page reads it. A file larger than the browser edits in place is reported
    without its contents because they would not be used, and so is one that is not text at all,
    a directory holding whatever the user put in it.
    """
    size = os.path.getsize(full_path)
    is_editable = size <= _max_editable_size
    content = ''

    if is_editable:
        try:
            with open_r(full_path) as opened:
                content = opened.read()
        except UnicodeDecodeError:
            is_editable = False

    # A yaml file is of its own kind by name alone, everything else says what it is by its contents
    file_name_lower = file_name.lower()

    if file_name_lower.endswith(_yaml_suffixes):
        info = ContentInfo(_kind_yaml, 0, 0)
    else:
        info = _read_content_info(content)

    out = {
        'name': get_user_config_name(file_name),
        'file_name': file_name,
        'directory': directory,
        'path': full_path,
        'kind': info.kind,
        'section_count': info.section_count,
        'entry_count': info.entry_count,
        'size': size,
        'is_editable': is_editable,
        'content': content,
    }

    return out

# ################################################################################################################################

def _get_file_list(directory_list:'strlist') -> 'anylist':
    """ Every user configuration file in the directories given, with what each of them holds.
    """
    out:'anylist' = []

    for directory in directory_list:

        # A directory that services read from does not have to exist yet ..
        if not os.path.exists(directory):
            continue

        # .. and everything in one is a file the page lists, whether it reads as user configuration
        # yet or not, the one exception being the environment file, which keeps secrets.
        for file_name in sorted(os.listdir(directory)):

            file_name_lower = file_name.lower()

            if file_name_lower == EnvFile.Default:
                continue

            if file_name.startswith('.'):
                continue

            full_path = os.path.join(directory, file_name)

            if not os.path.isfile(full_path):
                continue

            item = _build_file_item(directory, file_name, full_path)
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _save(request_data:'anydict') -> 'anydict':
    """ Writes the file's contents as the page has them now.
    """
    directory = request_data['directory']
    full_path = _get_full_path(directory, request_data['file_name'])

    os.makedirs(directory, exist_ok=True)

    with open_w(full_path) as opened:
        _ = opened.write(request_data['data'])

    logger.info('Saved user config file %s', full_path)

    out = {'path': full_path}
    return out

# ################################################################################################################################

def _create(request_data:'anydict') -> 'anydict':
    """ Creates a file that was not there before, with the contents that the page starts it with.
    """
    directory = request_data['directory']
    full_path = _get_full_path(directory, request_data['file_name'])

    if os.path.exists(full_path):
        raise Exception(f'File already exists `{full_path}`')

    os.makedirs(directory, exist_ok=True)

    with open_w(full_path) as opened:
        _ = opened.write(request_data['data'])

    logger.info('Created user config file %s', full_path)

    out = {'path': full_path}
    return out

# ################################################################################################################################

def _rename(request_data:'anydict') -> 'anydict':
    """ Gives the file another name in the directory it is in.
    """
    directory = request_data['directory']

    full_path = _get_full_path(directory, request_data['file_name'])
    new_full_path = _get_full_path(directory, request_data['new_file_name'])

    if os.path.exists(new_full_path):
        raise Exception(f'File already exists `{new_full_path}`')

    os.rename(full_path, new_full_path)

    logger.info('Renamed user config file %s to %s', full_path, new_full_path)

    out = {'path': new_full_path}
    return out

# ################################################################################################################################

def _delete(request_data:'anydict') -> 'anydict':
    """ Removes the file from the directory that services read it from.
    """
    full_path = _get_full_path(request_data['directory'], request_data['file_name'])

    if os.path.exists(full_path):
        os.remove(full_path)
        logger.info('Deleted user config file %s', full_path)

    out = {'path': full_path}
    return out

# ################################################################################################################################

# What each action the page takes is carried out by
_action_handler = {
    'save': _save,
    'add': _create,
    'upload': _create,
    'rename': _rename,
    'delete': _delete,
}

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'anydict', is_ok:'bool'=True) -> 'HttpResponse':

    payload = dumps(data).encode('utf-8')
    response_class = HttpResponse if is_ok else HttpResponseServerError

    out = response_class(payload, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The user configuration files that services read through self.config, one of which
    is looked at and edited at a time.
    """
    directory_list = _get_directory_list()
    table_list:'anylist' = []
    error = ''

    try:
        table_list = _get_file_list(directory_list)
    except Exception as e:
        error = str(e)
        logger.error('Config tables: could not read the files: %s', format_exc())

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'table_list_json': dumps(table_list),
        'user_conf_directory': directory_list[0],
        'max_editable_size': _max_editable_size,
        'error': error,
        'zato_clusters': True,
        'zato_template_name': _template_name,
    }

    out = TemplateResponse(req, _template_name, return_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def persist(req:'any_') -> 'HttpResponse':
    """ Carries out one change that the page has made to a file.
    """
    try:
        request_data = loads(req.body.decode('utf-8'))
        action = request_data['action']

        if action not in _action_handler:
            raise Exception(f'Unknown action `{action}`')

        handler = _action_handler[action]
        data = handler(request_data['data'])

        return _json_response({'success': True, 'data': data})

    except Exception as e:
        logger.error('Config tables: %s', format_exc())
        return _json_response({'success': False, 'error': str(e)}, False)

# ################################################################################################################################
# ################################################################################################################################
