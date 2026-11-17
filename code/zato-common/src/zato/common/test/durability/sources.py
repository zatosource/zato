# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The source files that the static checks of durability read - every file under version control or not yet added to it,
# without the ignored ones, of this installation and of each repository linked to it.

# stdlib
import os
from dataclasses import dataclass
from functools import cache
from subprocess import check_output

# Zato
from zato_links.finder import get_links, ModuleCtx as LinksModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The installation, which holds the directory of the links
    Installation_Dir = os.path.dirname(LinksModuleCtx.Links_Dir)

    # The suffixes of the files that the checks read
    Python_Suffix = '.py'
    Rust_Suffix   = '.rs'

    Setting_Suffixes = ('.py', '.rs', '.sql', '.yaml', '.yml', '.sh', '.mk', '.toml', '.c', '.conf', '.ini')

    # The names of the files without a suffix that the checks read
    Setting_Names = ('Makefile', 'Dockerfile', 'Dockerfile.apt-base')

    # The package directories of production code in this installation
    Public_Package_Prefix = 'code/zato-'
    Source_Dir_Marker     = '/src/'

    # The package with the support code of the tests, which is not production code even though it sits in a source root
    Test_Support_Marker = '/zato/common/test/'

    # Lists every file that is not ignored, relative to the top of the repository
    Git_List_Command = ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z']

    # What separates the names that git lists
    Git_Separator = '\0'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SourceFile:

    # The full path of the file
    path: str

    # The path relative to the repository it belongs to
    relative_path: str

    # The repository it belongs to
    repository_dir: str

    # Whether the file is production code as opposed to tests and their support code
    is_production: bool

    # Whether the file belongs to a linked repository rather than to the installation
    is_linked: bool

# ################################################################################################################################

    def read(self) -> 'str':
        """ Returns the contents of the file.
        """
        with open(self.path, encoding='utf8', errors='replace') as source_file:
            out = source_file.read()

        return out

# ################################################################################################################################
# ################################################################################################################################

source_file_list = list[SourceFile]

# ################################################################################################################################
# ################################################################################################################################

def _list_repository(repository_dir:'str') -> 'strlist':
    """ Returns the path of each file of a repository that git does not ignore, relative to the repository.
    """
    output = check_output(ModuleCtx.Git_List_Command, cwd=repository_dir)
    output = output.decode('utf8')

    out:'strlist' = []

    for relative_path in output.split(ModuleCtx.Git_Separator):
        if relative_path:
            full_path = os.path.join(repository_dir, relative_path)
            if os.path.isfile(full_path):
                out.append(relative_path)

    return out

# ################################################################################################################################

def _is_public_production(relative_path:'str') -> 'bool':
    """ Returns whether a file of the installation is production code.
    """

    # Our response to produce
    out = False

    if relative_path.startswith(ModuleCtx.Public_Package_Prefix):
        if ModuleCtx.Source_Dir_Marker in relative_path:
            out = ModuleCtx.Test_Support_Marker not in relative_path

    return out

# ################################################################################################################################

def _is_linked_production(full_path:'str', source_roots:'strlist') -> 'bool':
    """ Returns whether a file of a linked repository is production code.
    """
    for source_root in source_roots:
        source_root_prefix = source_root + os.sep
        if full_path.startswith(source_root_prefix):
            out = ModuleCtx.Test_Support_Marker not in full_path
            break
    else:
        out = False

    return out

# ################################################################################################################################

@cache
def get_source_files() -> 'source_file_list':
    """ Returns every file of the installation and of each linked repository that git does not ignore.
    """
    out:'source_file_list' = []

    # The installation itself ..
    for relative_path in _list_repository(ModuleCtx.Installation_Dir):
        item = SourceFile()
        item.path = os.path.join(ModuleCtx.Installation_Dir, relative_path)
        item.relative_path = relative_path
        item.repository_dir = ModuleCtx.Installation_Dir
        item.is_production = _is_public_production(relative_path)
        item.is_linked = False
        out.append(item)

    # .. and each repository linked to it.
    for link in get_links():
        repository_dir = link['repository_dir']
        source_roots = link['source_roots']

        for relative_path in _list_repository(repository_dir):
            full_path = os.path.join(repository_dir, relative_path)

            item = SourceFile()
            item.path = full_path
            item.relative_path = relative_path
            item.repository_dir = repository_dir
            item.is_production = _is_linked_production(full_path, source_roots)
            item.is_linked = True
            out.append(item)

    return out

# ################################################################################################################################

def get_setting_files() -> 'source_file_list':
    """ Returns the files in which a durability setting can be written - code, SQL, configuration and build files.
    """
    out:'source_file_list' = []

    for item in get_source_files():
        file_name = os.path.basename(item.path)

        if file_name.endswith(ModuleCtx.Setting_Suffixes):
            out.append(item)

        elif file_name in ModuleCtx.Setting_Names:
            out.append(item)

    return out

# ################################################################################################################################

def get_python_files(*, is_production:'bool') -> 'source_file_list':
    """ Returns the Python files of production code or of the tests.
    """
    out:'source_file_list' = []

    for item in get_source_files():
        if item.path.endswith(ModuleCtx.Python_Suffix):
            if item.is_production == is_production:
                out.append(item)

    return out

# ################################################################################################################################

def get_rust_files() -> 'source_file_list':
    """ Returns the Rust files of production code.
    """
    out:'source_file_list' = []

    for item in get_source_files():
        if item.path.endswith(ModuleCtx.Rust_Suffix):
            if item.is_production:
                out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
