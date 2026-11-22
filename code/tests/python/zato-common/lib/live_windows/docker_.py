# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from threading import Thread

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

def remove_directory(path:'Path', image:'str') -> 'None':
    """ Removes a directory that holds files a container created as root, through a short-lived container of the same image.
    """
    command = [
        'docker', 'run', '--rm',
        '--entrypoint', 'rm',
        '-v', f'{path.parent}:/parent',
        image,
        '-rf', f'/parent/{path.name}',
    ]

    _ = subprocess.run(command, capture_output=True, check=True)

# ################################################################################################################################

def remove_container(name:'str') -> 'None':
    """ Removes a container, whether it runs or not, and does nothing if there is no such container.
    """
    _ = subprocess.run(['docker', 'rm', '-f', '-v', name], capture_output=True, check=False)

# ################################################################################################################################

def container_is_running(name:'str') -> 'bool':
    result = subprocess.run(
        ['docker', 'inspect', '--format', '{{.State.Running}}', name], capture_output=True, text=True, check=False)

    state = result.stdout.strip()

    out = state == 'true'
    return out

# ################################################################################################################################

def pause_container(name:'str') -> 'None':
    """ Freezes every process of a container, the guest included, until it is unpaused.
    """
    _ = subprocess.run(['docker', 'pause', name], capture_output=True, check=True)

# ################################################################################################################################

def unpause_container(name:'str') -> 'None':
    _ = subprocess.run(['docker', 'unpause', name], capture_output=True, check=True)

# ################################################################################################################################

def published_port(name:'str', container_port:'int') -> 'int':
    """ Returns the host port that Docker published for a TCP port of a container.
    """
    result = subprocess.run(
        ['docker', 'port', name, f'{container_port}/tcp'], capture_output=True, text=True, check=True)

    # The first line is the IPv4 binding, in the form 127.0.0.1:49153
    lines = result.stdout.splitlines()
    first_binding = lines[0]
    port = first_binding.rsplit(':', 1)[1]

    out = int(port)
    return out

# ################################################################################################################################

def _print_lines(process:'subprocess.Popen[str]', prefix:'str') -> 'None':
    stdout = process.stdout
    if stdout:
        for line in stdout:
            line = line.rstrip()
            if line:
                print(f'{prefix} {line}', flush=True)

# ################################################################################################################################

def follow_logs(name:'str', prefix:'str') -> 'subprocess.Popen[str]':
    """ Prints each line of a container's log with a prefix, in a background thread, until the container is gone.
    """
    out = subprocess.Popen(
        ['docker', 'logs', '--follow', name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors='replace',
    )

    thread = Thread(target=_print_lines, args=(out, prefix), daemon=True, name=f'logs-{name}')
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
