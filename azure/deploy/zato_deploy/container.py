# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import re
import shlex
import ssl
import subprocess
import time
import urllib.request
from http.client import OK
from threading import Event, Thread

# Zato
from zato_deploy.common import clean_terminal_line, Config, Container, Line_Kind, Path, Port, Stage_ID, StageFailed, Status, strlist, strnone
from zato_deploy.state import Component, component_list, Progress

# ################################################################################################################################
# ################################################################################################################################

# The entrypoint colours its output and puts a timestamp in front of each of its own lines.
_Colour_Pattern    = re.compile(r'\x1b\[[0-9;]*m')
_Timestamp_Pattern = re.compile(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[^\]]*\] (\[VERBOSE\] )?')

# What the entrypoint prints that means nothing outside of a terminal.
_Skipped_Lines = {'(Ctrl+C to exit)'}

_Environment_Prefix = 'Starting Zato'
_Ready_Prefix       = 'Container ready'

_OK_Prefixes    = ['Requirements are in place', 'Version:', _Ready_Prefix]
_Error_Prefixes = ['ERROR', 'Failed to']

# The lines after which the container cannot become ready.
_Fatal_Prefixes = [
    'Failed to create a quickstart environment',
    'ERROR: Server directory',
    'ERROR: server did not respond to ping',
]

# How often the components that were started are checked, and how long one check may take.
_Component_Check_Interval = 1.5
_Component_Check_Timeout  = 30

# How long to wait for the environment to answer once the container is ready, and for each single answer.
_Environment_Timeout = 900
_Request_Timeout     = 3

# ################################################################################################################################
# ################################################################################################################################

def _process_check(pattern:'str') -> 'str':
    """ Returns a check that passes if a process runs whose command line matches the pattern.
    The first character of each pattern is in brackets, so that the pattern never matches the shell that runs the check.
    """
    quoted = shlex.quote(pattern)

    out = f'pgrep -f {quoted} >/dev/null'
    return out

# ################################################################################################################################

def _http_check(url:'str', condition:'str') -> 'str':
    """ Returns a check that passes if the HTTP status code of a URL meets the condition, with 000 meaning that nothing answered.
    """
    out = '[ "$(curl -s -o /dev/null -m 2 -w %{{http_code}} {})" {} ]'.format(url, condition)
    return out

# ################################################################################################################################

def build_components() -> 'component_list':
    """ Returns the components in the order the entrypoint starts them.
    """
    server_ping = _http_check(f'http://127.0.0.1:{Port.Server}/zato/ping', '= 200')
    mcp         = _http_check(f'http://127.0.0.1:{Port.Server}/mcp', '!= 000')
    dashboard   = _http_check(f'http://127.0.0.1:{Port.Dashboard_Internal}/accounts/login/', '= 200')
    console     = _http_check(f'http://127.0.0.1:{Port.OpenAPI_Console}/', '!= 000')

    definitions = [
        ('Scheduler',                 'Starting scheduler',                 _process_check('[q]s-1/scheduler')),
        ('Queue bridge',              'Starting queue bridge',              _process_check('[_]zato_queue_bridge')),
        ('On-prem gateway hub',       'Starting on-prem gateway hub',       _process_check('[z]ato-on-prem-gateway hub')),
        ('Server',                    'Starting server',                    server_ping),
        ('MCP gateway',               'Starting MCP gateway',               mcp),
        ('Dashboard',                 'Starting dashboard',                 dashboard),
        ('OpenAPI console',           'Starting OpenAPI console',           console),
        ('Rule engine',               'Starting rule engine',               server_ping),
        ('File pickup listener',      'Starting file pickup listener',      _process_check('[p]ickup/incoming/services')),
        ('Rule engine notifications', 'Starting rule engine notifications', _process_check('[r]ule_engine.jobs.notify')),
    ]

    out:'component_list' = []

    for name, log_prefix, check in definitions:
        component = Component()
        component.name       = name
        component.log_prefix = log_prefix
        component.check      = check
        component.status     = Status.Pending
        out.append(component)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _starts_with_any(text:'str', prefixes:'strlist') -> 'bool':

    for prefix in prefixes:
        if text.startswith(prefix):
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _get_kind(text:'str') -> 'strnone':

    if _starts_with_any(text, _OK_Prefixes):
        out = Line_Kind.OK
    elif _starts_with_any(text, _Error_Prefixes):
        out = Line_Kind.Error
    else:
        out = None

    return out

# ################################################################################################################################

