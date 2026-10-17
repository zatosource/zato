# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Turning the file transfer demo on and off, bringing it back after a restart of the server
# and stopping, on shutdown, the local servers this process started.

# stdlib
from logging import getLogger

# Zato
from zato.common.demo.file_transfer_server import write_self_signed_certificate
from zato.common.sftp_local import has_sshd
from zato.common.util.local_server import reuse_or_pick_port
from zato.server.demo_file_transfer import demo_server, ftp, sftp, smb
from zato.server.demo_file_transfer.common import change_password, delete_connections, delete_jobs, deploy_services, \
    get_paths, get_stored_connections, has_job, import_yaml, make_directory, make_root, remove_root, \
    remove_services_file, seed_files
from zato.server.demo_file_transfer.layout import All_Connections, Feeder_Name, FTP_Connections, get_connection_names, \
    get_schedule_job_names, SFTP_Connections, SMB_Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intlist, stranydict, strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.demo_file_transfer.common import demo_connection_list, DemoPaths

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The connection whose stored address says which port the SSH server listens on
_sftp_port_connection = SFTP_Connections[0].name

# The connections whose stored ports say which ports the demo server listens on, in the order of its port keys
_demo_server_port_connections = [
    FTP_Connections[0].name,
    FTP_Connections[1].name,
    SMB_Connections[0].name,
]

# ################################################################################################################################
# ################################################################################################################################

def _pick_ports(wanted:'intlist', taken:'intlist') -> 'intlist':
    """ Each wanted port if a server can still bind to it, a new free one otherwise, never one of the taken ones.
    The ports returned are added to the taken ones.
    """
    out:'intlist' = []

    for port in wanted:
        port = reuse_or_pick_port(port, taken)
        taken.append(port)
        out.append(port)

    return out

# ################################################################################################################################

def _new_demo_server_config(paths:'DemoPaths', ports:'intlist') -> 'stranydict':
    """ A new configuration of the demo server, with new passwords and a new certificate.
    """
    make_directory(paths.server_dir)

    certificate_path = write_self_signed_certificate(paths.server_dir)

    ftp_users = ftp.new_users(paths)
    smb_shares = smb.get_shares(paths)
    smb_users = smb.new_users()

    out = demo_server.new_config(paths, ports, certificate_path, ftp_users, smb_shares, smb_users)
    return out

# ################################################################################################################################

def _get_connections(paths:'DemoPaths', server_config:'stranydict', sftp_port:'int') -> 'demo_connection_list':
    """ All the demo connections, the SFTP ones only if there is an SSH server for them.
    """
    out:'demo_connection_list' = []

    if sftp_port:
        sftp_server = sftp.get_server(paths, sftp_port)
        sftp_connections = sftp.get_connections(paths, sftp_server)
        out.extend(sftp_connections)

    ftp_connections = ftp.get_connections(server_config)
    out.extend(ftp_connections)

    smb_connections = smb.get_connections(paths, server_config)
    out.extend(smb_connections)

    return out

# ################################################################################################################################

def _stop_all(paths:'DemoPaths') -> 'None':
    """ Stops both local servers, whichever process started them.
    """
    sftp.stop_any(paths)
    demo_server.stop_any(paths)

# ################################################################################################################################
# ################################################################################################################################

def import_demo_file_transfer(server:'ParallelServer') -> 'stranydict':
    """ Builds the demo's directories, starts its local servers, deploys its services, imports its connections
    with their schedules and the feeder job, and drops the first batch of files.
    """
    paths = get_paths()

    # Whatever an earlier import left behind goes away first, so each import starts from scratch ..
    _stop_all(paths)
    remove_root(paths)

    try:

        # .. the directories of the FTP and SMB users come first ..
        make_root(paths)
        ftp.build_tree(paths)
        smb.build_tree(paths)

        # .. the demo server gets its ports and its configuration ..
        taken:'intlist' = []
        server_ports = _pick_ports([0, 0, 0], taken)

        server_config = _new_demo_server_config(paths, server_ports)
        demo_server.write_config(paths, server_config)

        # .. it starts and the import waits until all three of its listeners are up ..
        demo_server.start(paths, server_config)

        # .. the SSH server goes in next, unless this machine has none ..
        if has_sshd():
            sftp_port = reuse_or_pick_port(0, taken)
            make_directory(paths.sftp_dir)
            _ = sftp.start(paths, sftp_port)
        else:
            sftp_port = 0
            logger.warning('File transfer demo: no SSH server binary on this machine, the SFTP connections are left out')

        connections = _get_connections(paths, server_config, sftp_port)

        # .. the jobs name the services, so the services are deployed before anything is imported ..
        deploy_services(server, connections)
        import_yaml(server, paths, connections)

        # .. and the schedules have something to pick up right away.
        seed_files(connections)

    # Nothing is left running if any of it failed
    except Exception:
        _stop_all(paths)
        raise

    connection_names:'strlist' = []

    for connection in connections:
        connection_names.append(connection.spec.name)

    out = {
        'is_ok': True,
        'connections': connection_names,
        'has_sftp': bool(sftp_port),
    }

    return out

# ################################################################################################################################

