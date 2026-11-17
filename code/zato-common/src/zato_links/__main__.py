# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import sysconfig
from json import dump, load

# Zato
from zato_links.finder import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The file that makes each Python process of this installation read the links when it starts
_pth_name = 'zato_links.pth'
_pth_line = 'import zato_links.finder; zato_links.finder.install()\n'

# The indentation of a stored link file
_link_indent = 4

# The suffix of the makefile through which the Zato Makefile includes the targets of a linked repository
_makefile_suffix = '.mk'

# ################################################################################################################################
# ################################################################################################################################

def add_link(manifest_path:'str') -> 'None':
    """ Links the repository whose manifest is given to this installation.
    """
    with open(manifest_path) as manifest_file:
        manifest = load(manifest_file)

    repository_dir = os.path.dirname(manifest_path)
    repository_dir = os.path.realpath(repository_dir)

    # The manifest has its source roots relative to its own repository ..
    source_roots:'strlist' = []

    for source_root in manifest['source_roots']:
        source_root = os.path.join(repository_dir, source_root)
        source_roots.append(source_root)

    link = {
        'repository_dir': repository_dir,
        'source_roots': source_roots,
        'extensions': manifest['extensions'],
    }

    # .. the link is stored under the name of the repository ..
    os.makedirs(ModuleCtx.Links_Dir, exist_ok=True)

    name = manifest['name']
    link_name = name + ModuleCtx.Link_Suffix
    link_path = os.path.join(ModuleCtx.Links_Dir, link_name)

    with open(link_path, 'w') as link_file:
        dump(link, link_file, indent=_link_indent)

    # .. each Python process of this installation reads it when it starts ..
    site_packages_dir = sysconfig.get_path('purelib')
    pth_path = os.path.join(site_packages_dir, _pth_name)

    with open(pth_path, 'w') as pth_file:
        _ = pth_file.write(_pth_line)

    print(f'Link `{name}` stored in {link_path}')

    # .. and the Zato Makefile includes the targets of a repository that has any.
    if makefile := manifest.get('makefile'):
        makefile = os.path.join(repository_dir, makefile)

        makefile_name = name + _makefile_suffix
        makefile_link_path = os.path.join(ModuleCtx.Links_Dir, makefile_name)

        with open(makefile_link_path, 'w') as makefile_link_file:
            _ = makefile_link_file.write(f'include {makefile}\n')

        print(f'Targets of `{name}` stored in {makefile_link_path}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    manifest_path = sys.argv[1]
    add_link(manifest_path)

# ################################################################################################################################
# ################################################################################################################################