def _clean_line(line:'str') -> 'str':
    """ Returns a line of the container's output without its colours and without the timestamp the page shows anyway.
    """
    line = _Colour_Pattern.sub('', line)
    line = clean_terminal_line(line)
    line = _Timestamp_Pattern.sub('', line)

    out = line.strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_zato_ids(image:'str') -> 'tuple[int, int]':
    """ Returns the user and group IDs that the zato account has in the image.
    """
    ids:'list[int]' = []

    for flag in ('-u', '-g'):
        command = ['docker', 'run', '--rm', '--entrypoint', 'id', image, flag, Container.User]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        value = result.stdout.strip()
        ids.append(int(value))

    user_id, group_id = ids

    out = (user_id, group_id)
    return out

# ################################################################################################################################

def _give_to_container(path:'str', user_id:'int', group_id:'int') -> 'None':
    """ Makes a directory and everything in it belong to the zato account of the container.
    """
    os.chown(path, user_id, group_id)

    for root, dir_names, file_names in os.walk(path):
        names = dir_names + file_names
        for name in names:
            child_path = os.path.join(root, name)
            os.chown(child_path, user_id, group_id)

# ################################################################################################################################

def start_container(progress:'Progress', config:'Config') -> 'str':
    """ Starts the container with the certificate directory mounted and returns its IP address.
    """
    progress.advance_to(Stage_ID.Requirements)

    # The container renews the certificate in the same directory, under its own account ..
    try:
        user_id, group_id = _get_zato_ids(config.image)
    except (subprocess.CalledProcessError, ValueError) as exception:
        raise StageFailed(f'User ID not read from the image: {exception}')

    os.makedirs(Path.Lets_Encrypt_Dir, exist_ok=True)
    _give_to_container(Path.Lets_Encrypt_Dir, user_id, group_id)

    # .. and it starts with what the template configured ..
    command = ['docker', 'run', '-d', '--restart=always', '--name', Container.Name]

    for port in Container.Published_Ports:
        command.extend(['-p', port])

    volume = f'{Path.Lets_Encrypt_Dir}:{Container.Lets_Encrypt_Dir}'
    command.extend(['--env-file', Path.Container_Env, '-v', volume, config.image])

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        error = result.stderr.strip()
        raise StageFailed(error)

    progress.log(f'Container {Container.Name} started')

    # .. and its own address is where it is checked from.
    template = '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
    result = subprocess.run(['docker', 'inspect', '-f', template, Container.Name], capture_output=True, text=True, check=True)

    out = result.stdout.strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

class ContainerWatch:
    """ Follows the output of the container to move through the stages, and checks each component it starts.
    """
    def __init__(self, progress:'Progress', components:'component_list') -> 'None':

        self.progress   = progress
        self.components = components
        self.stop_event = Event()

        self.is_container_ready = False
        self.logs_process:'subprocess.Popen[str] | None' = None

        # Longer prefixes come first, so that a line matches the most specific component.
        self.by_prefix = sorted(components, key=_get_prefix_length, reverse=True)

# ################################################################################################################################

    def start(self) -> 'None':

        logs_thread = Thread(target=self.follow_logs, name='zato-deploy-logs', daemon=True)
        logs_thread.start()

        components_thread = Thread(target=self.check_components, name='zato-deploy-components', daemon=True)
        components_thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':

        self.stop_event.set()

        if self.logs_process:
            self.logs_process.terminate()

# ################################################################################################################################

    def follow_logs(self) -> 'None':

        command = ['docker', 'logs', '-f', Container.Name]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
        self.logs_process = process

        # Each line may move the deployment on ..
        if process.stdout:
            for line in process.stdout:
                text = _clean_line(line)
                if not text:
                    continue
                if text in _Skipped_Lines:
                    continue
                self.handle_line(text)

        exit_code = process.wait()

        # .. and the output only ends before the environment is ready if the container stopped.
        if self.stop_event.is_set():
            return

        if not self.is_container_ready:
            self.progress.fail(f'The container stopped, docker logs exited with code {exit_code}')

# ################################################################################################################################

    def handle_line(self, text:'str') -> 'None':

        kind = _get_kind(text)
        self.progress.log(text, kind)

        # The environment is created once the requirements are in place ..
        if text.startswith(_Environment_Prefix):
            self.progress.advance_to(Stage_ID.Environment)
            return

        # .. then the components start one by one ..
        if component := self.find_component(text):
            self.progress.advance_to(Stage_ID.Components)
            with self.progress.lock:
                if component.status == Status.Pending:
                    component.status = Status.Active
            return

        # .. and the entrypoint says when it is finished with all of them ..
        if text.startswith(_Ready_Prefix):
            self.is_container_ready = True
            return

        # .. unless something happened that the container cannot recover from.
        if _starts_with_any(text, _Fatal_Prefixes):
            self.progress.fail(text, needs_log=False)

