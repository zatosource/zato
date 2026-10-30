# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

# The local container helpers, the certificate builder with the SOAP endpoint, and the REST endpoint
# are shared with other suites.
_this_directory = os.path.dirname(__file__)
_tests_directory = os.path.abspath(os.path.join(_this_directory, '..', '..'))

sys.path.insert(0, os.path.join(_tests_directory, 'zato-common', 'lib'))
sys.path.insert(0, os.path.join(_tests_directory, 'zato-common', 'soap', 'lib'))
sys.path.insert(0, os.path.join(_tests_directory, 'zato-dashboard', 'playwright_', 'lib'))
sys.path.insert(0, _this_directory)

# local
from local_docker import Container_Name, deploy_service_file, get_bridge_gateway, get_mount_source, is_container_running
from _outconn_tls import Container_Material_Root, LocalContainer, Service_File_Path

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def local_container() -> 'LocalContainer':
    """ Skips the suite when the local Zato container is not running or when no host directory
    is mapped to its directory of outgoing TLS material, otherwise deploys the service that invokes the connections.
    """
    if not is_container_running():
        pytest.skip(f'Container `{Container_Name}` is not running')

    host_material_root = get_mount_source(Container_Material_Root)

    if not host_material_root:
        pytest.skip(f'Container `{Container_Name}` has no host directory mounted at `{Container_Material_Root}`')

    deploy_service_file(Service_File_Path)

    out = LocalContainer()
    out.gateway = get_bridge_gateway()
    out.host_material_root = host_material_root

    return out

# ################################################################################################################################
# ################################################################################################################################
