# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The servers of the active-passive scheduler suite. Each server runs in a container of its own together with its own
# scheduler and its own Redis, and both servers share one database, in which the run state of each job is kept.

# stdlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# Redis
from redis import Redis
from redis.exceptions import RedisError

_pubsub_failover_dir = os.path.join(os.path.dirname(__file__), '..', 'pubsub_failover')
_pubsub_failover_dir = os.path.abspath(_pubsub_failover_dir)

sys.path.insert(0, _pubsub_failover_dir)

# Zato
from failover import build_server_env, ContainerServer, copy_server_environment, create_container, docker, \
    get_failover_dir, LinkProxy, remove_container, run_container, save_container_logs, wait_until_up
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, render_template, \
    run_quickstart_and_enmasse, SessionState
from zato.common.test.receiver import WebhookReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strlist, strstrdict

    PubSubDatabase = PubSubDatabase
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.scheduler_failover')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The image of the containers and the Redis server that it contains.
    Runtime_Image = 'zato-test-runtime:latest'
    Redis_Binary = '/usr/bin/redis-server'

    # The module of the service that each job invokes.
    Service_File_Name = 'zato_test_scheduler_run_log.py'

    # The enmasse file with the jobs and the one with the pub/sub objects of the workload.
    Scheduler_Template = 'scheduler_failover/_enmasse_template.yaml'
    PubSub_Template = 'pubsub_push/_enmasse_template.yaml'

    # How long ago the grid of the interval jobs begins, in seconds.
    Grid_Start_Age_Seconds = 3600

    # How long before the jobs are imported the one-time job of the past was due, in seconds.
    Past_Start_Age_Seconds = 60

    # How long after the jobs are imported the one-time job of the gap is due, in seconds.
    Gap_Start_Delay_Seconds = 180

    # How long the quickstart and the enmasse commands may take, in seconds.
    Command_Timeout_Seconds = 300

    # How long a Redis server may take to accept connections, in seconds.
    Redis_Ready_Timeout_Seconds = 30

    # How often a Redis server is checked while it starts, in seconds.
    Redis_Poll_Seconds = 0.2

    # How long a container has to stop before it is killed, in seconds.
    Stop_Timeout_Seconds = '10'

    # The type of the shared objects with the run state of the jobs.
    Run_State_Object_Type = 'scheduler.job'

# ################################################################################################################################

_tests_dir = os.path.join(os.path.dirname(__file__), '..')
_tests_dir = os.path.abspath(_tests_dir)

_repository_dir = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin = os.path.join(_repository_dir, 'code', 'bin', 'zato')
_scheduler_bin = os.path.join(_repository_dir, 'code', 'bin', '_zato_scheduler')
_launcher_path = os.path.join(os.path.dirname(__file__), 'launcher.sh')

_topic_names = [
    'iam.user.created',
    'iam.user.deleted',
    'iam.role.assigned',
    'iam.password.changed',
    'iam.login.failed',
    'customer.registered',
    'customer.updated',
    'customer.deactivated',
    'order.placed',
    'order.shipped',
]

# The format of the start dates in the enmasse file, which are in UTC.
_date_format = '%Y-%m-%dT%H:%M:%S'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SchedulerServer:
    """ One server with its container, its own Redis, its run log and the proxies in front of its link
    to the database and of its HTTP port.
    """
    label: 'str'
    server: 'ContainerServer'
    redis_container: 'str'
    redis_port: 'int'
    run_log_path: 'str'
    scheduler_log_path: 'str'
    database_proxy: 'LinkProxy'
    http_proxy: 'LinkProxy'

# ################################################################################################################################

@dataclass
class SchedulerPair:
    """ The servers that share the database, with the dates of the jobs and, when the workload runs,
    the credentials and the receivers of pub/sub.
    """
    database: 'PubSubDatabase'
    servers: 'list[SchedulerServer]'
    work_dir: 'str'
    gap_start: 'datetime'
    states: 'list[SessionState]' = field(default_factory=list)
    publisher_username: 'str' = 'test.pubsub.publisher'
    publisher_password: 'str' = ''
    puller_username: 'str' = 'test.pubsub.puller'
    puller_password: 'str' = ''
    receivers: 'dict' = field(default_factory=dict)

    # The password of the client of the services of each server
    invoke_password: 'str' = ''

    @property
    def a(self) -> 'SchedulerServer':
        return self.servers[0]

    @property
    def b(self) -> 'SchedulerServer':
        return self.servers[1]

