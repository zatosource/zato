# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Zato hot-deployment system
==========================

This module provides utilities for Zato's hot-deployment system, which allows services,
models, and configuration files to be deployed to a running Zato server without restart.

Starting the file watcher
-------------------------

To start the file watcher that monitors a directory for changes and hot-deploys files:

    py code/zato-common/src/zato/common/file_transfer/listener.py ~/env/qs-1/server1/pickup/code/impl/src/api/

Or with explicit observer type:

    py code/zato-common/src/zato/common/file_transfer/listener.py ~/env/qs-1/server1/pickup/code/impl/src/api/ --observer inotify

Available observer types:
    - inotify: Linux inotify-based watcher (most efficient on Linux)
    - polling: Cross-platform polling-based watcher (works everywhere but less efficient)
    - auto: Automatically selects the best observer for the platform

Architecture overview
---------------------

The hot-deployment system consists of several components:

1. File watcher (zato/common/file_transfer/listener.py)
   - Uses watchdog library with inotify/polling observers
   - Monitors directories for file changes (created, modified, deleted)
   - Publishes file-ready events to the broker when files are stable
   - Filters files by pattern (*.py, *.yaml, *.yml, *.ini)

2. Broker client (zato/broker/client.py)
   - Connects to RabbitMQ broker
   - Publishes hot-deploy messages to all server processes
   - Message types: HOT_DEPLOY.CREATE_SERVICE, HOT_DEPLOY.UPDATE_ENMASSE, etc.

3. Server worker (zato/server/base/worker/__init__.py)
   - Receives broker messages via on_broker_msg_HOT_DEPLOY_CREATE_SERVICE
   - Invokes zato.hot-deploy.create service to deploy the file

4. Hot-deploy service (zato/server/service/internal/hot_deploy/__init__.py)
   - Backs up current work directory
   - Imports services/models from the file
   - Registers them with the service store

5. Pickup configuration (this module + zato/server/base/parallel/__init__.py)
   - add_pickup_conf_from_code_dir: adds pickup/code/impl/src/api directory
   - add_pickup_conf_from_local_path: adds arbitrary directories to pickup_config
   - extract_pickup_from_items: extracts pickup paths from configuration

Directory structure
-------------------

Default hot-deploy directory structure:

    ~/env/qs-1/server1/
    ├── pickup/
    │   ├── code/
    │   │   └── impl/
    │   │       └── src/
    │   │           └── api/           <- Python services go here
    │   │               ├── my_service.py
    │   │               └── another_service.py
    │   └── incoming/
    │       └── services -> ../code/impl/src/api/  (symlink for backward compatibility)

The symlink is created automatically on server startup by add_pickup_conf_from_code_dir().

Configuration
-------------

Directories to watch are configured via:

1. server.conf [hot_deploy] section:
   pickup_dir = ../../pickup/code/impl/src/api

2. pickup.conf file:
   [hot-deploy.user.my-project]
   pickup_from = /path/to/my/project

3. Environment variables:
   Zato_Hot_Deploy_Dir = /path/to/directory
   Zato_Project_Root = /path/to/project

4. Programmatically via add_pickup_conf_from_local_path()

Flow of a hot-deployed file
---------------------------

1. User saves a .py file to pickup/code/impl/src/api/
2. File watcher detects the change via inotify
3. File watcher waits for file to be stable (no more writes)
4. File watcher calls publish_file() to send message to broker
5. Broker delivers HOT_DEPLOY.CREATE_SERVICE message to all servers
6. Each server's worker calls on_broker_msg_HOT_DEPLOY_CREATE_SERVICE
7. Worker invokes zato.hot-deploy.create service
8. Service imports the module and registers services/models
9. Services are now available for invocation

Debugging
---------

Enable detailed logging by setting environment variable:
    export Zato_Needs_Details=true
"""

# stdlib
import os
from logging import getLogger
from pathlib import Path

# Zato
from zato.common.api import HotDeploy
from zato.common.hot_deploy_ import HotDeployProject, pickup_order_patterns
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool
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

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

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

    if _needs_details:
        logger.info('*' * 60)
        logger.info('Root path %s', root_path)
        logger.info('Src. dir name %s', src_dir_name)
        logger.info('Project dirs %s', project_dirs)

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
            pickup_dirs_list = list(pickup_dirs)

            # .. go over any found ..
            for pickup_dir in pickup_dirs_list:

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
