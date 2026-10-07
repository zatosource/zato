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
from pathlib import Path

_this_directory = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))

# pytest
import pytest  # noqa: E402

# redis
from redis import Redis  # noqa: E402

# Zato
from zato.common.api import OpenAPI_Console_Auth  # noqa: E402
from zato.openapi.console.client import OpenAPIConsoleClient  # noqa: E402

# Live environment
from live_environment.parts import Parts, tear_down  # noqa: E402
from live_environment.quickstart import find_free_port, Host, ZatoEnvironment  # noqa: E402
from live_kafka.bridge import start_redis  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, iterator_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The services the channels under test route to, deployed by the server at startup from the hot-deployment directory
    Services_File = Path(_this_directory) / '_services.py'
    Services_File_Name = 'api_cases.py'

    # The channels the console documents, created the way a user creates them
    Channels_File = Path(_this_directory) / 'channels.yaml'

    # The Dashboard user the console is signed into with - the console's admin, who receives the complete document
    Admin_Username = 'admin'

    # How many replies are waited for before the server is declared silent - each wait is the client's own reply timeout
    Document_Attempts = 6

    # What the server is told where to find the suite's Redis and the services to deploy at startup
    Hot_Deploy_Variable = 'Zato_Hot_Deploy_Dir'
    Queue_Bridge_Redis_Port_Variable = 'Zato_Queue_Bridge_Redis_Port'
    Log_Deployed_Services_Variable = 'Zato_Log_User_Services_Deployed'

# ################################################################################################################################
# ################################################################################################################################

class ConsoleSuite:
    """ One Redis and one Zato server, with the suite's services deployed at startup and their channels in the ODB,
    and a console client that asks the server for the OpenAPI document the way the console does.
    """

    def __init__(self, zato:'ZatoEnvironment', redis_port:'int', environment:'strstrdict') -> 'None':
        self.zato = zato
        self.redis_port = redis_port
        self.environment = environment
        self.server_log_path = os.path.join(zato.server_directory, 'logs', 'server.log')

        self.auth = {
            'auth_type': OpenAPI_Console_Auth.Type_Credentials,
            'username': ModuleCtx.Admin_Username,
            'password': zato.password,
        }

# ################################################################################################################################

    def get_document(self) -> 'anydict':
        """ Asks the server for the complete document as the Dashboard admin. A server whose listener is not up yet
        answers nothing, hence the attempts.
        """
        redis_conn = Redis(host=Host, port=self.redis_port, decode_responses=True)
        client = OpenAPIConsoleClient(redis_conn)

        for attempt in range(1, ModuleCtx.Document_Attempts + 1):
            out = client.get_spec(self.auth)

            if out is not None:
                break

            print(f'[CONSOLE] No document after attempt {attempt}')

        else:
            raise Exception(f'No OpenAPI document arrived from the server within {ModuleCtx.Document_Attempts} attempts')

        paths = out['paths']
        print(f'[CONSOLE] Document has {len(paths)} paths')

        for path in sorted(paths):
            methods = sorted(paths[path])
            print(f'[CONSOLE] {path} -> {methods}')

        return out

# ################################################################################################################################

    def restart(self) -> 'None':
        """ Restarts the server with everything it had on disk and in the ODB, the same way a container restart does.
        """
        self.zato.restart(self.environment)

# ################################################################################################################################

    def import_channels(self, file_name:'str', definitions:'str') -> 'None':
        """ Imports channel definitions into the running server with enmasse, which writes them to the ODB
        and asks the server to reload its configuration, without any hot-deployment taking place.
        """
        _ = self.zato.import_yaml(file_name, definitions)

# ################################################################################################################################

    def server_log_lines(self, needle:'str') -> 'strlist':
        """ The lines of the server log that contain the given text, printed so a failing run can be read back.
        """
        out:'strlist' = []

        with open(self.server_log_path) as log_file:
            for line in log_file:
                if needle in line:
                    line = line.rstrip()
                    out.append(line)
                    print(f'[SERVER.LOG] {line}')

        return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def console_suite() -> 'iterator_':
    """ One Redis and one Zato server for the whole session. The services are deployed from a hot-deployment
    directory at startup and the channels are imported once the server is up.
    """
    parts = Parts()

    try:
        # .. Redis, which the server and the console client exchange commands through ..
        redis_port = find_free_port()
        redis_process = start_redis(redis_port)
        parts.add('redis-server', redis_process.kill)

        # .. the server pointed at that Redis ..
        directory = tempfile.mkdtemp(prefix='zato_openapi_console_live_')
        zato = ZatoEnvironment(directory, password_prefix='test.openapi.console')
        parts.add('zato environment', zato.stop)
        zato.create(redis_port=redis_port)

        # .. the services go where the server deploys them from at startup ..
        hot_deploy_directory = os.path.join(directory, 'hot-deploy', 'services')
        os.makedirs(hot_deploy_directory)
        _ = shutil.copy(ModuleCtx.Services_File, os.path.join(hot_deploy_directory, ModuleCtx.Services_File_Name))

        environment = {
            ModuleCtx.Hot_Deploy_Variable: hot_deploy_directory,
            ModuleCtx.Queue_Bridge_Redis_Port_Variable: str(redis_port),
            ModuleCtx.Log_Deployed_Services_Variable: 'True',
        }

        zato.start(environment)

        # .. and the channels are created the way a user creates them.
        _ = zato.import_yaml(ModuleCtx.Channels_File.name, ModuleCtx.Channels_File.read_text())

        suite = ConsoleSuite(zato, redis_port, environment)

        yield suite

    finally:
        tear_down(parts)

# ################################################################################################################################
# ################################################################################################################################
