# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path

# Zato
from zato.common.api import HotDeploy
from zato.common.hot_deploy_ import HotDeployProject
from zato.common.typing_ import cast_
from zato.common.util.file_system import resolve_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import iterator_, list_, strdictdict

# ################################################################################################################################
# ################################################################################################################################

def get_project_info(
    root,          # type: str
    src_dir_name,  # type: str
    max_levels=10, # type: int
) -> 'HotDeployProject | None':

    # Visit up to max_levels of the root directory,
    # trying to find a directory that holds the source code of a project / services.

    # Local aliases
    root_path = Path(root)

    # Assume we will not find such a directory
    out = None

    # Any potential project directories will go here
    project_dirs:'list_[Path]' = []

    # Look up the project directories recursively ..
    for item in root_path.rglob(src_dir_name):

        # .. if any is found, append it for later use ..
        project_dirs.append(item)

    print()
    print(111, project_dirs)
    print()

    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_pickup_from_items(
    base_dir,      # type: str
    pickup_config, # type: strdictdict
    src_dir_name,  # type: str
) -> 'iterator_[str | HotDeployProject]':

    # Go through each piece of the hot-deployment configuration ..
    for key, value in pickup_config.items(): # type: ignore

        # .. we handle only specific keys ..
        if key.startswith(HotDeploy.UserPrefix):

            # .. proceed only if we know where to pick up from ..
            if pickup_from := value.get('pickup_from'): # type: ignore

                # .. type hints ..
                pickup_from = cast_('str', pickup_from)

                # .. this will resolve home directories and environment variables ..
                pickup_from = resolve_path(pickup_from, base_dir)

                # .. check if this path points to a project ..
                if project := get_project_info(pickup_from, src_dir_name):

                    print()
                    print(111, project)
                    print()

                yield pickup_from

# ################################################################################################################################
# ################################################################################################################################
