# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What all the parts of the file transfer demo share - where its files live, how one demo connection is described,
# how the services are deployed, how the YAML is imported and how what was imported is found and deleted again.

# stdlib
import os
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from logging import getLogger
from shutil import rmtree
from time import sleep

# PyYAML
import yaml

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.odb.model import GenericConn, Job
from zato.common.typing_ import cast_
from zato.common.util.open_ import open_w
from zato.server.commands import CommandsFacade
from zato.server.demo_file_transfer.files import build_files
from zato.server.demo_file_transfer.layout import build_schedule, Feeder_Interval, Feeder_Name, get_service_names, \
    Schedule_Start_Step, Services_File_Name, Type_FTP, Type_SFTP, Type_SMB
from zato.server.demo_file_transfer.services import render_services_source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, stranydict, strdict, strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.demo_file_transfer.layout import ConnectionSpec

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

demo_connection_list = list['DemoConnection']

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The environment variable that moves the whole demo elsewhere, e.g. for tests that must not touch a real one
Root_Env_Name = 'Zato_Demo_File_Transfer_Root'

# Where the demo keeps everything unless told otherwise
Default_Root = '/tmp/zato-demo-file-transfer'

# Nobody but the user the server runs as may look into the demo's directories
_root_mode = 0o700

# The YAML holds passwords, so it is readable to its owner only
_yaml_mode = 0o600

# Hot deploy picks the services file up on its own, so the import waits for the services
# rather than assuming they are there - this is how long it waits.
_wait_steps = 400
_wait_step_seconds = 0.05

# How far in the future the first schedule runs for the first time, in seconds
_first_start_delay = 5

# The YAML section each connection type goes into
_yaml_sections = {
    Type_SFTP: 'outgoing_sftp',
    Type_FTP:  'outgoing_ftp',
    Type_SMB:  'outgoing_smb',
}

