# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess

# Live containers
from live_containers.docker import has_docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import bytesnone, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Each stack has a network of its own, so that its db is the only db its services see - this one is joined on top of it,
# by the few services one system reaches in another by name
Network_Name = 'zato-hl7-live'

# The entry containers use to reach services on the host
Host_Gateway = 'host.docker.internal'

# What a suite checks before it decides whether to skip, named here as well since it is this module every suite imports it from
has_docker = has_docker

# ################################################################################################################################
# ################################################################################################################################

def ensure_network() -> 'None':
    """ Creates the shared network unless it exists.
    """
    inspect = subprocess.run(['docker', 'network', 'inspect', Network_Name], capture_output=True, check=False)

    if inspect.returncode != 0:
        _ = subprocess.run(['docker', 'network', 'create', Network_Name], capture_output=True, check=True)

# ################################################################################################################################

def ensure_volume(name:'str') -> 'None':
    """ Creates a volume unless it exists - one a compose file declares external, so that the stack's stop leaves it be.
    """
    inspect = subprocess.run(['docker', 'volume', 'inspect', name], capture_output=True, check=False)

    if inspect.returncode != 0:
        _ = subprocess.run(['docker', 'volume', 'create', name], capture_output=True, check=True)

# ################################################################################################################################

def _decode(data:'bytes') -> 'str':
    out = data.decode('utf8', 'replace')
    return out

# ################################################################################################################################
# ################################################################################################################################

class ComposeStack:
    """ One docker compose project - a system's containers, started and stopped together.
    """

    def __init__(self, project_name:'str', compose_path:'str', environment:'strstrdict') -> 'None':
        self.project_name = project_name
        self.compose_path = compose_path
        self.environment = environment

# ################################################################################################################################

    def _command(self, *arguments:'str') -> 'strlist':
        out = ['docker', 'compose', '-p', self.project_name, '-f', self.compose_path]
        out.extend(arguments)

        return out

# ################################################################################################################################

    def _environment(self) -> 'strstrdict':
        """ The process environment plus the placeholders the compose file interpolates.
        """
        out = dict(os.environ)
        out.update(self.environment)

        return out

# ################################################################################################################################

    def _run(self, arguments:'strlist', *, check:'bool', input_data:'bytesnone'=None) -> 'subprocess.CompletedProcess[bytes]':
        environment = self._environment()

        out = subprocess.run(arguments, env=environment, input=input_data, capture_output=True, check=False)

        if check:
            if out.returncode != 0:
                command = ' '.join(arguments)
                stderr = _decode(out.stderr)
                raise Exception(f'Command failed ({out.returncode}): {command}\n{stderr}')

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Pulls what is missing and starts every service, waiting for none of them.
        """
        ensure_network()

        command = self._command('up', '-d')
        _ = self._run(command, check=True)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Removes the containers, their volumes and anything left over from an earlier run.
        """
        command = self._command('down', '-v', '--remove-orphans')
        _ = self._run(command, check=False)

# ################################################################################################################################

    def logs(self, service:'str'='') -> 'str':
        """ The output of one service, or of all of them.
        """
        if service:
            command = self._command('logs', '--no-color', service)
        else:
            command = self._command('logs', '--no-color')

        result = self._run(command, check=False)

        out = _decode(result.stdout) + _decode(result.stderr)
        return out

# ################################################################################################################################

    def follow_logs(self) -> 'None':
        """ Streams the output of every service to this process's own stdout until interrupted - the services
        keep running when the stream ends.
        """
        command = self._command('logs', '--follow', '--no-color')
        self._run_attached(command)

# ################################################################################################################################

    def follow_exec(self, service:'str', arguments:'strlist') -> 'Iterator[str]':
        """ Runs a command inside a running service and yields its output line by line until interrupted - for a
        system that logs to a file of its own rather than to its container's output.
        """
        command = self._command('exec', '-T', service)
        command.extend(arguments)

        process = subprocess.Popen(command, env=self._environment(), stdout=subprocess.PIPE, text=True)
        stdout = process.stdout

        if stdout is None:
            raise Exception(f'No stdout from {command}')

        try:
            for line in stdout:
                yield line.rstrip('\n')
        except KeyboardInterrupt:
            pass
        finally:
            process.terminate()

# ################################################################################################################################

    def _run_attached(self, command:'strlist') -> 'None':
        try:
            _ = subprocess.run(command, env=self._environment(), check=False)
        except KeyboardInterrupt:
            pass

# ################################################################################################################################

    def exec_raw(self, service:'str', arguments:'strlist', *, input_data:'bytesnone'=None) -> 'bytes':
        """ Runs a command inside a running service and returns its output as bytes, failing on a non-zero exit.
        """
        command = self._command('exec', '-T', service)
        command.extend(arguments)

        result = self._run(command, check=True, input_data=input_data)

        out = result.stdout
        return out

# ################################################################################################################################

    def exec_status(self, service:'str', arguments:'strlist') -> 'int':
        """ Runs a command inside a running service and returns its exit code, for a command whose exit code is the answer.
        """
        command = self._command('exec', '-T', service)
        command.extend(arguments)

        result = self._run(command, check=False)

        out = result.returncode
        return out

# ################################################################################################################################

    def exec(self, service:'str', arguments:'strlist', *, input_data:'bytesnone'=None) -> 'str':
        """ Runs a command inside a running service and returns its output as text, failing on a non-zero exit.
        """
        output = self.exec_raw(service, arguments, input_data=input_data)

        out = _decode(output)
        return out

# ################################################################################################################################

    def run_raw(self, service:'str', arguments:'strlist', *, input_data:'bytesnone'=None) -> 'bytes':
        """ Runs a one-off container of a service alone, without its dependencies, and returns its output as bytes.
        """
        command = self._command('run', '--rm', '-T', '--no-deps', service)
        command.extend(arguments)

        result = self._run(command, check=True, input_data=input_data)

        out = result.stdout
        return out

# ################################################################################################################################

    def run(self, service:'str', arguments:'strlist', *, input_data:'bytesnone'=None) -> 'str':
        """ Runs a one-off container of a service and returns its output as text, failing on a non-zero exit.
        """
        output = self.run_raw(service, arguments, input_data=input_data)

        out = _decode(output)
        return out

# ################################################################################################################################

    def restart(self, service:'str') -> 'None':
        """ Restarts one service's container, keeping the container and everything written inside it.
        """
        command = self._command('restart', service)
        _ = self._run(command, check=True)

# ################################################################################################################################

    def is_running(self, service:'str') -> 'bool':
        """ True when the service has a running container.
        """
        command = self._command('ps', '--status', 'running', '-q', service)
        result = self._run(command, check=False)

        container_ids = _decode(result.stdout).strip()

        out = container_ids != ''
        return out

# ################################################################################################################################

    def exited_services(self) -> 'strlist':
        """ The services whose container has stopped - what a wait for readiness has to know about, since
        a system whose container is gone is not going to answer.
        """
        command = self._command('ps', '--status', 'exited', '--format', '{{.Service}}')
        result = self._run(command, check=False)

        out:'strlist' = []

        for line in _decode(result.stdout).splitlines():
            if line.strip():
                out.append(line.strip())

        return out

# ################################################################################################################################
# ################################################################################################################################
