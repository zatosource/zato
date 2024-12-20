# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.api import HotDeploy
from zato.common.hot_deploy_ import HotDeployProject, pickup_order_patterns
from zato.common.typing_ import cast_
from zato.common.util.env import get_list_from_environment
from zato.common.util.file_system import resolve_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import iterator_, list_, pathlist, strdictdict
    strdictdict = strdictdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_project_info(
    root,          # type: str
    src_dir_name,  # type: str
) -> 'list_[HotDeployProject] | None':

    # Local aliases
    root_path = Path(root)

    # Assume we will not find such a directory
    out:'list_[HotDeployProject]' = []

    # Any potential project directories will go here
    project_dirs:'pathlist' = []

    # Look up the project directories recursively ..
    for item in root_path.rglob(src_dir_name):

        # .. if any is found, append it for later use ..
        project_dirs.append(item)

    # .. now, go through all the project directories found and construct project objects ..
    # .. along with their directories to pick up code from ..
    for item in project_dirs:

        # .. do build the business object ..
        project = HotDeployProject()
        project.pickup_from_path = []

        # .. this is what will be added to sys.path by a starting server ..
        project.sys_path_entry = item

        # .. make use of the default patterns ..
        patterns = pickup_order_patterns[:]

        # .. append any extra patterns found in the environment  ..
        if extra_patterns := get_list_from_environment(HotDeploy.Env.Pickup_Patterns, ','):
            logger.info('Found extra hot-deployment patterns via %s -> %s', HotDeploy.Env.Pickup_Patterns, extra_patterns)
            patterns.extend(extra_patterns)

        # .. look up all the directories to pick up from ..
        for pattern in patterns:

            # .. remove any potential whitespace ..
            pattern = pattern.strip()

            # .. do look them up ..
            pickup_dirs = item.rglob(pattern)

            # .. go over any found ..
            for pickup_dir in pickup_dirs:

                # .. ignore Python's own directories ..
                if '__pycache__' in pickup_dir.parts:
                    continue

                # .. ignore items that are not directories ..
                if not pickup_dir.is_dir():
                    continue

                # .. and add it to the project's list of directories ..
                if not pickup_dir in project.pickup_from_path:
                    project.pickup_from_path.append(pickup_dir)

        # .. we can append the project to our result ..
        out.append(project)

    # .. now, we can return the result to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_pickup_from_items(
    base_dir,      # type: str
    pickup_config, # type: strdictdict
    src_dir_name,  # type: str
) -> 'iterator_[str | list_[HotDeployProject]]':

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
                if project_list := get_project_info(pickup_from, src_dir_name):
                    yield project_list
                else:
                    yield pickup_from

# ################################################################################################################################
# ################################################################################################################################