# ################################################################################################################################

    def find_component(self, text:'str') -> 'Component | None':

        for component in self.by_prefix:
            if text.startswith(component.log_prefix):
                out = component
                break
        else:
            out = None

        return out

# ################################################################################################################################

    def check_components(self) -> 'None':
        """ Checks the components that were started, each until it runs.
        """
        while not self.stop_event.wait(_Component_Check_Interval):

            with self.progress.lock:
                starting:'component_list' = []
                for component in self.components:
                    if component.status == Status.Active:
                        starting.append(component)

            if not starting:
                continue

            # One shell in the container checks all of them at once, printing the index of each that runs ..
            script_lines:'strlist' = []
            for index, component in enumerate(starting):
                script_lines.append(f'if {component.check}; then echo {index}; fi')

            script = '\n'.join(script_lines)
            command = ['docker', 'exec', Container.Name, 'sh', '-c', script]

            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=_Component_Check_Timeout)
            except subprocess.TimeoutExpired:
                continue

            # .. and each of those is marked as running.
            running = result.stdout.split()

            for index in running:
                component = starting[int(index)]
                with self.progress.lock:
                    component.status = Status.Done
                self.progress.log(f'{component.name} is running', Line_Kind.OK)

            self.update_fraction()

# ################################################################################################################################

    def update_fraction(self) -> 'None':

        with self.progress.lock:
            stage = self.progress.get_stage(Stage_ID.Components)
            done_count = 0
            for component in self.components:
                if component.status == Status.Done:
                    done_count += 1
            component_count = len(self.components)
            stage.fraction = done_count / component_count

# ################################################################################################################################

    def is_finished(self) -> 'bool':
        """ Returns whether the container is ready and every component it started runs.
        """
        if not self.is_container_ready:
            return False

        with self.progress.lock:
            for component in self.components:
                if component.status == Status.Active:
                    out = False
                    break
            else:
                out = True

        return out

# ################################################################################################################################

    def drop_components_not_started(self) -> 'None':
        """ Removes the components that the container never started, which the image may not include.
        """
        with self.progress.lock:
            started:'component_list' = []
            for component in self.components:
                if component.status != Status.Pending:
                    started.append(component)
            self.components = started
            stage = self.progress.get_stage(Stage_ID.Components)
            stage.components = started

# ################################################################################################################################
# ################################################################################################################################

def _get_prefix_length(component:'Component') -> 'int':
    out = len(component.log_prefix)
    return out

# ################################################################################################################################

def _is_ping_ok(url:'str') -> 'bool':

    try:
        with urllib.request.urlopen(url, timeout=_Request_Timeout) as response:
            body = response.read()
        data = json.loads(body)
        out = data['is_ok'] is True
    except (OSError, ValueError, KeyError):
        out = False

    return out

# ################################################################################################################################

def _is_dashboard_ok(url:'str') -> 'bool':

    # The certificate is issued for the public name, not for the address of the container.
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.check_hostname = False
    tls_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(url, timeout=_Request_Timeout, context=tls_context) as response:
            out = response.status == OK
    except OSError:
        out = False

    return out

# ################################################################################################################################

def check_environment(progress:'Progress', container_ip:'str') -> 'None':
    """ Waits until the server and the Dashboard both answer from outside of the container.
    """
    progress.advance_to(Stage_ID.Checking)

    ping_url      = f'http://{container_ip}:{Port.Load_Balancer}/zato/ping'
    dashboard_url = f'https://{container_ip}:{Port.Dashboard}/accounts/login/'

    is_ping_ok      = False
    is_dashboard_ok = False

    deadline = time.monotonic() + _Environment_Timeout

    while True:

        # The server answers through the load balancer ..
        if not is_ping_ok:
            if is_ping_ok := _is_ping_ok(ping_url):
                progress.log(f'GET {ping_url} - {{"is_ok":true}}', Line_Kind.OK)

        # .. and the Dashboard on the very port the page is on ..
        if not is_dashboard_ok:
            if is_dashboard_ok := _is_dashboard_ok(dashboard_url):
                progress.log(f'GET {dashboard_url} - 200', Line_Kind.OK)

        # .. and once both of them do, the environment is ready.
        if is_ping_ok:
            if is_dashboard_ok:
                break

        if progress.has_failed():
            raise StageFailed('The deployment failed while the environment was being checked')

        now = time.monotonic()
        if now > deadline:
            raise StageFailed(f'The environment did not answer within {_Environment_Timeout} seconds')

        time.sleep(1)

# ################################################################################################################################
# ################################################################################################################################
