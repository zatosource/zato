# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The name of the local container that the local Docker suites run against
Container_Name = 'zato-4.1'

# Where the quickstart environment is installed inside the container
Server_Directory = '/opt/zato/env/qs-1/server1'
Zato_Binary = '/opt/zato/current/bin/zato'

# Where hot-deployed services are picked up inside the container
Pickup_Directory = f'{Server_Directory}/pickup/incoming/services'

# The server's main log inside the container
Server_Log_Path = f'{Server_Directory}/logs/server.log'

# How long one docker command may take by default, in seconds
Docker_Timeout = 120

# How often to read the server's log while waiting for a line to appear, in seconds
_log_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def run_command(command:'strlist', timeout:'float'=Docker_Timeout) -> 'subprocess.CompletedProcess':
    """ Runs one host command, raising with the full output when it fails.
    """
    out = subprocess.run(command, capture_output=True, text=True, timeout=timeout)

    if out.returncode != 0:
        raise Exception(
            f'Command failed (exit {out.returncode}): {command}\nstdout: {out.stdout}\nstderr: {out.stderr}')

    return out

# ################################################################################################################################

def is_container_running(container_name:'str'=Container_Name) -> 'bool':
    """ Tells whether the local Zato container exists and is running.
    """
    try:
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{.State.Running}}', container_name],
            capture_output=True, text=True, timeout=Docker_Timeout,
        )
    except FileNotFoundError:
        return False

    if result.returncode != 0:
        return False

    out = result.stdout.strip() == 'true'
    return out

# ################################################################################################################################

def get_bridge_gateway(container_name:'str'=Container_Name) -> 'str':
    """ Returns the docker bridge gateway address - the container reaches host ports through it.
    """
    result = run_command(
        ['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}', container_name])

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def import_enmasse(
    yaml_text:'str',
    file_prefix:'str',
    timeout:'float'=Docker_Timeout,
    container_name:'str'=Container_Name,
    ) -> 'None':
    """ Imports the given enmasse YAML into the container's server.
    """
    host_yaml_path = os.path.join(tempfile.gettempdir(), f'{file_prefix}-{os.getpid()}.yaml')
    container_yaml_path = f'/tmp/{file_prefix}.yaml'

    with open(host_yaml_path, 'w') as yaml_file:
        _ = yaml_file.write(yaml_text)

    try:
        _ = run_command(['docker', 'cp', host_yaml_path, f'{container_name}:{container_yaml_path}'], timeout)
        _ = run_command(['docker', 'exec', container_name,
            Zato_Binary, 'enmasse', Server_Directory, '--verbose', '--import', '--input', container_yaml_path], timeout)
        _ = run_command(['docker', 'exec', container_name, 'rm', container_yaml_path], timeout)

    finally:
        os.remove(host_yaml_path)

# ################################################################################################################################

def deploy_service_file(service_path:'str', container_name:'str'=Container_Name) -> 'None':
    """ Copies a service file into the container's hot-deployment directory.
    """
    file_name = os.path.basename(service_path)
    _ = run_command(['docker', 'cp', service_path, f'{container_name}:{Pickup_Directory}/{file_name}'])

# ################################################################################################################################

def invoke_service(
    service_name:'str',
    payload:'str',
    timeout:'float'=Docker_Timeout,
    container_name:'str'=Container_Name,
    ) -> 'str':
    """ Invokes a service in the container's server and returns everything the command printed,
    without raising, so that callers may retry while the service is still being deployed.
    """
    result = subprocess.run(
        ['docker', 'exec', container_name, Zato_Binary, 'service', 'invoke', Server_Directory, service_name,
            '--payload', payload],
        capture_output=True, text=True, timeout=timeout,
    )

    out = result.stdout + result.stderr
    return out

# ################################################################################################################################

def get_server_log_size(container_name:'str'=Container_Name) -> 'int':
    """ Returns the current size of the server's log, in bytes, so that later reads cover only what follows.
    """
    result = run_command(['docker', 'exec', container_name, 'stat', '-c', '%s', Server_Log_Path])

    out = int(result.stdout.strip())
    return out

# ################################################################################################################################

def read_server_log(offset:'int', container_name:'str'=Container_Name) -> 'str':
    """ Returns what the server's log holds from the given byte offset onwards.
    """
    start_position = offset + 1
    result = run_command(['docker', 'exec', container_name, 'tail', '-c', f'+{start_position}', Server_Log_Path])

    out = result.stdout
    return out

# ################################################################################################################################

def wait_for_server_log(text:'str', offset:'int', timeout:'float', container_name:'str'=Container_Name) -> 'str':
    """ Waits until the server's log, read from the given byte offset, contains the given text,
    and returns what was read.
    """
    deadline = time.monotonic() + timeout

    while True:
        log_text = read_server_log(offset, container_name)

        # Stop as soon as the text is there ..
        if text in log_text:
            return log_text

        # .. or fail with what was read once the deadline passes.
        if time.monotonic() >= deadline:
            raise Exception(f'`{text}` not found in {Server_Log_Path} within {timeout}s, read:\n{log_text}')

        time.sleep(_log_poll_interval)

# ################################################################################################################################
# ################################################################################################################################
