# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import time

# local
from local_docker import run_command

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The image that the suites run their own containers from
Image_Name = 'zato-test-runtime'

# The directory with the image's definition
_image_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zato_container')

# The repository that the container runs - it is mounted at its own path, which the virtual environment's scripts point to
Repository_Directory = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))

# The Docker repository with the entrypoint and the scripts that it runs
Env_Docker_Repository_Directory = 'Zato_Test_Docker_Repository_Directory'
_default_docker_repository_directory = os.path.abspath(os.path.join(Repository_Directory, '..', '..', 'zato-docker'))

# The files of the Docker repository that the image would contain, by where the entrypoint expects them
_docker_repository_files = {
    'entrypoint.sh': '/entrypoint.sh',
    'generate-cert.sh': '/generate-cert.sh',
    'sslconfig.py': '/sslconfig.py',
    'blocked-paths.txt': '/blocked-paths.txt',
}

# What the entrypoint prints once every component was started
_ready_text = 'Container ready'

# The password of every account in the container
_password = 'zato.test.password'

# How long the image build may take, in seconds
_build_timeout = 1800

# How long the entrypoint may take to start every component, in seconds
Start_Timeout = 300

# How often to read the container's output while it starts, in seconds
_start_poll_interval = 2.0

# ################################################################################################################################
# ################################################################################################################################

def get_docker_repository_directory() -> 'str':
    out = os.environ.get(Env_Docker_Repository_Directory, _default_docker_repository_directory)
    return out

# ################################################################################################################################

def build_image() -> 'None':
    """ Builds the image, which takes only as long as the layers that changed since the previous build.
    """
    _ = run_command([
        'docker', 'build', '--quiet',
        '--tag', Image_Name,
        '--build-arg', f'Zato_Repository_Directory={Repository_Directory}',
        '--build-arg', f'Zato_User_ID={os.getuid()}',
        '--build-arg', f'Zato_Group_ID={os.getgid()}',
        _image_directory,
    ], _build_timeout)

# ################################################################################################################################

def remove_container(container_name:'str') -> 'None':
    """ Removes the container with all its processes, if it exists.
    """
    _ = subprocess.run(['docker', 'rm', '--force', container_name], capture_output=True, text=True)

# ################################################################################################################################

def start_container(container_name:'str', mounts:'strstrdict') -> 'None':
    """ Starts a container that runs the repository through the Docker repository's entrypoint,
    with each host directory of the mounts mapped to the container directory that it names.
    """
    docker_repository_directory = get_docker_repository_directory()

    # A container that a previous run left behind is replaced
    remove_container(container_name)

    command:'strlist' = [
        'docker', 'run', '--detach',
        '--name', container_name,
        '--env', f'Zato_Password={_password}',
        '--volume', f'{Repository_Directory}:{Repository_Directory}:ro',
    ]

    for file_name, container_path in _docker_repository_files.items():
        host_path = os.path.join(docker_repository_directory, file_name)
        command.extend(['--volume', f'{host_path}:{container_path}:ro'])

    for host_directory, container_directory in mounts.items():
        command.extend(['--mount', f'type=bind,source={host_directory},target={container_directory}'])

    command.append(Image_Name)

    _ = run_command(command)

# ################################################################################################################################

def wait_until_started(container_name:'str') -> 'None':
    """ Waits until the entrypoint reports that every component was started,
    and fails with the container's output if the container stops or the time runs out.
    """
    deadline = time.monotonic() + Start_Timeout

    while True:
        result = subprocess.run(['docker', 'logs', container_name], capture_output=True, text=True)
        output = result.stdout + result.stderr

        # Stop as soon as the entrypoint is done ..
        if _ready_text in output:
            return

        # .. or fail if the container is gone ..
        state = run_command(['docker', 'inspect', '-f', '{{.State.Running}}', container_name])
        if state.stdout.strip() != 'true':
            raise Exception(f'Container `{container_name}` stopped while starting, output:\n{output}')

        # .. or if it is taking too long.
        if time.monotonic() >= deadline:
            raise Exception(f'Container `{container_name}` did not start within {Start_Timeout}s, output:\n{output}')

        time.sleep(_start_poll_interval)

# ################################################################################################################################
# ################################################################################################################################
