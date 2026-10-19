# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The import and the removal of the MCP healthcare demo - the HL7 MLLP and FHIR demo it builds on,
# the SQLite databases of the healthcare network, the services, the SQL connections, and the bearer token,
# security group and MCP gateway imported through enmasse.

# stdlib
import os
from contextlib import closing
from logging import getLogger
from shutil import copyfile, rmtree
from time import sleep

# Zato
from zato.common.api import GENERIC, Groups
from zato.common.demo.seed import Channel_Main
from zato.common.odb.model import GenericConn, GenericObject, SecurityBase, SQLConnectionPool
from zato.common.typing_ import cast_
from zato.server.commands import CommandsFacade
from zato.server.demo import import_demo_data
from zato.server.demo_mcp.common import Database_Directory, Gateway_Name, Group_Name, Security_Name, Service_Names, \
    Services_File_Name, SQL_Connections
from zato.server.demo_mcp.warehouse import build_databases

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strdict, strlist
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The enmasse file with the bearer token, the security group and the MCP gateway
_config_file_name = 'enmasse.yaml'

# The source of the services, deployed as it is
_services_source_file_name = 'services.py'

# What the SQL connections are created with, beyond their names and database paths
_sql_engine    = 'sqlite'
_sql_host      = 'localhost'
_sql_port      = 0
_sql_username  = 'demo'
_sql_pool_size = 1

# Hot deploy and the SQL connection pools both come up on their own, so the import waits for them
# rather than assuming they are there - this is how long it waits.
_wait_steps = 200
_wait_step_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _get_database_directory(server:'ParallelServer') -> 'str':
    out = os.path.join(server.work_dir, Database_Directory)
    return out

# ################################################################################################################################

def _ensure_hl7_demo(server:'ParallelServer') -> 'bool':
    """ Imports the HL7 MLLP and FHIR demo unless it is already in place. Returns whether it was imported now.
    """
    with closing(server.odb.session()) as session:
        existing = session.query(GenericConn.id).\
            filter(GenericConn.name==Channel_Main).\
            first()

    if existing:
        return False

    _ = import_demo_data(server)
    return True

# ################################################################################################################################

def _ensure_services(server:'ParallelServer') -> 'bool':
    """ Deploys the services and waits for all of them to come up. The file is always written,
    so a rerun replaces an earlier version in place.
    """
    source_path = os.path.join(os.path.dirname(__file__), _services_source_file_name)
    target_path = os.path.join(server.hot_deploy_config.pickup_dir, Services_File_Name)

    _ = copyfile(source_path, target_path)

    steps_left = _wait_steps

    while steps_left:

        deployed_count = 0

        for service_name in Service_Names:
            if server.service_store.is_deployed(service_name):
                deployed_count += 1

        if deployed_count == len(Service_Names):
            logger.info('Deployed the MCP healthcare services from %s', target_path)
            return True

        sleep(_wait_step_seconds)
        steps_left -= 1

    logger.warning('The MCP healthcare services did not deploy from %s', target_path)
    return False

# ################################################################################################################################

def _ensure_sql_connections(server:'ParallelServer', database_paths:'strdict') -> 'strlist':
    """ Creates the SQL connections that do not exist yet and waits for their pools to come up.
    Returns the names of the connections created.
    """
    sql_name_column = cast_('any_', SQLConnectionPool.name)

    with closing(server.odb.session()) as session:
        rows = session.query(SQLConnectionPool.name).\
            filter(sql_name_column.in_(SQL_Connections)).\
            all()

    existing:'strlist' = []

    for (name,) in rows:
        existing.append(name)

    # Our response to produce
    out:'strlist' = []

    for name in SQL_Connections:

        if name in existing:
            continue

        _ = server.invoke('zato.outgoing.sql.create', {
            'name': name,
            'is_active': True,
            'engine': _sql_engine,
            'host': _sql_host,
            'port': _sql_port,
            'db_name': database_paths[name],
            'username': _sql_username,
            'pool_size': _sql_pool_size,
        })

        out.append(name)

    # The gateway resolves its SQL tools through the pools, so they need to be up before it is imported
    steps_left = _wait_steps
    pool_store = server.config_manager.sql_pool_store

    while steps_left:

        ready_count = 0

        for name in SQL_Connections:
            if name in pool_store.wrappers:
                ready_count += 1

        if ready_count == len(SQL_Connections):
            break

        sleep(_wait_step_seconds)
        steps_left -= 1

    else:
        logger.warning('The MCP healthcare SQL connections did not come up')

    return out

