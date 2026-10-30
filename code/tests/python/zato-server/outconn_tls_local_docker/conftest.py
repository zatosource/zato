# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import sys
import tempfile

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
from local_docker import deploy_service_file, get_bridge_gateway
from zato_container import build_image, remove_container, start_container, wait_until_started
from _outconn_tls import Container_Material_Root, Container_Name, LocalContainer, Service_File_Path, \
    wait_for_tls_material_listener

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def local_container() -> 'any_':
    """ Starts a container that runs the repository through the Docker repository's entrypoint,
    with a host directory of its own mapped to the container's directory of outgoing TLS material,
    deploys the service that invokes the connections, and removes the container and the directory at the end.
    """
    host_material_root = tempfile.mkdtemp(prefix='zato-outconn-tls-')

    build_image()
    start_container(Container_Name, {host_material_root: Container_Material_Root})

    try:
        wait_until_started(Container_Name)

        out = LocalContainer()
        out.name = Container_Name
        out.gateway = get_bridge_gateway(Container_Name)
        out.host_material_root = host_material_root

        wait_for_tls_material_listener(out)
        deploy_service_file(Service_File_Path, Container_Name)

        yield out

    finally:
        remove_container(Container_Name)
        shutil.rmtree(host_material_root, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
