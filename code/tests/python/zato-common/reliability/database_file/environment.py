# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the tests of the database file. A server on SQLite with a push subscription to an endpoint
# of the test, a topic published to through REST and an audited REST channel, and the clients of the test.

# stdlib
import hashlib
import json
import os
import shutil
import time
from base64 import b64encode
from http.client import OK
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.test.conftest_base_pubsub import find_free_port, render_template
from zato.common.test.receiver import wait_until_receivers_quiet, WebhookReceiver
from zato.common.test.reliability.power_loss import PowerLossServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The enmasse file and the services of the server
    Template_Path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
    Services_Path = os.path.join(os.path.dirname(__file__), '_services.py')

    # The variable through which zato start receives the directory that the server deploys from each time it starts
    Env_Deploy_From = 'Zato_Deploy_From'

    # The directory that the server deploys from, its directories and the enmasse file of the server
    Deploy_Dir_Name    = 'deploy'
    Deploy_Code_Dir    = 'code'
    Deploy_Enmasse_Dir = 'enmasse'
    Enmasse_File_Name  = 'database-file.yaml'

    # The directory of the database of the server and the directory of what the endpoint of the test received
    Database_Dir_Name = 'database'
    Push_Dir_Name     = 'push-receiver'

    # The names of the passwords and of the port of the endpoint of the test in the placeholders of the enmasse file
    Publisher_Password_Key = 'publisher_password'
    Pusher_Password_Key    = 'pusher_password'
    Push_Port_Key          = 'push_port'

    # The user that publishes
    Publisher_Username = 'test.reliability.database-file.publisher'

    # The paths of the REST interface of the server and of the endpoint of the test
    Publish_Path  = '/pubsub/topic/reliability.database-file'
    Audited_Path  = '/test/reliability/database-file/audited'
    Push_URL_Path = '/webhook/database-file'

    # The log of the server, relative to its directory
    Server_Log_Dir  = 'logs'
    Server_Log_Name = 'server.log'

    # The files that SQLite keeps next to a database in the WAL mode
    Companion_Suffixes = ('-wal', '-shm')

    # How long one request may take, in seconds
    Request_Timeout = 30

    # How often a condition is checked while a test waits for it, in seconds
    Poll_Interval = 0.2

    # How long the server may take to import its definitions after it started, and how long a publication
    # made while it waits may take to reach the endpoint, in seconds
    Ready_Timeout = 120
    Readiness_Delivery_Timeout = 5

    # The correlation ID of the publications made while the test waits for the definitions
    Readiness_Correl_ID = 'readiness'

# ################################################################################################################################
# ################################################################################################################################

class HTTPResult(NamedTuple):
    """ The status code and the parsed body of one HTTP response.
    """
    status_code: 'int'
    body: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

class DatabaseFileEnvironment:
    """ A server on SQLite, the endpoint that it pushes to and the path of the file of its database.
    """

    def __init__(self, name:'str', parent_dir:'str') -> 'None':

        self.parent_dir = parent_dir

        database_dir = os.path.join(parent_dir, ModuleCtx.Database_Dir_Name)
        os.makedirs(database_dir)

        self.db_path = os.path.join(database_dir, DatabaseEnv.File_Name)

        self.placeholders = {
            ModuleCtx.Publisher_Password_Key: 'test.publisher.' + CryptoManager.generate_hex_string(),
            ModuleCtx.Pusher_Password_Key: 'test.pusher.' + CryptoManager.generate_hex_string(),
            ModuleCtx.Push_Port_Key: str(find_free_port()),
        }

        publisher_password = self.placeholders[ModuleCtx.Publisher_Password_Key]
        self.publisher_auth = build_auth(ModuleCtx.Publisher_Username, publisher_password)

        enmasse_yaml = render_template(ModuleCtx.Template_Path, self.placeholders)
        deploy_dir = _create_deploy_dir(parent_dir, enmasse_yaml)

        server_env = {
            DatabaseEnv.Env_Type: DatabaseEnv.Type_SQLite,
            DatabaseEnv.Env_Path: self.db_path,
            ModuleCtx.Env_Deploy_From: deploy_dir,
        }

        # The server imports no definitions before it starts, it imports them from its deployment directory.
        self.server = PowerLossServer(
            name=name,
            parent_dir=parent_dir,
            template_path=os.devnull,
            placeholders=self.placeholders,
            hot_deploy_sources=[],
            database_env=server_env,
        )

        push_port = int(self.placeholders[ModuleCtx.Push_Port_Key])
        push_dir = os.path.join(parent_dir, ModuleCtx.Push_Dir_Name)

        self.receiver = WebhookReceiver(push_port, push_dir, ModuleCtx.Push_URL_Path)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the endpoint of the test, creates the server, starts it and waits until it imported its definitions.
        """
        self.receiver.start()
        self.server.create()
        self.server.start()

        self._wait_for_definitions()

# ################################################################################################################################

    def _wait_for_definitions(self) -> 'None':
        """ Waits until a publication of the server reaches the endpoint of the test and the audited channel answers,
        which the server does once it imported its enmasse file, and leaves the endpoint with nothing received.
        """
        deadline = time.monotonic() + ModuleCtx.Ready_Timeout

        # The publications that precede the import are refused, and those that precede the subscription are not pushed ..
        while True:
            result = self.publish(ModuleCtx.Readiness_Correl_ID)

            if result.status_code == OK:
                delivered = self.receiver.wait_for_delivery(1, ModuleCtx.Readiness_Delivery_Timeout)

                if delivered:
                    break

            if time.monotonic() > deadline:
                raise Exception(f'No publication reached the endpoint within {ModuleCtx.Ready_Timeout}s')

            time.sleep(ModuleCtx.Poll_Interval)

        # .. the pushes of the publications made in the meantime arrive before the endpoint is cleared ..
        wait_until_receivers_quiet([self.receiver])
        self.receiver.clear_output()

        # .. and the audited channel answers too.
        def is_channel_ready() -> 'bool':
            result = self.call_audited()
            out = result.status_code == OK
            return out

        wait_until(is_channel_ready, ModuleCtx.Ready_Timeout, 'the audited channel')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and the endpoint of the test and removes the environment of the server.
        """
        self.server.remove()
        self.receiver.stop()