# The attribute of a service through which each connection type is reached
_facades = {
    Type_SFTP: 'sftp',
    Type_FTP:  'ftp',
    Type_SMB:  'smb',
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DemoPaths:
    """ Where each file and directory of the demo lives.
    """
    root: 'str'

    # The demo server with the FTP, FTPS and SMB listeners
    server_dir: 'str'
    server_config: 'str'
    server_pid: 'str'
    server_log: 'str'

    # The SSH server and the files its connections see
    sftp_dir: 'str'
    sshd_dir: 'str'
    sshd_log: 'str'
    sftp_files_dir: 'str'

    # The files the FTP and SMB connections see
    ftp_dir: 'str'
    smb_dir: 'str'

    # The YAML the connections and the jobs are imported from
    yaml_path: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DemoConnection:
    """ One demo connection - what it is, its YAML definition without the schedules,
    and the directories its schedules poll, as the connection sees them and as they are on disk.
    """
    spec: 'ConnectionSpec'
    definition: 'stranydict'
    directories: 'strdict'
    local_directories: 'strdict'

# ################################################################################################################################
# ################################################################################################################################

def get_paths() -> 'DemoPaths':
    """ Where everything of the demo lives - under its root, which an environment variable may move.
    """
    root = os.environ.get(Root_Env_Name) or Default_Root

    out = DemoPaths()
    out.root = root

    out.server_dir = os.path.join(root, 'server')
    out.server_config = os.path.join(out.server_dir, 'demo-server.json')
    out.server_pid = os.path.join(out.server_dir, 'demo-server.pid')
    out.server_log = os.path.join(out.server_dir, 'demo-server.log')

    out.sftp_dir = os.path.join(root, 'sftp')
    out.sshd_dir = os.path.join(out.sftp_dir, 'sshd')
    out.sshd_log = os.path.join(out.sshd_dir, 'sshd.log')
    out.sftp_files_dir = os.path.join(out.sftp_dir, 'files')

    out.ftp_dir = os.path.join(root, 'ftp')
    out.smb_dir = os.path.join(root, 'smb')

    out.yaml_path = os.path.join(root, 'demo-file-transfer.yaml')

    return out

# ################################################################################################################################

def new_connection(spec:'ConnectionSpec', definition:'stranydict') -> 'DemoConnection':
    """ A demo connection with no directories yet - each part adds the ones its protocol uses.
    """
    out = DemoConnection()
    out.spec = spec
    out.definition = definition
    out.directories = {}
    out.local_directories = {}

    return out

# ################################################################################################################################

def make_directory(path:'str') -> 'None':
    """ Creates a directory of the demo along with any missing parents, all readable to the owner only.
    """
    os.makedirs(path, mode=_root_mode, exist_ok=True)

# ################################################################################################################################

def make_root(paths:'DemoPaths') -> 'None':
    make_directory(paths.root)
    os.chmod(paths.root, _root_mode)

# ################################################################################################################################

def remove_root(paths:'DemoPaths') -> 'None':
    rmtree(paths.root, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

def _get_services_file_path(server:'ParallelServer') -> 'str':
    out = os.path.join(server.hot_deploy_config.pickup_dir, Services_File_Name)
    return out

# ################################################################################################################################

def build_feeder_targets(connections:'demo_connection_list') -> 'dictlist':
    """ What the feeder uploads to - each connection with the facade it is reached through
    and the directory of each of its schedule shapes.
    """
    out:'dictlist' = []

    for connection in connections:

        conn_type = connection.spec.conn_type

        target = {
            'facade': _facades[conn_type],
            'conn_name': connection.spec.name,
            'directories': connection.directories,
        }

        out.append(target)

    return out

# ################################################################################################################################

def deploy_services(server:'ParallelServer', connections:'demo_connection_list') -> 'None':
    """ Writes the services file into the hot-deployment directory and waits until all its services are deployed.
    The file is always written, so a rerun replaces an earlier version in place.
    """
    targets = build_feeder_targets(connections)
    source = render_services_source(targets)

    file_path = _get_services_file_path(server)

    with open_w(file_path) as services_file:
        _ = services_file.write(source)

    service_names = get_service_names()
    steps_left = _wait_steps

    while steps_left:

        # Each service has to be there, not only some of them ..
        missing = 0

        for service_name in service_names:
            if not server.service_store.is_deployed(service_name):
                missing += 1

        # .. and once none is missing, the file is in.
        if not missing:
            logger.info('Deployed the file transfer demo services from %s', file_path)
            return

        sleep(_wait_step_seconds)
        steps_left -= 1

    raise Exception(f'The file transfer demo services did not deploy from {file_path}')

# ################################################################################################################################

def remove_services_file(server:'ParallelServer') -> 'None':

    file_path = _get_services_file_path(server)

    if os.path.exists(file_path):
        os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def build_yaml(connections:'demo_connection_list') -> 'stranydict':
    """ The enmasse YAML with all the demo connections, each with its schedules, and the feeder job.
    The first runs of consecutive schedules are a few seconds apart, so they do not all start at once.
    """
    out:'stranydict' = {}

    now = datetime.now(timezone.utc)
    schedule_index = 0

    for connection in connections:

        section_name = _yaml_sections[connection.spec.conn_type]
        section = out.setdefault(section_name, [])

        schedules = []

        for shape, directory in connection.directories.items():

            delay = _first_start_delay + schedule_index * Schedule_Start_Step
            start = now + timedelta(seconds=delay)
            start_date = start.isoformat()

            schedule = build_schedule(shape, directory, start_date)
            schedules.append(schedule)

            schedule_index += 1

        definition = dict(connection.definition)
        definition['schedules'] = schedules

        section.append(definition)

    # The feeder job keeps the directories supplied with new files
    feeder_job = {
        'name': Feeder_Name,
        'service': Feeder_Name,
        'job_type': 'interval_based',
        'seconds': Feeder_Interval,
        'is_active': True,
    }

    out['scheduler'] = [feeder_job]

    return out

# ################################################################################################################################

def import_yaml(server:'ParallelServer', paths:'DemoPaths', connections:'demo_connection_list') -> 'None':
    """ Writes the YAML out and imports it, raising an exception if enmasse reports a failure.
    """
    config = build_yaml(connections)
    data = yaml.safe_dump(config, sort_keys=False)

    with open_w(paths.yaml_path) as yaml_file:
        _ = yaml_file.write(data)

    os.chmod(paths.yaml_path, _yaml_mode)

    facade = CommandsFacade()
    facade.init(server)

    result = facade.run_enmasse_sync_import(paths.yaml_path)

    if not result.is_ok:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        logger.warning('File transfer demo: enmasse failed, stdout=%s, stderr=%s', stdout, stderr)
        raise Exception(f'Could not import {paths.yaml_path}')

# ################################################################################################################################
# ################################################################################################################################

def seed_files(connections:'demo_connection_list') -> 'None':
    """ Drops the first batch of files straight into each directory on disk, a malformed invoice included,
    so the schedules have something to pick up before the feeder runs for the first time.
    """
    for connection in connections:
        for shape, local_directory in connection.local_directories.items():

            demo_files = build_files(shape, True)

            for demo_file in demo_files:

                file_path = os.path.join(local_directory, demo_file.name)

                with open(file_path, 'wb') as local_file:
                    _ = local_file.write(demo_file.data)

# ################################################################################################################################
# ################################################################################################################################

def get_stored_connections(server:'ParallelServer', names:'strlist') -> 'anydict':
    """ The stored demo connections of the given names, each as a dict with its id, type, address and port.
    """
    name_column = cast_('any_', GenericConn.name)

    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.id, GenericConn.name, GenericConn.type_, GenericConn.address, GenericConn.port).\
            filter(name_column.in_(names)).\
            filter(GenericConn.cluster_id==default_cluster_id).\
            all()

    # Our response to produce
    out:'anydict' = {}

    for conn_id, name, type_, address, port in rows:
        out[name] = {
            'id': conn_id,
            'type_': type_,
            'address': address or '',
            'port': port or 0,
        }

    return out

# ################################################################################################################################

def has_job(server:'ParallelServer', job_name:'str') -> 'bool':

    with closing(server.odb.session()) as session:
        row = session.query(Job.id).\
            filter(Job.name==job_name).\
            filter(Job.cluster_id==default_cluster_id).\
            first()

    out = row is not None
    return out

# ################################################################################################################################

def change_password(server:'ParallelServer', conn_id:'int', password:'str') -> 'None':
    _ = server.invoke('zato.generic.connection.change-password', {'id': conn_id, 'password': password})

# ################################################################################################################################

def delete_jobs(server:'ParallelServer', job_names:'strlist') -> 'strlist':
    """ Deletes the named scheduler jobs and returns the names of what was deleted.
    """
    job_name_column = cast_('any_', Job.name)

    with closing(server.odb.session()) as session:
        rows = session.query(Job.id, Job.name).\
            filter(job_name_column.in_(job_names)).\
            filter(Job.cluster_id==default_cluster_id).\
            all()

    # Our response to produce
    out:'strlist' = []

    for job_id, job_name in rows:
        _ = server.invoke('zato.scheduler.job.delete', {'id': job_id})
        out.append(job_name)

    return out

# ################################################################################################################################

def delete_connections(server:'ParallelServer', names:'strlist') -> 'strlist':
    """ Deletes the named generic connections, which deletes the jobs of their schedules too,
    and returns the names of what was deleted.
    """
    stored = get_stored_connections(server, names)

    # Our response to produce
    out:'strlist' = []

    for name, stored_connection in stored.items():
        request = {'id': stored_connection['id'], 'cluster_id': default_cluster_id}
        _ = server.invoke('zato.generic.connection.delete', request)
        out.append(name)

    return out

# ################################################################################################################################
# ################################################################################################################################
