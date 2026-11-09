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
import sqlite3
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
from failover import build_server_env, ContainerServer, create_container, docker, get_failover_dir, LinkProxy, \
    remove_container, run_container, save_container_logs, wait_until_up
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, render_template, \
    run_quickstart_and_enmasse, SessionState
from zato.common.test.pubsub_database import connect, is_postgresql_mode
from zato.common.test.receiver import WebhookReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strstrdict

    PubSubDatabase = PubSubDatabase
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

    # The service that each job invokes, the module it is in and its row in the configuration database.
    Service_Name = 'test.scheduler.failover.record-run'
    Service_File_Name = 'zato_test_scheduler_run_log.py'
    Service_Impl_Name = 'zato_test_scheduler_run_log.RecordRun'

    # The enmasse file with the jobs and the one with the pub/sub objects of the workload.
    Scheduler_Template = 'scheduler_failover/_enmasse_template.yaml'
    PubSub_Template = 'pubsub_push/_enmasse_template.yaml'

    # How long ago the grid of the interval jobs begins, in seconds.
    Grid_Start_Age_Seconds = 3600

    # How long before the jobs are imported the one-time job of the past was due, in seconds.
    Past_Start_Age_Seconds = 60

    # How long after the jobs are imported the one-time job of the gap is due, in seconds.
    Gap_Start_Delay_Seconds = 300

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
    """ One server with its container, its own Redis, its run log and, on PostgreSQL, the proxies
    in front of its link to the database and of its HTTP port.
    """
    label: 'str'
    server: 'ContainerServer'
    redis_container: 'str'
    redis_port: 'int'
    run_log_path: 'str'
    scheduler_log_path: 'str'
    database_proxy: 'LinkProxy | None' = None
    http_proxy: 'LinkProxy | None' = None

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
    _ = docker('rm', '-f', container_name, check=False)

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

def add_service_row(quickstart_directory:'str') -> 'None':
    """ Adds the service of the jobs to the configuration database, because the import of a job requires its service.
    The server matches the row with the service from the pickup directory by its name.
    """
    odb_path = os.path.join(quickstart_directory, 'zato.db')
    connection = sqlite3.connect(odb_path)

    try:
        cursor = connection.cursor()
        _ = cursor.execute('select max(id) from service')
        service_id = cursor.fetchone()[0] + 1

        _ = cursor.execute(
            'insert into service (id, name, is_active, impl_name, is_internal, slow_threshold, opaque1) ' + \
            'values (?, ?, 1, ?, 0, 99999, ?)',
            (service_id, ModuleCtx.Service_Name, ModuleCtx.Service_Impl_Name, 'null'))

        connection.commit()
    finally:
        connection.close()

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

