# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from time import sleep, time

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The counterparty image, built from the upstream repository at a pinned release tag - never latest.
    Image = 'zato-openas2:4.8.3'
    Build_Context = 'https://github.com/OpenAS2/OpenAs2App.git#v4.8.3'

    # The name the container runs under so a stale one can be removed.
    Container_Name = 'zato-as2-interop-openas2'

    # Paths inside the container - the image keeps a pristine configuration template
    # beside the live configuration directory its entrypoint would populate from it.
    Config_Dir          = '/opt/openas2/config'
    Config_Template_Dir = '/opt/openas2/config_template'
    Data_Dir            = '/opt/openas2/data'

    # The AS2 receiver port inside the container and the host port it is published on.
    Receiver_Port      = 10080
    Host_Receiver_Port = 25080

    # The log line that says the whole server, its receiver included, is up.
    Started_Marker = 'OpenAS2 Server v4.8.3 started'

    # The name under which the container reaches listeners running on the host.
    Host_Alias = 'host.docker.internal'

    # How long to wait for the receiver to accept connections and how long to sleep between attempts.
    Ready_Timeout = 180
    Ready_Sleep   = 1

# ################################################################################################################################
# ################################################################################################################################

def is_docker_available() -> 'bool':
    """ Tells whether a working docker daemon can be reached - the suite skips itself when it cannot.
    """
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, check=False)
    except OSError:
        out = False
    else:
        out = result.returncode == 0

    return out

# ################################################################################################################################

def ensure_image() -> 'None':
    """ Builds the counterparty image from the pinned upstream tag unless it is already present locally.
    """
    result = subprocess.run(['docker', 'image', 'inspect', ModuleCtx.Image], capture_output=True, check=False)

    # The image is already there, nothing to build.
    if result.returncode == 0:
        return

    # The first build compiles the counterparty from source inside docker, which takes a while.
    build = subprocess.run(['docker', 'build', '-t', ModuleCtx.Image, ModuleCtx.Build_Context],
        capture_output=True, check=False)

    if build.returncode != 0:
        stderr = build.stderr.decode('utf-8')
        raise Exception(f'Could not build {ModuleCtx.Image}: {stderr}')

# ################################################################################################################################

def extract_config_template(target_dir:'str') -> 'None':
    """ Copies the image's pristine configuration template into the given host directory,
    so the suite runs with exactly the configuration upstream ships, overriding only
    the partnerships and the keystore.
    """
    temp_name = ModuleCtx.Container_Name + '-template'

    # A leftover from an interrupted run must never break the copy ..
    _ = subprocess.run(['docker', 'rm', '-f', temp_name], capture_output=True, check=False)

    # .. a stopped container is enough to read files out of the image ..
    _ = subprocess.run(['docker', 'create', '--name', temp_name, ModuleCtx.Image], capture_output=True, check=True)

    # .. copy the template's contents, not the directory itself ..
    source = f'{temp_name}:{ModuleCtx.Config_Template_Dir}/.'
    _ = subprocess.run(['docker', 'cp', source, target_dir], capture_output=True, check=True)

    # .. and the temporary container has served its purpose.
    _ = subprocess.run(['docker', 'rm', temp_name], capture_output=True, check=False)

# ################################################################################################################################

def start_openas2(config_dir:'str', data_dir:'str') -> 'None':
    """ Starts the counterparty with the given configuration and storage directories mounted in,
    then waits until its AS2 receiver accepts connections.
    """

    # A container left over from a previous, possibly interrupted, run has to go first.
    _ = subprocess.run(['docker', 'rm', '-f', ModuleCtx.Container_Name], capture_output=True, check=False)

    command = [
        'docker', 'run', '-d', '--rm',
        '--name', ModuleCtx.Container_Name,

        # The container must be able to reach our own inbound listener on the host.
        '--add-host', f'{ModuleCtx.Host_Alias}:host-gateway',

        # The entrypoint probes the terminal for colors, which needs a defined terminal type.
        '-e', 'TERM=dumb',

        '-p', f'{ModuleCtx.Host_Receiver_Port}:{ModuleCtx.Receiver_Port}',
        '-v', f'{config_dir}:{ModuleCtx.Config_Dir}',
        '-v', f'{data_dir}:{ModuleCtx.Data_Dir}',
        ModuleCtx.Image,
    ]

    _ = subprocess.run(command, capture_output=True, check=True)

    _wait_for_receiver()

# ################################################################################################################################

def stop_openas2() -> 'None':
    """ Stops the counterparty - the container removes itself because it was started with --rm.
    """
    _ = subprocess.run(['docker', 'stop', ModuleCtx.Container_Name], capture_output=True, check=False)

# ################################################################################################################################

def restore_ownership(directory:'str') -> 'None':
    """ Hands files the container created as root back to the invoking user, so the suite
    can remove its temporary directories without elevated privileges.
    """
    uid = os.getuid()
    gid = os.getgid()

    ownership = f'{uid}:{gid}'
    mount = f'{directory}:/restore'

    command = ['docker', 'run', '--rm', '--entrypoint', 'chown', '-v', mount, ModuleCtx.Image, '-R', ownership, '/restore']
    _ = subprocess.run(command, capture_output=True, check=False)

# ################################################################################################################################

def _read_container_logs() -> 'str':
    """ Returns everything the container has logged so far.
    """
    logs = subprocess.run(['docker', 'logs', ModuleCtx.Container_Name], capture_output=True, check=False)

    out = logs.stdout.decode('utf-8') + logs.stderr.decode('utf-8')
    return out

# ################################################################################################################################

def _wait_for_receiver() -> 'None':
    """ Waits until the counterparty logs that it has fully started - a TCP probe against
    the published port would only reach docker's own proxy, which accepts connections
    long before the receiver inside the container binds its socket.
    """
    deadline = time() + ModuleCtx.Ready_Timeout

    while time() < deadline:
        output = _read_container_logs()
        if ModuleCtx.Started_Marker in output:
            return
        sleep(ModuleCtx.Ready_Sleep)

    # The receiver never came up - the container logs say why.
    output = _read_container_logs()
    raise Exception(f'The AS2 receiver did not come up on port {ModuleCtx.Host_Receiver_Port}, container logs: {output}')

# ################################################################################################################################
# ################################################################################################################################