# ################################################################################################################################
# ################################################################################################################################

def format_date(value:'datetime') -> 'str':
    out = value.strftime(_date_format)
    return out

# ################################################################################################################################

def _start_redis(container_name:'str', port:'int') -> 'None':
    """ Starts the Redis of one server, which keeps nothing on disk, and waits until it accepts connections.
    """
    _ = docker('rm', '-f', '-v', container_name, check=False)

    _ = docker(
        'run', '-d',
        '--name', container_name,
        '--network', 'host',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--entrypoint', ModuleCtx.Redis_Binary,
        ModuleCtx.Runtime_Image,
        '--port', str(port),
        '--bind', '127.0.0.1',
        '--save', '',
        '--appendonly', 'no',
    )

    deadline = time.monotonic() + ModuleCtx.Redis_Ready_Timeout_Seconds
    client = Redis(host='127.0.0.1', port=port)

    while True:
        try:
            _ = client.ping()
            break
        except RedisError:
            if time.monotonic() > deadline:
                raise
            time.sleep(ModuleCtx.Redis_Poll_Seconds)

    client.close()

# ################################################################################################################################

def _patch_redis_port(server_directory:'str', port:'int') -> 'None':
    """ Points the server at its own Redis rather than at the default port.
    """
    server_conf_path = os.path.join(server_directory, 'config', 'repo', 'server.conf')

    with open(server_conf_path, 'r') as server_conf_file:
        content = server_conf_file.read()

    pattern = r'^(\[redis\]\nhost=\S+\nport=)\d+'
    content, count = re.subn(pattern, f'\\g<1>{port}', content, flags=re.MULTILINE)

    if count != 1:
        raise Exception(f'No [redis] port found in {server_conf_path}')

    with open(server_conf_path, 'w') as server_conf_file:
        _ = server_conf_file.write(content)

# ################################################################################################################################

def _deploy_services(server:'SchedulerServer') -> 'None':
    """ Starts the server once, before it has any jobs, which deploys the services of its pickup directory
    into its configuration database, and stops it again, so that the jobs that invoke the services can be imported.
    """
    run_container(server.server)
    _ = wait_until_up(server.server)

    _ = docker('stop', '--time', ModuleCtx.Stop_Timeout_Seconds, server.server.container_name)
    remove_container(server.server)

# ################################################################################################################################

