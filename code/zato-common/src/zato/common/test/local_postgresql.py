# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A PostgreSQL cluster of a test that runs from the local build of PostgreSQL, a primary with one synchronous standby
# on reserved ports of 127.0.0.1. Each commit of the primary waits for the standby. The data directories of a cluster
# are on a disk, under a reserved name, and a cluster whose process exited without removing it is removed by the next
# cluster that starts.

# stdlib
import os
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass

# Zato
from zato.common.test.reservation import forget_name, is_name_live, is_reserved_name, NameReservation, PortInUse, \
    PortReservation, reserve_name, start_on_reserved_port
from zato.common.test.sql_conformance.disk import get_disk_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The installation prefix of the local build of PostgreSQL, with debug symbols and frame pointers
Local_PostgreSQL_Prefix = os.path.join(os.path.expanduser('~'), 'files', 'postgresql', '19')

# The purpose of the port reservations of the instances, by which the performance tools find them
Purpose_Local = 'postgresql-local'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The installation prefix in place of the default one
    Env_Prefix = 'Zato_Test_PostgreSQL_Prefix'

    # The directory on a disk with the clusters, and the prefix of the reserved name of each cluster
    Disk_Dir_Name = 'postgresql-local'
    Name_Prefix   = 'zato-postgresql-local'

    # The address that the instances listen on
    Host = '127.0.0.1'

    # The names of the instances, which are also their directories and, on the standby, its cluster_name,
    # which the primary names in synchronous_standby_names
    Primary = 'primary'
    Standby = 'standby'

    # The file of the settings of the tests, which postgresql.conf includes, and the password file of the clients
    Settings_File = 'zato.conf'
    Password_File = 'pgpass'

    # The file that the postmaster writes its PID into, as its first line
    PID_File = 'postmaster.pid'

    # How long pg_ctl waits for an instance to start or stop, and how long the standby may take to become synchronous
    Start_Timeout = 120
    Stop_Timeout  = 120
    Sync_Timeout  = 120

    # How often the state of the standby is checked
    Poll_Interval = 0.2

    # The lines of the log of an instance that could not bind its port
    Bind_Failures = ('could not bind', 'could not create any TCP/IP sockets')

    # The mode of the password file, which libpq requires
    Password_File_Mode = 0o600

# ################################################################################################################################
# ################################################################################################################################