# ################################################################################################################################

    def publish(self, correl_id:'str') -> 'HTTPResult':
        """ Publishes one message through REST and returns the response of the server.
        """
        url = self.server.base_url + ModuleCtx.Publish_Path

        payload = {
            'data': {'correl_id': correl_id},
            'correl_id': correl_id,
        }

        out = post_json(url, self.publisher_auth, payload)
        return out

# ################################################################################################################################

    def call_audited(self) -> 'HTTPResult':
        """ Invokes the audited REST channel and returns the response of the server.
        """
        url = self.server.base_url + ModuleCtx.Audited_Path

        out = post_json(url, self.publisher_auth, {})
        return out

# ################################################################################################################################

    def remove_database(self) -> 'None':
        """ Removes the file of the database together with the files that SQLite keeps next to it,
        as a restore script or a remount of a volume does.
        """
        os.remove(self.db_path)

        for suffix in ModuleCtx.Companion_Suffixes:
            companion_path = self.db_path + suffix

            if os.path.exists(companion_path):
                os.remove(companion_path)

# ################################################################################################################################

    def count_log_lines(self, text:'str') -> 'int':
        """ Returns how many lines of the log of the server contain a text.
        """
        log_path = os.path.join(self.server.server_directory, ModuleCtx.Server_Log_Dir, ModuleCtx.Server_Log_Name)

        out = 0

        with open(log_path) as log_file:
            for line in log_file:
                if text in line:
                    out += 1

        return out

# ################################################################################################################################
# ################################################################################################################################

def _create_deploy_dir(parent_dir:'str', enmasse_yaml:'str') -> 'str':
    """ Creates the directory that the server deploys from each time it starts - its services in the code directory
    and its enmasse file in the enmasse directory, which the server imports once the services are deployed.
    """
    out = os.path.join(parent_dir, ModuleCtx.Deploy_Dir_Name)

    code_dir = os.path.join(out, ModuleCtx.Deploy_Code_Dir)
    enmasse_dir = os.path.join(out, ModuleCtx.Deploy_Enmasse_Dir)

    os.makedirs(code_dir)
    os.makedirs(enmasse_dir)

    _ = shutil.copy2(ModuleCtx.Services_Path, code_dir)

    enmasse_path = os.path.join(enmasse_dir, ModuleCtx.Enmasse_File_Name)

    with open(enmasse_path, 'w') as enmasse_file:
        _ = enmasse_file.write(enmasse_yaml)

    return out

# ################################################################################################################################

def build_auth(username:'str', password:'str') -> 'str':
    """ Returns the value of the Authorization header of Basic Auth.
    """
    credentials = f'{username}:{password}'
    credentials = credentials.encode()
    credentials = b64encode(credentials)

    out = 'Basic ' + credentials.decode()
    return out

# ################################################################################################################################

def post_json(url:'str', auth:'str', payload:'any_') -> 'HTTPResult':
    """ Sends one request with Basic Auth and returns its status code and its parsed body.
    """
    serialized = json.dumps(payload)
    body = serialized.encode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', auth)
    request.add_header('Content-Type', 'application/json')

    # An error status is read in the same way as a success ..
    try:
        with urlopen(request, timeout=ModuleCtx.Request_Timeout) as response:
            response_data = response.read()
            status_code = response.status
    except HTTPError as error:
        response_data = error.read()
        status_code = error.code

    # .. and an empty body parses to an empty dict.
    if response_data:
        response_body = json.loads(response_data)
    else:
        response_body = {}

    out = HTTPResult(status_code, response_body)
    return out

# ################################################################################################################################

def get_digest(path:'str') -> 'str':
    """ Returns the SHA-256 digest of the content of a file.
    """
    with open(path, 'rb') as input_file:
        data = input_file.read()

    content_hash = hashlib.sha256(data)

    out = content_hash.hexdigest()
    return out

# ################################################################################################################################

def wait_until(condition:'any_', timeout:'float', description:'str') -> 'None':
    """ Waits until a condition holds, failing once the timeout passes.
    """
    deadline = time.monotonic() + timeout

    while not condition():
        if time.monotonic() > deadline:
            raise Exception(f'Timed out after {timeout}s waiting for {description}')
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
