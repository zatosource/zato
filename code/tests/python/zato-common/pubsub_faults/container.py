# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The controls that the fault suites apply to one test container - the files of its cgroup, its network namespace
# and its processes. The cgroup files are owned by root, so they are written by a short-lived helper container
# that mounts the cgroup tree, and the network namespace is changed by a helper container that joins it.

# stdlib
import os
import subprocess

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Where the cgroups of the containers are, on the host and inside the helper container that writes to them.
_host_cgroup_root   = '/sys/fs/cgroup/system.slice'
_helper_cgroup_root = '/host-cgroup/system.slice'

# The image of the helper that writes to the cgroup files.
_helper_image = 'alpine:latest'

# The image of the helper that runs tc in the network namespace of a container, built when first needed.
_tc_image = 'zato-pubsub-test-tc:1'
_tc_dockerfile = 'FROM alpine:latest\nRUN apk add --no-cache iproute2-tc iproute2-minimal\n'

# The block devices of the host as the kernel lists them.
_sys_block_root = '/sys/dev/block'

# ################################################################################################################################
# ################################################################################################################################

def run_command(command:'strlist') -> 'str':
    """ Runs a command to its end and returns what it printed, raising an exception if it failed.
    """
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        raise Exception(f'Command {command} failed with {result.returncode}: {result.stderr.strip()}')

    out = result.stdout
    return out

# ################################################################################################################################

def get_disk_device(path:'str') -> 'str':
    """ Returns the major and minor numbers of the whole disk that holds a path, as io.max expects them.
    """
    device = os.stat(path).st_dev
    device_id = f'{os.major(device)}:{os.minor(device)}'

    # A partition is listed next to the file with the numbers of its disk, one directory up ..
    device_dir = os.path.realpath(os.path.join(_sys_block_root, device_id))

    if os.path.exists(os.path.join(device_dir, 'partition')):
        disk_dir = os.path.dirname(device_dir)
        with open(os.path.join(disk_dir, 'dev')) as dev_file:
            out = dev_file.read().strip()

    # .. whereas a whole disk is listed under its own numbers.
    else:
        out = device_id

    return out

# ################################################################################################################################

def ensure_tc_image() -> 'None':
    """ Builds the image with tc unless it exists already.
    """
    result = subprocess.run(['docker', 'image', 'inspect', _tc_image], capture_output=True, check=False)

    if result.returncode != 0:
        _ = subprocess.run(['docker', 'build', '-t', _tc_image, '-'], input=_tc_dockerfile.encode('utf8'),
            capture_output=True, check=True)

# ################################################################################################################################
# ################################################################################################################################

class Container:
    """ One test container, with the files of its cgroup, its network namespace and its processes.
    """

    def __init__(self, name:'str') -> 'None':
        self.name = name
        self.container_id = run_command(['docker', 'inspect', '-f', '{{.Id}}', name]).strip()
        self.host_pid = int(run_command(['docker', 'inspect', '-f', '{{.State.Pid}}', name]).strip())

        scope_name = f'docker-{self.container_id}.scope'

        self.cgroup_dir = os.path.join(_host_cgroup_root, scope_name)
        self.helper_cgroup_dir = os.path.join(_helper_cgroup_root, scope_name)

# ################################################################################################################################

    def read_cgroup(self, file_name:'str') -> 'str':
        with open(os.path.join(self.cgroup_dir, file_name)) as cgroup_file:
            out = cgroup_file.read()
        return out

# ################################################################################################################################

    def write_cgroup(self, file_name:'str', value:'str') -> 'None':
        path = os.path.join(self.helper_cgroup_dir, file_name)
        script = f"echo '{value}' > {path}"

        _ = run_command(['docker', 'run', '--rm', '--privileged', '-v', '/sys/fs/cgroup:/host-cgroup',
            _helper_image, 'sh', '-c', script])

# ################################################################################################################################

    def read_io_stat(self, device:'str') -> 'strintdict':
        """ Returns the bytes and operations that the container read and wrote on one device so far.
        """
        out:'strintdict' = {'rbytes': 0, 'wbytes': 0, 'rios': 0, 'wios': 0}

        for line in self.read_cgroup('io.stat').splitlines():
            fields = line.split()
            if fields[0] == device:
                for item in fields[1:]:
                    name, _, value = item.partition('=')
                    if name in out:
                        out[name] = int(value)

        return out

# ################################################################################################################################

    def read_cpu_usage_usec(self) -> 'int':
        """ Returns the CPU time that the container used so far, in microseconds.
        """
        for line in self.read_cgroup('cpu.stat').splitlines():
            name, value = line.split()
            if name == 'usage_usec':
                out = int(value)
                return out

        # .. a cgroup with the cpu controller always reports its usage.
        else:
            raise Exception(f'No usage_usec in cpu.stat of {self.name}')

# ################################################################################################################################

    def read_memory_current(self) -> 'int':
        out = int(self.read_cgroup('memory.current'))
        return out

# ################################################################################################################################

    def read_oom_kills(self) -> 'int':
        """ Returns how many processes of the container the OOM killer ended so far.
        """
        for line in self.read_cgroup('memory.events').splitlines():
            name, value = line.split()
            if name == 'oom_kill':
                out = int(value)
                return out

        # .. a cgroup with the memory controller always reports its events.
        else:
            raise Exception(f'No oom_kill in memory.events of {self.name}')

# ################################################################################################################################

    def protect_from_oom_killer(self) -> 'None':
        """ Keeps the main process of the container out of the choice of the OOM killer, so that it ends
        one of the processes that the main process started.
        """
        script = f'echo -1000 > /proc/{self.host_pid}/oom_score_adj'
        _ = run_command(['docker', 'run', '--rm', '--privileged', '--pid', 'host', _helper_image, 'sh', '-c', script])

# ################################################################################################################################

    def run_tc(self, script:'str') -> 'str':
        """ Runs a shell script with tc and ip in the network namespace of the container.
        """
        ensure_tc_image()

        out = run_command(['docker', 'run', '--rm', '--net', f'container:{self.name}', '--cap-add', 'NET_ADMIN',
            _tc_image, 'sh', '-c', script])

        return out

# ################################################################################################################################

    def execute(self, script:'str') -> 'str':
        """ Runs a shell script inside the container.
        """
        out = run_command(['docker', 'exec', self.name, 'sh', '-c', script])
        return out

# ################################################################################################################################

    def start_script(self, script:'str') -> 'subprocess.Popen[bytes]':
        """ Starts a shell script inside the container without waiting for it to complete.
        """
        out = subprocess.Popen(['docker', 'exec', self.name, 'sh', '-c', script],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out

# ################################################################################################################################

    def pause(self) -> 'None':
        _ = run_command(['docker', 'pause', self.name])

# ################################################################################################################################

    def unpause(self) -> 'None':
        _ = run_command(['docker', 'unpause', self.name])

# ################################################################################################################################

    def is_paused(self) -> 'bool':
        state = run_command(['docker', 'inspect', '-f', '{{.State.Paused}}', self.name]).strip()
        out = state == 'true'
        return out

# ################################################################################################################################
# ################################################################################################################################