class LocalPostgreSQLError(Exception):
    """ Raised when an instance of a local cluster fails to start or to become synchronous.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LocalInstance:
    """ One instance of a local cluster.
    """
    role: 'str'
    data_dir: 'str'
    log_path: 'str'
    listen_addresses: 'str'
    port: 'int'
    reservation: 'PortReservation'

# ################################################################################################################################

@dataclass(init=False)
class LocalCluster:
    """ A primary and its synchronous standby, with the credentials of their database.
    """
    reservation: 'NameReservation'
    base_dir: 'str'
    username: 'str'
    password: 'str'
    database: 'str'
    password_file: 'str'
    primary: 'LocalInstance'
    standby: 'LocalInstance'

# ################################################################################################################################
# ################################################################################################################################

def get_prefix() -> 'str':
    """ Returns the installation prefix of the local build of PostgreSQL.
    """
    if not (out := os.environ.get(ModuleCtx.Env_Prefix)):
        out = Local_PostgreSQL_Prefix

    return out

# ################################################################################################################################

def get_binary(name:'str') -> 'str':
    """ Returns the path of a program of the local build.
    """
    prefix = get_prefix()

    out = os.path.join(prefix, 'bin', name)
    return out

# ################################################################################################################################

def get_client_env(cluster:'LocalCluster') -> 'strstrdict':
    """ Returns the environment of a client program of the local build that connects to the cluster.
    """
    out = dict(os.environ)
    out['PGPASSFILE'] = cluster.password_file
    out['PGHOST'] = ModuleCtx.Host
    out['PGUSER'] = cluster.username

    return out

# ################################################################################################################################

def _run(command:'strlist', env:'strstrdict | None'=None) -> 'str':
    """ Runs a program of the local build and returns its output, raising LocalPostgreSQLError with the output if it fails.
    """
    result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)

    if result.returncode != 0:
        command_line = ' '.join(command)
        raise LocalPostgreSQLError(f'`{command_line}` exited with {result.returncode}: {result.stderr}{result.stdout}')

    out = result.stdout
    return out

# ################################################################################################################################

def run_psql(cluster:'LocalCluster', instance:'LocalInstance', query:'str') -> 'str':
    """ Runs one query through psql on an instance of the cluster and returns its rows, one per line, unaligned.
    """
    env = get_client_env(cluster)
    psql = get_binary('psql')
    command = [psql, '-X', '-p', f'{instance.port}', '-d', cluster.database, '-Atc', query]

    out = _run(command, env)
    out = out.strip()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _format_setting(setting:'str') -> 'str':
    """ Turns a setting of the form `name=value` into a line of a configuration file.
    """
    name, _, value = setting.partition('=')

    out = f"{name} = '{value}'"
    return out

# ################################################################################################################################

def _write_settings(instance:'LocalInstance', settings:'strlist') -> 'None':
    """ Writes the settings of the tests and the port of an instance into the file that its postgresql.conf includes.
    """
    lines:'strlist' = []

    for setting in settings:
        line = _format_setting(setting)
        lines.append(line)

    path = os.path.join(instance.data_dir, ModuleCtx.Settings_File)
    data = '\n'.join(lines) + '\n'

    with open(path, 'w') as settings_file:
        _ = settings_file.write(data)

# ################################################################################################################################

def _get_instance_settings(instance:'LocalInstance', settings:'strlist', synchronous_standby:'str') -> 'strlist':
    """ Returns the settings of the tests together with those of the instance itself.
    """
    out = list(settings)
    out.append(f'port={instance.port}')
    out.append(f'listen_addresses={instance.listen_addresses}')
    out.append('unix_socket_directories=')
    out.append(f'cluster_name={instance.role}')
    out.append(f'synchronous_standby_names={synchronous_standby}')

    return out

# ################################################################################################################################

def _include_settings(data_dir:'str') -> 'None':
    """ Makes postgresql.conf of a new data directory include the file of the settings of the tests.
    """
    path = os.path.join(data_dir, 'postgresql.conf')

    with open(path, 'a') as config_file:
        _ = config_file.write(f"\ninclude '{ModuleCtx.Settings_File}'\n")

# ################################################################################################################################

def _start_instance(instance:'LocalInstance', settings:'strlist') -> 'None':
    """ Starts an instance with pg_ctl on the port of the instance and waits until it accepts connections.
    Raises PortInUse if the instance could not bind its port.
    """
    instance_settings = _get_instance_settings(instance, settings, '')
    _write_settings(instance, instance_settings)

    # Each attempt has a log of its own, so that a failed bind is found in the log of this attempt only.
    if os.path.exists(instance.log_path):
        os.remove(instance.log_path)

    pg_ctl = get_binary('pg_ctl')
    command = [pg_ctl, 'start', '-D', instance.data_dir, '-l', instance.log_path, '-w', '-t', f'{ModuleCtx.Start_Timeout}']

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        return

    with open(instance.log_path) as log_file:
        log = log_file.read()

    for failure in ModuleCtx.Bind_Failures:
        if failure in log:
            raise PortInUse(f'{instance.role} could not bind port {instance.port}')

    raise LocalPostgreSQLError(f'{instance.role} did not start on port {instance.port}: {result.stderr}{log}')

# ################################################################################################################################

def _start_on_reserved_port(base_dir:'str', role:'str', settings:'strlist', listen_addresses:'str') -> 'LocalInstance':
    """ Starts an instance whose data directory exists on a port reserved for it, listening on the given addresses.
    """
    instance = LocalInstance()
    instance.role = role
    instance.data_dir = os.path.join(base_dir, role)
    instance.log_path = os.path.join(base_dir, f'{role}.log')
    instance.listen_addresses = listen_addresses

    def start(port:'int') -> 'None':
        instance.port = port
        _start_instance(instance, settings)

    started = start_on_reserved_port(Purpose_Local, start)
    instance.reservation = started.reservation

    return instance

# ################################################################################################################################
# ################################################################################################################################

def _stop_data_dir(data_dir:'str') -> 'None':
    """ Stops an instance that a process which no longer runs left behind, without a checkpoint, as its data is removed.
    """
    pid_path = os.path.join(data_dir, ModuleCtx.PID_File)

    if not os.path.exists(pid_path):
        return

    with open(pid_path) as pid_file:
        first_line = pid_file.readline()

    pid = int(first_line)

    # The postmaster runs in its data directory, and a PID whose process runs elsewhere was reused by another process.
    try:
        working_dir = os.readlink(f'/proc/{pid}/cwd')
    except (FileNotFoundError, PermissionError):
        return

    real_data_dir = os.path.realpath(data_dir)

    if working_dir != real_data_dir:
        return

    try:
        os.kill(pid, signal.SIGQUIT)
    except ProcessLookupError:
        return

    deadline = time.monotonic() + ModuleCtx.Stop_Timeout

    while os.path.exists(pid_path):
        if time.monotonic() > deadline:
            os.kill(pid, signal.SIGKILL)
            break
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def remove_stale_clusters() -> 'None':
    """ Stops and removes every cluster whose name no process that runs holds.
    """
    disk_dir = get_disk_dir(ModuleCtx.Disk_Dir_Name)

    for name in os.listdir(disk_dir):

        if not is_reserved_name(name, ModuleCtx.Name_Prefix):
            continue

        if is_name_live(name):
            continue

        base_dir = os.path.join(disk_dir, name)

        for role in (ModuleCtx.Standby, ModuleCtx.Primary):
            data_dir = os.path.join(base_dir, role)
            _stop_data_dir(data_dir)

        shutil.rmtree(base_dir)
        forget_name(name)

# ################################################################################################################################

def _write_password_file(cluster:'LocalCluster') -> 'None':
    """ Writes the password file that the client programs of the local build read.
    """
    data = f'{ModuleCtx.Host}:*:*:{cluster.username}:{cluster.password}\n'

    descriptor = os.open(cluster.password_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, ModuleCtx.Password_File_Mode)

    with os.fdopen(descriptor, 'w') as password_file:
        _ = password_file.write(data)

# ################################################################################################################################

def _wait_until_synchronous(cluster:'LocalCluster') -> 'None':
    """ Waits until the primary reports the standby as its synchronous standby.
    """
    query = f"SELECT sync_state FROM pg_stat_replication WHERE application_name = '{ModuleCtx.Standby}'"
    deadline = time.monotonic() + ModuleCtx.Sync_Timeout

    while True:

        sync_state = run_psql(cluster, cluster.primary, query)

        if sync_state == 'sync':
            return

        if time.monotonic() > deadline:
            raise LocalPostgreSQLError(f'Standby on port {cluster.standby.port} is not synchronous -> `{sync_state}`')

        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _record_instance(cluster:'LocalCluster', instance:'LocalInstance') -> 'None':
    """ Writes the details of an instance into the reservation of its port, for the tools that sample it.
    """
    prefix = get_prefix()

    instance.reservation.update(
        role=instance.role,
        data_dir=instance.data_dir,
        log_path=instance.log_path,
        database=cluster.database,
        username=cluster.username,
        password_file=cluster.password_file,
        prefix=prefix,
    )

# ################################################################################################################################

def _admit_subnets(data_dir:'str', client_subnets:'strlist') -> 'None':
    """ Makes pg_hba.conf of a new data directory admit the clients of the given subnets with a password.
    """
    path = os.path.join(data_dir, 'pg_hba.conf')
    lines:'strlist' = []

    for subnet in client_subnets:
        line = f'host all all {subnet} scram-sha-256\n'
        lines.append(line)

    with open(path, 'a') as hba_file:
        _ = hba_file.write(''.join(lines))

# ################################################################################################################################

def start_local_cluster(
    username:'str',
    password:'str',
    database:'str',
    settings:'strlist',
    extra_listen_addresses:'strlist | None' = None,
    client_subnets:'strlist | None' = None,
    ) -> 'LocalCluster':
    """ Initializes and starts a primary with the given settings and its synchronous standby, each on a port reserved
    for it, with a superuser and a database of the given names, and returns them once each commit waits for the standby.
    Each instance listens on 127.0.0.1 and on the extra addresses, and admits the clients of the given subnets.
    """
    remove_stale_clusters()

    addresses = [ModuleCtx.Host]

    if extra_listen_addresses:
        addresses.extend(extra_listen_addresses)

    listen_addresses = ','.join(addresses)

    # The cluster is under a name of its own ..
    disk_dir = get_disk_dir(ModuleCtx.Disk_Dir_Name)

    out = LocalCluster()
    out.reservation = reserve_name(ModuleCtx.Name_Prefix)
    out.base_dir = os.path.join(disk_dir, out.reservation.name)
    out.username = username
    out.password = password
    out.database = database
    out.password_file = os.path.join(out.base_dir, ModuleCtx.Password_File)

    os.makedirs(out.base_dir)
    _write_password_file(out)

    # .. the primary is initialized with the superuser and its password ..
    primary_dir = os.path.join(out.base_dir, ModuleCtx.Primary)
    initial_password_file = os.path.join(out.base_dir, 'initial-password')

    with open(initial_password_file, 'w') as initial_file:
        _ = initial_file.write(password)

    initdb = get_binary('initdb')

    _ = _run([initdb, '-D', primary_dir, '-U', username, f'--pwfile={initial_password_file}',
        '--auth-local=scram-sha-256', '--auth-host=scram-sha-256', '--encoding=UTF8', '--locale=C'])

    os.remove(initial_password_file)
    _include_settings(primary_dir)

    # .. it admits the clients of the subnets, and so does the standby, which is a copy of it ..
    if client_subnets:
        _admit_subnets(primary_dir, client_subnets)

    # .. it starts without a synchronous standby, which does not exist yet ..
    out.primary = _start_on_reserved_port(out.base_dir, ModuleCtx.Primary, settings, listen_addresses)

    client_env = get_client_env(out)
    primary_port = f'{out.primary.port}'
    createdb = get_binary('createdb')

    _ = _run([createdb, '-p', primary_port, database], client_env)

    # .. the standby is a base backup of the primary that streams from it ..
    standby_dir = os.path.join(out.base_dir, ModuleCtx.Standby)
    pg_basebackup = get_binary('pg_basebackup')

    _ = _run([pg_basebackup, '-p', primary_port, '-D', standby_dir, '-R', '-X', 'stream', '--checkpoint=fast'], client_env)

    out.standby = _start_on_reserved_port(out.base_dir, ModuleCtx.Standby, settings, listen_addresses)

    # .. and the primary makes each commit wait for it from now on.
    primary_settings = _get_instance_settings(out.primary, settings, ModuleCtx.Standby)
    _write_settings(out.primary, primary_settings)

    pg_ctl = get_binary('pg_ctl')

    _ = _run([pg_ctl, 'reload', '-D', out.primary.data_dir])
    _wait_until_synchronous(out)

    _record_instance(out, out.primary)
    _record_instance(out, out.standby)

    return out

# ################################################################################################################################

def get_cluster_env(cluster:'LocalCluster') -> 'strstrdict':
    """ Returns the variables that point the Zato database of a server or of a test at the primary of the cluster.
    """
    out = {
        'Zato_Database_Type': 'postgresql',
        'Zato_Database_Host': ModuleCtx.Host,
        'Zato_Database_Port': f'{cluster.primary.port}',
        'Zato_Database_Username': cluster.username,
        'Zato_Database_Password': cluster.password,
        'Zato_Database_Name': cluster.database,
    }

    return out

# ################################################################################################################################

def stop_primary(cluster:'LocalCluster') -> 'None':
    """ Stops the primary of a running cluster, with its data directory and the reservation of its port left in place.
    """
    pg_ctl = get_binary('pg_ctl')
    primary = cluster.primary

    _ = _run([pg_ctl, 'stop', '-D', primary.data_dir, '-m', 'fast', '-w', '-t', f'{ModuleCtx.Stop_Timeout}'])

# ################################################################################################################################

def start_primary(cluster:'LocalCluster') -> 'None':
    """ Starts the primary that stop_primary stopped, on its data directory and on its reserved port, and waits until
    each commit waits for the standby again.
    """
    # The settings file of the primary keeps its port and its synchronous standby, so the start writes no settings ..
    pg_ctl = get_binary('pg_ctl')
    primary = cluster.primary

    _ = _run([pg_ctl, 'start', '-D', primary.data_dir, '-l', primary.log_path, '-w', '-t', f'{ModuleCtx.Start_Timeout}'])

    # .. and the function returns once the standby streams from the primary again and each commit waits for it.
    _wait_until_synchronous(cluster)

# ################################################################################################################################

def stop_local_cluster(cluster:'LocalCluster') -> 'None':
    """ Stops the standby and the primary, removes their data and releases the reservations of the cluster.
    """
    pg_ctl = get_binary('pg_ctl')

    for instance in (cluster.standby, cluster.primary):
        _ = _run([pg_ctl, 'stop', '-D', instance.data_dir, '-m', 'fast', '-w', '-t', f'{ModuleCtx.Stop_Timeout}'])
        instance.reservation.release()

    shutil.rmtree(cluster.base_dir)
    cluster.reservation.release()

# ################################################################################################################################
# ################################################################################################################################