def remove_demo_file_transfer(server:'ParallelServer') -> 'stranydict':
    """ Deletes the demo's feeder job, its connections with their schedules and its services,
    stops its local servers and removes all of its files.
    """
    paths = get_paths()

    # The feeder goes first, so it does not upload anything to connections that are about to go away ..
    deleted = delete_jobs(server, [Feeder_Name])

    # .. deleting a connection deletes the jobs of its schedules too ..
    connection_names = get_connection_names(All_Connections)
    deleted_connections = delete_connections(server, connection_names)
    deleted.extend(deleted_connections)

    # .. though any job of a schedule still left is deleted on its own ..
    schedule_job_names = get_schedule_job_names()
    deleted_jobs = delete_jobs(server, schedule_job_names)
    deleted.extend(deleted_jobs)

    # .. now nothing uses the local servers anymore ..
    _stop_all(paths)

    # .. and the services and the files go last.
    remove_services_file(server)
    remove_root(paths)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _resume_demo_server(server:'ParallelServer', paths:'DemoPaths', stored:'anydict', taken:'intlist') -> 'stranydict':
    """ Brings the demo server back, unless it runs already, and returns its configuration.
    The ports it listens on are added to the taken ones.
    """
    server_config = demo_server.read_config(paths)

    # A server that runs with the configuration on disk is left alone ..
    if server_config:
        if demo_server.is_running(paths, server_config):
            ports = demo_server.get_ports(server_config)
            taken.extend(ports)
            return server_config

    # .. otherwise, it listens on the ports its connections were stored with, if they are still free ..
    stored_ports:'intlist' = []

    for name in _demo_server_port_connections:
        stored_port = 0

        if stored_connection := stored.get(name):
            stored_port = stored_connection['port']

        stored_ports.append(stored_port)

    ports = _pick_ports(stored_ports, taken)

    # .. without a configuration on disk, its users get new passwords, which the connections are told about ..
    if not server_config:
        server_config = _new_demo_server_config(paths, ports)

        passwords = _get_passwords(paths, server_config)

        for name, password in passwords.items():
            if stored_connection := stored.get(name):
                change_password(server, stored_connection['id'], password)

    # .. otherwise, it keeps them and only the ports may be different ..
    else:
        for key, port in zip(demo_server.Port_Keys, ports):
            server_config[key] = port

    ftp.build_tree(paths)
    smb.build_tree(paths)

    demo_server.write_config(paths, server_config)
    demo_server.start(paths, server_config)

    return server_config

# ################################################################################################################################

def _get_passwords(paths:'DemoPaths', server_config:'stranydict') -> 'stranydict':
    """ The password of each FTP and SMB connection, as the demo server's configuration has it.
    """
    out:'stranydict' = {}

    ftp_connections = ftp.get_connections(server_config)
    smb_connections = smb.get_connections(paths, server_config)

    for connection in ftp_connections + smb_connections:
        out[connection.spec.name] = connection.definition['password']

    return out

# ################################################################################################################################

def _resume_sftp(paths:'DemoPaths', stored:'anydict', taken:'intlist') -> 'int':
    """ Brings the SSH server back, unless it runs already, and returns its port, zero if the demo has no SFTP part.
    """
    stored_connection = stored.get(_sftp_port_connection)

    # The demo was imported without the SFTP connections or there is no SSH server to run now
    if not stored_connection:
        return 0

    if not has_sshd():
        logger.warning('File transfer demo: no SSH server binary on this machine, the SFTP connections stay down')
        return 0

    stored_port = sftp.parse_port(stored_connection['address'])
    sftp_server = sftp.get_server(paths, stored_port)

    # A server that runs with the configuration on disk is left alone ..
    if sftp_server.is_running():
        taken.append(stored_port)
        return stored_port

    # .. otherwise, it starts on the port its connections were stored with, if it is still free.
    out = reuse_or_pick_port(stored_port, taken)
    taken.append(out)

    make_directory(paths.sftp_dir)
    _ = sftp.start(paths, out)

    return out

# ################################################################################################################################

def resume_demo_file_transfer(server:'ParallelServer') -> 'None':
    """ Brings the demo's local servers and directories back after a restart, if the demo is on at all.
    The connections are imported anew only if any of the servers has to listen on a different port now.
    """
    if not has_job(server, Feeder_Name):
        return

    paths = get_paths()

    connection_names = get_connection_names(All_Connections)
    stored = get_stored_connections(server, connection_names)

    make_root(paths)

    taken:'intlist' = []

    server_config = _resume_demo_server(server, paths, stored, taken)
    sftp_port = _resume_sftp(paths, stored, taken)

    # The directories each connection polls are created anew if they are gone ..
    connections = _get_connections(paths, server_config, sftp_port)

    # .. and if a server listens on a port other than the one its connections were stored with,
    # .. all the connections are imported anew with what they are to use now.
    needs_import = False

    for connection in connections:

        stored_connection = stored.get(connection.spec.name)

        if not stored_connection:
            needs_import = True
            break

        if address := connection.definition.get('address'):
            if address != stored_connection['address']:
                needs_import = True
                break

        if port := connection.definition.get('port'):
            if port != stored_connection['port']:
                needs_import = True
                break

    if needs_import:
        import_yaml(server, paths, connections)

    logger.info('File transfer demo resumed (connections imported anew: %s)', needs_import)

# ################################################################################################################################

def stop_demo_file_transfer() -> 'None':
    """ Stops the local servers this very process started, leaving alone any another process started.
    """
    sftp.stop_started()
    demo_server.stop_started()

# ################################################################################################################################
# ################################################################################################################################
