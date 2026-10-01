# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from json import loads
from logging import getLogger
from tempfile import NamedTemporaryFile
from traceback import format_exc

# Zato
from zato.common.api import HotDeploy
from zato.common.util.hot_deploy_ import get_project_info, list_changed_project_files, list_project_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hot_deploy_ import HotDeployProject
    from zato.common.typing_ import any_, anydict, intlist, strlist
    from zato.server.base.parallel import ParallelServer
    projectlist = list[HotDeployProject]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Where a server keeps checkouts of repositories that the dashboard connects to
Repos_Dir_Name = 'repo'

# Checkouts this process already knows as projects, and the directories they pick code up from
_projects:'dict[str, projectlist]' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_repo_dir(server:'ParallelServer') -> 'str':
    """ Returns the directory where the dashboard keeps checkouts of repositories for this server.
    """
    out = os.path.join(server.base_dir, Repos_Dir_Name)
    return out

# ################################################################################################################################

def _get_services_deployed(response:'any_') -> 'intlist':
    """ Extracts the IDs of the services deployed out of the response of zato.hot-deploy.create, whatever its shape.
    """
    if hasattr(response, 'getvalue'):
        response = response.getvalue()

    if isinstance(response, (str, bytes)):
        response = loads(response) if response else {}

    if not isinstance(response, dict):
        return []

    response = response.get('zato_hot_deploy_create_response', response)

    out = response.get('services_deployed') or []
    return out

# ################################################################################################################################

def _deploy_code(server:'ParallelServer', path:'str') -> 'strlist':
    """ Hot-deploys one file in place and returns the names of the services it contained.
    """
    response = server.invoke('zato.hot-deploy.create', {'payload_name': path, 'payload': ''}, serialize=False)

    out:'strlist' = []

    for service_id in _get_services_deployed(response):
        out.append(server.service_store.get_service_name_by_id(service_id))

    return out

# ################################################################################################################################

def _deploy_enmasse(server:'ParallelServer', path:'str') -> 'tuple[int, int]':
    """ Imports one enmasse file and returns how many objects it created and updated.
    """
    # Zato
    from zato.server.commands import CommandsFacade

    commands = CommandsFacade()
    commands.init(server)

    with NamedTemporaryFile(prefix='zato-enmasse-result-', suffix='.json', delete=False) as result_file:
        result_path = result_file.name

    try:
        result = commands.run_enmasse_sync_import(path, result_file=result_path)

        if not result.is_ok:
            raise Exception(f'Enmasse import of {path} failed, exit code {result.exit_code}, {result.stderr.strip()}')

        with open(result_path) as f:
            data:'anydict' = loads(f.read() or '{}')

    finally:
        if os.path.exists(result_path):
            os.remove(result_path)

    created = sum(data.get('created', {}).values())
    updated = sum(data.get('updated', {}).values())

    return created, updated

# ################################################################################################################################

def deploy(server:'ParallelServer', path:'str', files:'strlist') -> 'anydict':
    """ Deploys a checkout of a repository - everything in it the first time this process sees it, otherwise only the files
    given, if any - and returns how many services were new or updated, how many enmasse objects were created or updated,
    and what could not be deployed.
    """
    root = os.path.abspath(path)

    if not os.path.isdir(root):
        raise Exception(f'Checkout not found at {root}')

    # A checkout seen for the first time in this process becomes a project - its source directories go to sys.path,
    # the way they would had the server started with it, and everything in it is deployed.
    projects = _projects.get(root)
    is_new = projects is None

    if projects is None:
        projects = get_project_info(root, HotDeploy.Source_Directory) or []

        for project in projects:
            entry = str(project.sys_path_entry)
            if entry not in sys.path:
                sys.path.insert(0, entry)

        _projects[root] = projects

    if is_new:
        py_files, enmasse_files = list_project_files(root, projects)
    else:
        py_files, enmasse_files = list_changed_project_files(root, files, projects)

    known_services = set(server.service_store.name_to_impl_name)

    services_new = 0
    services_updated = 0
    objects_created = 0
    objects_updated = 0
    errors:'strlist' = []

    for item in py_files:
        try:
            for name in _deploy_code(server, item):
                if name in known_services:
                    services_updated += 1
                else:
                    services_new += 1
                    known_services.add(name)
        except Exception as e:
            logger.warning('Could not deploy `%s`, e:`%s`', item, format_exc())
            errors.append(f'{os.path.relpath(item, root)}: {e}')

    for item in enmasse_files:
        try:
            created, updated = _deploy_enmasse(server, item)
            objects_created += created
            objects_updated += updated
        except Exception as e:
            logger.warning('Could not import `%s`, e:`%s`', item, format_exc())
            errors.append(f'{os.path.relpath(item, root)}: {e}')

    out:'anydict' = {
        'services_new':     services_new,
        'services_updated': services_updated,
        'objects_created':  objects_created,
        'objects_updated':  objects_updated,
        'errors':           errors,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