# ################################################################################################################################
# ################################################################################################################################

def import_demo_mcp(server:'ParallelServer') -> 'stranydict':
    """ Sets up the MCP healthcare demo - the HL7 MLLP and FHIR demo it builds on, the databases,
    the services, the SQL connections, and the bearer token, security group and MCP gateway.
    """

    # The interface feeds the gateway reports on are the ones of the HL7 MLLP demo, so it goes in first ..
    hl7_imported = _ensure_hl7_demo(server)

    # .. the databases are built anew ..
    database_paths = build_databases(_get_database_directory(server))

    # .. the gateway names the services, so they are deployed before it ..
    services_deployed = _ensure_services(server)

    # .. and so are the SQL connections ..
    sql_created = _ensure_sql_connections(server, database_paths)

    # .. while the bearer token, its group and the gateway are imported through enmasse.
    config_path = os.path.join(os.path.dirname(__file__), _config_file_name)

    facade = CommandsFacade()
    facade.init(server)

    result = facade.run_enmasse_sync_import(config_path)

    if not result.is_ok:
        logger.warning('MCP healthcare demo: enmasse failed, stdout=%s, stderr=%s',
            result.stdout.strip(), result.stderr.strip())

    out = {
        'hl7_imported': hl7_imported,
        'services_deployed': services_deployed,
        'sql_created': sql_created,
        'is_ok': result.is_ok,
    }

    return out

# ################################################################################################################################

def remove_demo_mcp(server:'ParallelServer') -> 'stranydict':
    """ Removes what the MCP healthcare demo created. The HL7 MLLP and FHIR demo stays in place,
    it is a demo config set of its own.
    """
    sql_name_column = cast_('any_', SQLConnectionPool.name)

    with closing(server.odb.session()) as session:

        gateway_rows = session.query(GenericConn.id, GenericConn.name).\
            filter(GenericConn.name==Gateway_Name).\
            filter(GenericConn.type_==GENERIC.CONNECTION.TYPE.GATEWAY_MCP).\
            all()

        group_rows = session.query(GenericObject.id, GenericObject.name).\
            filter(GenericObject.name==Group_Name).\
            filter(GenericObject.type_==Groups.Type.Group_Parent).\
            filter(GenericObject.subtype==Groups.Type.API_Clients).\
            all()

        security_rows = session.query(SecurityBase.id, SecurityBase.name).\
            filter(SecurityBase.name==Security_Name).\
            all()

        sql_rows = session.query(SQLConnectionPool.id, SQLConnectionPool.name).\
            filter(sql_name_column.in_(SQL_Connections)).\
            all()

    deleted:'strlist' = []

    # The gateway goes first, together with its REST channel ..
    for gateway_id, gateway_name in gateway_rows:
        _ = server.invoke('zato.generic.connection.delete', {'id': gateway_id})
        deleted.append(gateway_name)

    # .. the group follows once no gateway uses it ..
    for group_id, group_name in group_rows:
        _ = server.invoke('zato.groups.delete', {'id': group_id})
        deleted.append(group_name)

    # .. then the bearer token that was its member ..
    for security_id, security_name in security_rows:
        _ = server.invoke('zato.security.oauth.delete', {'id': security_id})
        deleted.append(security_name)

    # .. the SQL connections ..
    for sql_id, sql_name in sql_rows:
        _ = server.invoke('zato.outgoing.sql.delete', {'id': sql_id})
        deleted.append(sql_name)

    # .. the services file ..
    services_path = os.path.join(server.hot_deploy_config.pickup_dir, Services_File_Name)

    if os.path.exists(services_path):
        os.remove(services_path)

    # .. and the databases behind the SQL connections.
    database_directory = _get_database_directory(server)

    if os.path.isdir(database_directory):
        rmtree(database_directory)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################
# ################################################################################################################################
