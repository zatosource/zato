# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from typing import NamedTuple

# Zato
from zato.common.api import EnvFile
from zato.common.user_config import ModuleCtx as UserConfigCtx
from zato.common.util.api import get_user_config_name
from zato.common.util.open_ import open_r, open_w
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_service_name_prefix = 'zato.user-conf.'

# What a file a service reads through self.config is written under. Rule files and enmasse
# files live in the same directories and are not what these services are about.
_suffixes_supported = ('.ini', '.conf')

# A file that keeps a section of this name is a list of the values that are accepted,
# a file without one maps the codes of one party per section to such values.
_codes_section = UserConfigCtx.Codes_Section

_kind_codes = 'codes'
_kind_mappings = 'mappings'

# ################################################################################################################################
# ################################################################################################################################

class ContentInfo(NamedTuple):
    kind: str
    section_count: int
    entry_count: int

# ################################################################################################################################
# ################################################################################################################################

def _read_content_info(content:'str') -> 'ContentInfo':
    """ What a file holds - the kind of file it is, how many sections it has and how many
    values there are under them. A line that reads as neither stops the counting, the same
    way the reader of the file stops at it.
    """
    section_count = 0
    entry_count = 0
    has_codes = False
    has_section = False

    for line in content.splitlines():

        line = line.strip()

        # Empty lines and the file's own notes say nothing about what it holds ..
        if not line:
            continue

        if line.startswith(('#', ';')):
            continue

        # .. a section is what the values under it belong to ..
        if line.startswith('['):

            if not line.endswith(']'):
                break

            name = line[1:-1].strip()
            section_count += 1
            has_section = True

            if name == _codes_section:
                has_codes = True

            continue

        # .. and everything else is a value, which needs both a section above it
        # .. and a sign that says what it maps to.
        if '=' not in line:
            break

        if not has_section:
            break

        entry_count += 1

    if has_codes:
        kind = _kind_codes
    else:
        kind = _kind_mappings

    out = ContentInfo(kind, section_count, entry_count)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _Base(AdminService):
    """ What every one of these services needs - the directories the files live in and
    the one path a name on input is allowed to mean.
    """

    def _get_directory_list(self) -> 'strlist':
        """ Every directory the server reads config files from, each with a trailing separator,
        which is what makes a directory and a file name join into a path by concatenation.
        """
        out:'strlist' = []

        for item in self.server.user_conf_location:
            directory = os.path.abspath(item) + os.sep
            out.append(directory)

        for item in sorted(self.server.user_conf_location_extra):
            directory = os.path.abspath(item) + os.sep
            out.append(directory)

        return out

# ################################################################################################################################

    def _get_full_path(self, directory:'str', file_name:'str') -> 'str':
        """ The file the caller named. A name is a name of a file and nothing else - it names
        no directory of its own, it is written in one of the suffixes these services know, and
        the directory it is in is one of the directories the server itself reported.
        """
        base_name = os.path.basename(file_name)

        if base_name != file_name:
            raise Exception(f'Invalid file name `{file_name}`')

        base_name_lower = base_name.lower()

        if not base_name_lower.endswith(_suffixes_supported):
            raise Exception(f'Invalid file name `{file_name}`')

        directory = os.path.abspath(directory) + os.sep
        directory_list = self._get_directory_list()

        if directory not in directory_list:
            raise Exception(f'Invalid directory `{directory}`')

        out = os.path.join(directory, base_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class GetList(_Base):
    """ Every config file a service reads through self.config, with what each of them holds.
    """
    name = _service_name_prefix + 'get-list'
    input = Int('max_size')

    def handle(self) -> 'None':

        max_size = self.request.input.max_size
        directory_list = self._get_directory_list()

        file_list:'anylist' = []

        for directory in directory_list:

            # A directory the server is told to read may not be there yet ..
            if not os.path.exists(directory):
                continue

            # .. and what is in one may be something other than a config file.
            for file_name in sorted(os.listdir(directory)):

                # What a file is written in is the suffix it goes by, whichever case it is in
                file_name_lower = file_name.lower()

                if not file_name_lower.endswith(_suffixes_supported):
                    continue

                if file_name_lower == EnvFile.Default:
                    continue

                full_path = os.path.join(directory, file_name)

                if not os.path.isfile(full_path):
                    continue

                item = self._build_item(directory, file_name, full_path, max_size)
                file_list.append(item)

        self.response.payload = {
            'directory_list': directory_list,
            'file_list': file_list,
        }

# ################################################################################################################################

    def _build_item(self, directory:'str', file_name:'str', full_path:'str', max_size:'int') -> 'anydict':
        """ One file as the caller reads it. A file larger than the caller works with is
        reported without its contents, since what it says it cannot do anything with anyway.
        """
        size = os.path.getsize(full_path)
        is_editable = size <= max_size

        if is_editable:
            with open_r(full_path) as opened:
                content = opened.read()
        else:
            content = ''

        info = _read_content_info(content)
        config_name = get_user_config_name(file_name)

        out = {
            'name': config_name,
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
# ################################################################################################################################

class Save(_Base):
    """ The file as the caller has it now, written where the server reads it from.
    """
    name = _service_name_prefix + 'save'
    input = 'directory', 'file_name', '-data'

    def handle(self) -> 'None':

        directory = self.request.input.directory
        file_name = self.request.input.file_name
        data = self.request.input.data

        full_path = self._get_full_path(directory, file_name)

        with open_w(full_path) as opened:
            _ = opened.write(data)

        logger.info('Saved user config file %s', full_path)

        self.response.payload = {'path': full_path}

# ################################################################################################################################
# ################################################################################################################################

class Create(_Base):
    """ A file that was not there before, with whatever the caller starts it off with.
    """
    name = _service_name_prefix + 'create'
    input = 'directory', 'file_name', '-data'

    def handle(self) -> 'None':

        directory = self.request.input.directory
        file_name = self.request.input.file_name
        data = self.request.input.data

        full_path = self._get_full_path(directory, file_name)

        if os.path.exists(full_path):
            raise Exception(f'File already exists `{full_path}`')

        with open_w(full_path) as opened:
            _ = opened.write(data)

        logger.info('Created user config file %s', full_path)

        self.response.payload = {'path': full_path}

# ################################################################################################################################
# ################################################################################################################################

class Rename(_Base):
    """ The same file under another name, in the same directory it was in.
    """
    name = _service_name_prefix + 'rename'
    input = 'directory', 'file_name', 'new_file_name'

    def handle(self) -> 'None':

        directory = self.request.input.directory
        file_name = self.request.input.file_name
        new_file_name = self.request.input.new_file_name

        full_path = self._get_full_path(directory, file_name)
        new_full_path = self._get_full_path(directory, new_file_name)

        if os.path.exists(new_full_path):
            raise Exception(f'File already exists `{new_full_path}`')

        os.rename(full_path, new_full_path)

        logger.info('Renamed user config file %s to %s', full_path, new_full_path)

        self.response.payload = {'path': new_full_path}

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Base):
    """ The file, gone from where the server reads it from.
    """
    name = _service_name_prefix + 'delete'
    input = 'directory', 'file_name'

    def handle(self) -> 'None':

        directory = self.request.input.directory
        file_name = self.request.input.file_name

        full_path = self._get_full_path(directory, file_name)

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info('Deleted user config file %s', full_path)

        self.response.payload = {'path': full_path}

# ################################################################################################################################
# ################################################################################################################################
