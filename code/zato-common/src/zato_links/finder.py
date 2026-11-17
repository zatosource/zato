# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Each Python process of the installation imports this module at startup, which is why, apart from json,
# it imports only the modules that the interpreter has already loaded by then.

# stdlib
import os
import sys
from importlib import import_module
from importlib._abc import Loader
from json import load

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Sequence
    from importlib.machinery import ModuleSpec
    from types import ModuleType
    from zato.common.typing_ import any_, anylist, strlist, strset

    strlistdict     = dict[str, strlist]
    strsequencenone = Sequence[str] | None
    modulenone      = ModuleType | None
    specnone        = ModuleSpec | None

# ################################################################################################################################
# ################################################################################################################################

# The installation that this package is part of, four levels above it
_package_dir      = os.path.dirname(os.path.realpath(__file__))
_installation_dir = os.path.join(_package_dir, os.pardir, os.pardir, os.pardir, os.pardir)
_links_dir        = os.path.join(_installation_dir, 'links')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory with one link file for each repository linked to this installation
    Links_Dir = os.path.normpath(_links_dir)

    # The suffix of the link files
    Link_Suffix = '.json'

    # What separates the module of an extension from the function in it
    Extension_Separator = ':'

# ################################################################################################################################
# ################################################################################################################################

class _ExtendingLoader(Loader):
    """ Executes a module with its own loader, then adds the directories of the linked repositories to it
    if it is a package and runs the extensions of the linked repositories on it.
    """

    def __init__(self, loader:'any_', directories:'strlist', extensions:'strlist') -> 'None':
        self.loader:'Loader' = loader
        self.directories = directories
        self.extensions = extensions

# ################################################################################################################################

    def create_module(self, spec:'ModuleSpec') -> 'modulenone':
        out = self.loader.create_module(spec)
        return out

# ################################################################################################################################

    def exec_module(self, module:'ModuleType') -> 'None':

        # The module is complete before any extension sees it ..
        self.loader.exec_module(module)

        # .. the directories of the linked repositories come after those that the package itself added to its path,
        # so that each package of the installation is found before a directory of the same name in a link ..
        for directory in self.directories:
            if directory not in module.__path__:
                module.__path__.append(directory)

        # .. and each extension receives it in the order the links declare them.
        for extension in self.extensions:
            module_name, _, function_name = extension.partition(ModuleCtx.Extension_Separator)
            extension_module = import_module(module_name)
            extend = getattr(extension_module, function_name)
            extend(module)

# ################################################################################################################################
# ################################################################################################################################

class LinkFinder:
    """ Adds the directories of the linked repositories to the packages of the same names
    and runs the extensions that the linked repositories declare for modules.
    """

    def __init__(self, source_roots:'strlist', top_level_names:'strset', extensions:'strlistdict') -> 'None':
        self.source_roots = source_roots
        self.top_level_names = top_level_names
        self.extensions = extensions

# ################################################################################################################################

    def _find_by_next_finders(self, fullname:'str', path:'strsequencenone', target:'modulenone') -> 'specnone':
        """ Returns the specification that the finders after this one give for a module.
        """
        own_index = sys.meta_path.index(self)
        next_index = own_index + 1
        next_finders = sys.meta_path[next_index:]

        for finder in next_finders:
            if out := finder.find_spec(fullname, path, target):
                break
        else:
            out = None

        return out

# ################################################################################################################################

    def _get_package_directories(self, fullname:'str') -> 'strlist':
        """ Returns the directory of the same package in each linked repository that has one.
        """
        out:'strlist' = []

        relative_path = fullname.replace('.', os.sep)

        for source_root in self.source_roots:
            directory = os.path.join(source_root, relative_path)
            if os.path.isdir(directory):
                out.append(directory)

        return out

# ################################################################################################################################

    def find_spec(self, fullname:'str', path:'strsequencenone', target:'modulenone'=None) -> 'specnone':

        # Our response to produce
        out = None

        top_level_name, _, _ = fullname.partition('.')

        # Only the modules under a top-level package that a link adds to are examined ..
        if top_level_name in self.top_level_names:

            # .. each of them is found by the finders that follow this one ..
            if out := self._find_by_next_finders(fullname, path, target):

                # .. a package receives the directories of the same name from each link ..
                if out.submodule_search_locations is None:
                    directories:'strlist' = []
                else:
                    directories = self._get_package_directories(fullname)

                extensions = self.extensions.get(fullname, [])

                # .. both of which a loader adds once the module is executed.
                if directories or extensions:
                    out.loader = _ExtendingLoader(out.loader, directories, extensions)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _read_links() -> 'anylist':
    """ Returns the links of this installation in the order of the names of their files.
    """
    out:'anylist' = []

    # The links directory is absent when no repository has been linked or when its links were removed ..
    if os.path.isdir(ModuleCtx.Links_Dir):

        file_names = os.listdir(ModuleCtx.Links_Dir)
        file_names.sort()

        # .. and otherwise, each of its link files is one link.
        for file_name in file_names:
            if file_name.endswith(ModuleCtx.Link_Suffix):
                link_path = os.path.join(ModuleCtx.Links_Dir, file_name)

                with open(link_path) as link_file:
                    link = load(link_file)

                out.append(link)

    return out

# ################################################################################################################################

def get_link_directories() -> 'strlist':
    """ Returns the directory of each linked repository, which holds its source roots and the files its targets use,
    e.g. for a container to mount at the same paths.
    """
    out:'strlist' = []

    links = _read_links()

    for link in links:
        out.append(link['repository_dir'])

    return out

# ################################################################################################################################

def _new_finder(links:'anylist') -> 'LinkFinder':
    """ Returns a finder for the source roots and the extensions of all the links.
    """
    source_roots:'strlist' = []
    top_level_names:'strset' = set()
    extensions:'strlistdict' = {}

    for link in links:

        # Each source root adds to the top-level packages it has directories for ..
        for source_root in link['source_roots']:
            source_roots.append(source_root)

            for entry in os.scandir(source_root):
                if entry.is_dir():
                    top_level_names.add(entry.name)

        # .. and each extension is run after the module it extends, which may be one that no source root adds to.
        for module_name, extension in link['extensions'].items():
            module_extensions = extensions.setdefault(module_name, [])
            module_extensions.append(extension)

            top_level_name, _, _ = module_name.partition('.')
            top_level_names.add(top_level_name)

    out = LinkFinder(source_roots, top_level_names, extensions)
    return out

# ################################################################################################################################

def install() -> 'None':
    """ Makes the linked repositories part of the packages of this installation in the current process.
    """
    # The site-packages directory may be processed more than once, e.g. through a lib64 link to it,
    # and a process has one finder however many times its .pth file runs ..
    for finder in sys.meta_path:
        if isinstance(finder, LinkFinder):
            return

    links = _read_links()

    # .. which is installed only if there is anything to link.
    if links:
        finder = _new_finder(links)
        sys.meta_path.insert(0, finder)

# ################################################################################################################################
# ################################################################################################################################