def import_jobs(quickstart_directory:'str', server_directory:'str', rendered_yaml:'str', extra_env:'strstrdict') -> 'None':
    """ Imports the enmasse file with the jobs, offline, into the configuration database of a server,
    with the given variables added to the environment of the command.
    """
    rendered_path = os.path.join(quickstart_directory, 'enmasse.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered_yaml)

    env = os.environ.copy()
    env['Zato_Needs_Config_Reload'] = 'False'
    env.update(extra_env)

    command = [_zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory]
    result = subprocess.run(command, capture_output=True, text=True, check=False,
        timeout=ModuleCtx.Command_Timeout_Seconds, env=env)

    if result.returncode != 0:
        raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def _create_environments(labels:'strlist', pair:'SchedulerPair', invoke_password:'str') -> 'strlist':
    """ Creates the quickstart environment of the first server in the shared database, with the service of the jobs
    in its pickup directory, and a copy of it for each other server, and returns their server directories.
    """
    out:'strlist' = []
    first_state:'SessionState | None' = None

    for label in labels:
        state = SessionState(f'zato.test.scheduler_failover.{label}', f'server-logs-scheduler-{label}.txt')
        pair.states.append(state)

        quickstart_prefix = f'zato_scheduler_failover_{label}_'

        # The first server has the environment that quickstart creates in the database ..
        if first_state is None:
            server_directory = run_quickstart_and_enmasse(
                state=state,
                logger=logger,
                zato_bin=_zato_bin,
                invoke_password=invoke_password,
                rendered_yaml='',
                quickstart_prefix=quickstart_prefix,
                extra_env=pair.database.env,
                log_to_files=False,
            )

            # .. with the service of the jobs, which a server deploys from its pickup directory as it starts ..
            pickup_dir = os.path.join(server_directory, 'pickup', 'incoming', 'services')
            service_path = os.path.join(os.path.dirname(__file__), ModuleCtx.Service_File_Name)
            _ = shutil.copy(service_path, pickup_dir)

            first_state = state

        # .. and each other server has a copy of it, because the servers share the configuration of the database.
        else:
            server_directory = copy_server_environment(first_state, state, quickstart_prefix, tempfile.gettempdir())

        out.append(server_directory)

    return out

# ################################################################################################################################

def _new_server(label:'str', server_directory:'str', database:'PubSubDatabase', work_dir:'str') -> 'SchedulerServer':
    """ Returns one server in its environment, with its own Redis and its own scheduler.
    """
    # The server has its own Redis ..
    redis_port = find_free_port()
    redis_container = f'zato-scheduler-test-redis-{label}'
    _start_redis(redis_container, redis_port)

    server = ContainerServer(
        name=label,
        container_name=f'zato-scheduler-test-failover-{label}',
        server_directory=server_directory,
        port=find_free_port(),
        broker_port=find_free_port(),
        entrypoint=_launcher_path,
    )

    patch_server_conf(server_directory, server.port, False)
    _patch_redis_port(server_directory, redis_port)
    build_server_env(server, database)

    # .. its link to the database and its HTTP port are each behind a proxy, which a test may cut ..
    env = server.env

    database_proxy = LinkProxy(find_free_port(), database.port, os.path.join(work_dir, f'proxy-database-{label}.log'))
    env['Zato_Database_Port'] = str(database_proxy.listen_port)

    internal_port = find_free_port()
    env['Zato_Config_Bind_Port'] = str(internal_port)
    http_proxy = LinkProxy(server.port, internal_port, os.path.join(work_dir, f'proxy-http-{label}.log'))

    database_proxy.start()
    http_proxy.start()

    out = SchedulerServer(
        label=label,
        server=server,
        redis_container=redis_container,
        redis_port=redis_port,
        run_log_path=os.path.join(work_dir, f'run-log-{label}.jsonl'),
        scheduler_log_path=os.path.join(work_dir, f'scheduler-{label}.log'),
        database_proxy=database_proxy,
        http_proxy=http_proxy,
    )

    # .. and its own scheduler, which the launcher starts in the container.
    env['Zato_Scheduler_Redis_Host'] = '127.0.0.1'
    env['Zato_Scheduler_Redis_Port'] = str(redis_port)
    env['Zato_Scheduler_HTTP_Port'] = str(find_free_port())
    env['Zato_Scheduler_Log_Level'] = 'info'
    env['Zato_Test_Scheduler_Binary'] = _scheduler_bin
    env['Zato_Test_Zato_Binary'] = _zato_bin
    env['Zato_Test_Scheduler_Log'] = out.scheduler_log_path
    env['Zato_Test_Scheduler_Run_Log'] = out.run_log_path
    env['Zato_Test_Scheduler_Server_Label'] = label

    return out

# ################################################################################################################################

def _add_pubsub_objects(placeholders:'strstrdict', pair:'SchedulerPair', data_dir:'str') -> 'str':
    """ Adds the credentials and the receivers of the pub/sub workload, returning the rendered pub/sub enmasse file.
    """
    pair.publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()
    pair.puller_password = 'test.pull.' + CryptoManager.generate_hex_string()

    placeholders['publisher_password'] = pair.publisher_password
    placeholders['puller_password'] = pair.puller_password

    for topic_name in _topic_names:
        key = topic_name.replace('.', '_')
        port = find_free_port()

        placeholders[f'sub_{key}_password'] = 'test.sub.' + CryptoManager.generate_hex_string()
        placeholders[f'port_{key}'] = str(port)

        output_directory = os.path.join(data_dir, 'receivers', key)
        os.makedirs(output_directory, exist_ok=True)

        receiver = WebhookReceiver(port, output_directory)
        receiver.start()

        pair.receivers[topic_name] = receiver

    template_path = os.path.join(_tests_dir, ModuleCtx.PubSub_Template)
    out = render_template(template_path, placeholders)

    return out

# ################################################################################################################################

def render_job_file(placeholders:'strstrdict') -> 'tuple[str, datetime]':
    """ Renders the enmasse file with the jobs, adding their dates to the placeholders, and returns it
    with the date of the one-time job of the gap.
    """
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    grid_start = now - timedelta(seconds=ModuleCtx.Grid_Start_Age_Seconds)
    past_start = datetime.now(timezone.utc) - timedelta(seconds=ModuleCtx.Past_Start_Age_Seconds)
    gap_start = datetime.now(timezone.utc) + timedelta(seconds=ModuleCtx.Gap_Start_Delay_Seconds)
    gap_start = gap_start.replace(microsecond=0)

    placeholders['grid_start'] = format_date(grid_start)
    placeholders['past_start'] = format_date(past_start)
    placeholders['gap_start'] = format_date(gap_start)

    template_path = os.path.join(_tests_dir, ModuleCtx.Scheduler_Template)
    rendered_yaml = render_template(template_path, placeholders)

    out = (rendered_yaml, gap_start)
    return out

# ################################################################################################################################

def build_pair(database:'PubSubDatabase', needs_workload:'bool') -> 'SchedulerPair':
    """ Builds the servers on the database, of which the first one runs and the others wait as stopped containers.
    """
    work_dir = tempfile.mkdtemp(prefix='scheduler_', dir=get_failover_dir())

    # The servers share the jobs of the database, so both of them follow one grid of dates ..
    placeholders:'strstrdict' = {}
    rendered_yaml, gap_start = render_job_file(placeholders)

    pair = SchedulerPair(database=database, servers=[], work_dir=work_dir, gap_start=gap_start)

    # .. the workload adds the objects of pub/sub to the same file ..
    if needs_workload:
        data_dir = os.path.join(work_dir, 'data')
        pubsub_yaml = _add_pubsub_objects(placeholders, pair, data_dir)
        rendered_yaml = pubsub_yaml + '\n' + rendered_yaml

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
    pair.invoke_password = invoke_password

    labels = ['a', 'b']

    try:
        server_directories = _create_environments(labels, pair, invoke_password)

        for label, server_directory in zip(labels, server_directories):
            server = _new_server(label, server_directory, database, work_dir)
            pair.servers.append(server)

        # .. the first server starts once to deploy the service, and the jobs that invoke it are imported
        # .. into the shared database after that ..
        first_directory = server_directories[0]

        _deploy_services(pair.a)
        import_jobs(os.path.dirname(first_directory), first_directory, rendered_yaml, database.env)

        # .. the first server becomes active and the others wait.
        run_container(pair.a.server)
        _ = wait_until_up(pair.a.server)

        for server in pair.servers[1:]:
            create_container(server.server)

    except Exception:
        remove_pair(pair)
        raise

    return pair

# ################################################################################################################################

def remove_pair(pair:'SchedulerPair') -> 'None':
    """ Removes the containers, the proxies, the receivers and the environments of the servers.
    """
    for server in pair.servers:
        save_container_logs(server.server, pair.work_dir)
        remove_container(server.server)

        _ = docker('rm', '-f', '-v', server.redis_container, check=False)

        server.database_proxy.stop()
        server.http_proxy.stop()

    for receiver in pair.receivers.values():
        receiver.stop()

    for state in pair.states:
        state.cleanup()

# ################################################################################################################################
# ################################################################################################################################

def start_server(server:'SchedulerServer') -> 'None':
    """ Starts the existing container of a server, which takes over as it starts.
    """
    _ = docker('start', server.server.container_name)

# ################################################################################################################################

def stop_server(server:'SchedulerServer') -> 'None':
    _ = docker('stop', '--time', ModuleCtx.Stop_Timeout_Seconds, server.server.container_name)

# ################################################################################################################################

def kill_server(server:'SchedulerServer') -> 'None':
    _ = docker('kill', server.server.container_name)

# ################################################################################################################################

def pause_server(server:'SchedulerServer') -> 'None':
    _ = docker('pause', server.server.container_name)

# ################################################################################################################################

def unpause_server(server:'SchedulerServer') -> 'None':
    _ = docker('unpause', server.server.container_name)

# ################################################################################################################################

def cut_off_server(server:'SchedulerServer', command:'str') -> 'None':
    """ Cuts or restores the links of a server to the database and to its clients, with its process running throughout.
    """
    _ = server.database_proxy.command(command)
    _ = server.http_proxy.command(command)

# ################################################################################################################################

def wait_for_server(server:'SchedulerServer') -> 'float':
    out = wait_until_up(server.server)
    return out

# ################################################################################################################################
# ################################################################################################################################
