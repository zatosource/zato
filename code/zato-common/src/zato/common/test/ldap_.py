# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from subprocess import run as subprocess_run
from time import sleep, time
from uuid import uuid4

# ldap3
from ldap3 import Connection as LDAPConnection, Server as LDAPServer

# Zato
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Docker image the directory server runs from
    Image = 'bitnamilegacy/openldap:latest'

    # The port the server listens on inside the container
    Container_Port = 1389

    # The suffix of the directory that the server serves
    Root_DN = 'dc=example,dc=org'

    # Credentials of the directory's administrator
    Admin_Username = 'admin'
    Admin_Password = 'adminpassword'

    # The users that the directory is seeded with
    User_List = 'user01,user02'
    Password_List = 'password01,password02'

    # How long to wait for the server to accept binds, in seconds
    Ready_Timeout = 120.0

    # How long to sleep between bind attempts while waiting for the server, in seconds
    Ready_Sleep_Time = 1.0

    # How long a single readiness bind attempt may take, in seconds
    Ready_Connect_Timeout = 5

# ################################################################################################################################
# ################################################################################################################################

class LDAPTestServer:
    """ Starts an OpenLDAP server in a container on a random port for use in tests.
    """
    def __init__(self) -> 'None':

        # Connection details for clients
        self.host = '127.0.0.1'
        self.port = get_free_port()
        self.root_dn = ModuleCtx.Root_DN
        self.admin_dn = f'cn={ModuleCtx.Admin_Username},{ModuleCtx.Root_DN}'
        self.admin_password = ModuleCtx.Admin_Password

        # The first of the seeded users, which is what tests look up in the directory
        self.username = ModuleCtx.User_List.split(',')[0]

        # Each server runs in a container of its own so that parallel runs never collide
        self.container_name = 'zato-test-ldap-' + uuid4().hex[:8]

# ################################################################################################################################

    def _remove_stale_container(self) -> 'None':
        """ Removes a container left over from a previous, possibly interrupted, run.
        """
        _ = subprocess_run(['docker', 'rm', '-f', self.container_name], capture_output=True, check=False)

# ################################################################################################################################

    def _wait_until_accepting_binds(self) -> 'None':

        # Keep trying until the server accepts binds or we run out of time
        deadline = time() + ModuleCtx.Ready_Timeout
        last_error = ''

        while time() < deadline:

            server = LDAPServer(f'{self.host}:{self.port}', connect_timeout=ModuleCtx.Ready_Connect_Timeout)
            conn = LDAPConnection(server, user=self.admin_dn, password=self.admin_password, raise_exceptions=True)

            try:
                _ = conn.bind()
                _ = conn.unbind()
                return
            except Exception as e:
                last_error = str(e)
                sleep(ModuleCtx.Ready_Sleep_Time)

        # If we are here, the server never came up
        raise Exception(f'LDAP server did not start on {self.host}:{self.port}, last error: {last_error}')

# ################################################################################################################################

    def start(self) -> 'None':

        self._remove_stale_container()

        # The container removes itself when it is stopped ..
        command = [
            'docker', 'run', '-d', '--rm',
            '--name', self.container_name,
            '-e', 'LDAP_ROOT=' + ModuleCtx.Root_DN,
            '-e', 'LDAP_ADMIN_USERNAME=' + ModuleCtx.Admin_Username,
            '-e', 'LDAP_ADMIN_PASSWORD=' + ModuleCtx.Admin_Password,
            '-e', 'LDAP_USERS=' + ModuleCtx.User_List,
            '-e', 'LDAP_PASSWORDS=' + ModuleCtx.Password_List,
            '-p', f'{self.port}:{ModuleCtx.Container_Port}',
            ModuleCtx.Image,
        ]

        # .. and the directory is seeded while it starts, hence the wait below.
        _ = subprocess_run(command, capture_output=True, check=True)

        self._wait_until_accepting_binds()

        logger.info('Test LDAP server started on %s:%s (%s)', self.host, self.port, self.container_name)

# ################################################################################################################################

    def stop(self) -> 'None':

        # Stopping the container also removes it because it was started with --rm
        _ = subprocess_run(['docker', 'stop', self.container_name], capture_output=True, check=False)

        logger.info('Test LDAP server stopped (%s)', self.container_name)

# ################################################################################################################################
# ################################################################################################################################