def _new_server(
    label:'str',
    rendered_yaml:'str',
    invoke_password:'str',
    database:'PubSubDatabase',
    work_dir:'str',
    state:'SessionState',
) -> 'SchedulerServer':
    """ Creates the environment of one server, with the service of the jobs, the jobs, its own Redis and its scheduler.
    """
    server_directory = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=_zato_bin,
        invoke_password=invoke_password,
        rendered_yaml='',
        quickstart_prefix=f'zato_scheduler_failover_{label}_',
    )

    quickstart_directory = os.path.dirname(server_directory)

    # The service of the jobs is deployed from the pickup directory as the server starts,
    # and its row exists before the jobs that invoke it are imported ..
    pickup_dir = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    service_path = os.path.join(os.path.dirname(__file__), ModuleCtx.Service_File_Name)
    _ = shutil.copy(service_path, pickup_dir)

    add_service_row(quickstart_directory)
    import_jobs(quickstart_directory, server_directory, rendered_yaml, {})

    # .. the server has its own Redis ..
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

    out = SchedulerServer(
        label=label,
        server=server,
        redis_container=redis_container,
        redis_port=redis_port,
        run_log_path=os.path.join(work_dir, f'run-log-{label}.jsonl'),
        scheduler_log_path=os.path.join(work_dir, f'scheduler-{label}.log'),
    )

    # .. and its own scheduler, which the launcher starts in the container ..
    env = server.env
    env['Zato_Scheduler_Redis_Host'] = '127.0.0.1'
    env['Zato_Scheduler_Redis_Port'] = str(redis_port)
    env['Zato_Scheduler_HTTP_Port'] = str(find_free_port())
    env['Zato_Scheduler_Log_Level'] = 'info'
    env['Zato_Test_Scheduler_Binary'] = _scheduler_bin
    env['Zato_Test_Zato_Binary'] = _zato_bin
    env['Zato_Test_Scheduler_Log'] = out.scheduler_log_path
    env['Zato_Test_Scheduler_Run_Log'] = out.run_log_path
    env['Zato_Test_Scheduler_Server_Label'] = label

    # .. and on PostgreSQL, its link to the database and its HTTP port are each behind a proxy, which a test may cut.
    if is_postgresql_mode(database.mode):

        database_proxy = LinkProxy(find_free_port(), database.port, os.path.join(work_dir, f'proxy-database-{label}.log'))
        env['Zato_PubSub_DB_Port'] = str(database_proxy.listen_port)

        internal_port = find_free_port()
        env['Zato_Config_Bind_Port'] = str(internal_port)
        http_proxy = LinkProxy(server.port, internal_port, os.path.join(work_dir, f'proxy-http-{label}.log'))

        database_proxy.start()
        http_proxy.start()

        out.database_proxy = database_proxy
        out.http_proxy = http_proxy

    return out

# ################################################################################################################################

def _clear_run_state(database:'PubSubDatabase') -> 'None':
    """ Deletes the run state that an earlier pair in the same database left behind.
    """
    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute("select to_regclass('zato_shared_object')")
        table = cursor.fetchall()[0][0]

        if table:
            cursor.execute('delete from zato_shared_object where object_type = %s', (ModuleCtx.Run_State_Object_Type,))
            connection.commit()
    finally:
        connection.close()

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

def build_pair(database:'PubSubDatabase', server_count:'int', needs_workload:'bool') -> 'SchedulerPair':
    """ Builds the servers on the database, of which the first one runs and the others wait as stopped containers.
    """
    if is_postgresql_mode(database.mode):
        _clear_run_state(database)

    work_dir = tempfile.mkdtemp(prefix='scheduler_', dir=get_failover_dir())

    # The dates of the jobs are the same in each server, so both of them follow one grid ..
    placeholders:'strstrdict' = {}
    rendered_yaml, gap_start = render_job_file(placeholders)

    pair = SchedulerPair(database=database, servers=[], work_dir=work_dir, gap_start=gap_start)

    # .. the workload adds the objects of pub/sub to the same file ..
    if needs_workload:
        data_dir = os.path.join(work_dir, 'data')
        pubsub_yaml = _add_pubsub_objects(placeholders, pair, data_dir)
        rendered_yaml = pubsub_yaml + '\n' + rendered_yaml

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
    labels = ['a', 'b'][:server_count]

    try:
        for label in labels:
            state = SessionState(f'zato.test.scheduler_failover.{label}', f'server-logs-scheduler-{label}.txt')
            pair.states.append(state)

            server = _new_server(label, rendered_yaml, invoke_password, database, work_dir, state)
            pair.servers.append(server)

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

        _ = docker('rm', '-f', server.redis_container, check=False)

        if server.database_proxy:
            server.database_proxy.stop()

        if server.http_proxy:
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
    if not server.database_proxy:
        raise Exception(f'Server {server.label} has no proxies')

    if not server.http_proxy:
        raise Exception(f'Server {server.label} has no proxies')

    _ = server.database_proxy.command(command)
    _ = server.http_proxy.command(command)

# ################################################################################################################################

def wait_for_server(server:'SchedulerServer') -> 'float':
    out = wait_until_up(server.server)
    return out

# ################################################################################################################################
# ################################################################################################################################
