# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The local build of PostgreSQL as the Zato database of the pods. The primary and its synchronous standby run on the host
# on reserved ports, the primary also listens on the address of the host on the network of kind and admits the clients
# of its subnet, and the pods reach it through a Service without a selector, whose EndpointSlice names that address.

# stdlib
import logging
import os

# Zato
from kube_cluster import apply_manifest, delete_manifest, get_kind_gateway, get_kind_subnet, kubectl, ModuleCtx as ClusterCtx
from kube_env import create_secret, KubeBackend
from zato.common.test.direct_sql.reset import recreate_public_schema
from zato.common.test.pubsub_database import connect, ModuleCtx as DatabaseCtx, start_reachable_local_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeSession
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import anytuple, strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.local_postgresql')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable that selects the Zato database of a session, and its values
    Env_Backend     = 'Zato_Test_Kube_PostgreSQL_Backend'
    Backend_Cluster = 'cluster'
    Backend_Local   = 'local'

    # The manifest of the Service of the primary, the name of the Service and the port that the pods connect to
    Manifest     = 'postgresql-local.yaml'
    Service_Name = 'postgresql-local'
    Service_Port = 5432

    # The Secret with the Zato database settings of the pods
    Secret_Name = 'zato-ha-pubsub-db-local'

    # The state in which the primary reports a standby that each commit waits for
    Sync_State = 'sync'

# ################################################################################################################################
# ################################################################################################################################

def get_backend_name() -> 'str':
    """ Returns the Zato database of the pods of this session - the instance in the cluster or the local build on the host.
    """
    if not (out := os.environ.get(ModuleCtx.Env_Backend, '')):
        out = ModuleCtx.Backend_Cluster

    return out

# ################################################################################################################################

def is_local_backend() -> 'bool':
    backend_name = get_backend_name()

    out = backend_name == ModuleCtx.Backend_Local
    return out

# ################################################################################################################################
# ################################################################################################################################

class KubeLocalPostgreSQL(KubeBackend):
    """ The local cluster on the host, reached by the test process on 127.0.0.1 and by the pods through the Service.
    """

    def __init__(self, database:'PubSubDatabase', placeholders:'strstrdict') -> 'None':
        self.pod_names = []
        self.database = database
        self.placeholders = placeholders

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes every table, so that the pair of the next test begins with a database without data.
        """
        connection = connect(self.database, is_admin=True)
        connection.autocommit = True

        recreate_public_schema(connection)
        connection.close()

# ################################################################################################################################

    def query(self, statement:'str') -> 'anytuple':
        """ Runs one statement on the primary under its superuser and returns its rows.
        """
        connection = connect(self.database, is_admin=True)

        try:
            cursor = connection.cursor()
            cursor.execute(statement)
            out = cursor.fetchall()
        finally:
            connection.close()

        return out

# ################################################################################################################################

    def read_sync_state(self) -> 'str':
        """ Returns the state in which the primary reports its standby, or an empty string if it reports none.
        """
        rows = self.query('SELECT sync_state FROM pg_stat_replication')

        if rows:
            first_row = rows[0]
            out = first_row[0]
        else:
            out = ''

        return out

# ################################################################################################################################

    def read_client_addresses(self) -> 'strset':
        """ Returns the address of each client of the database of the pods, the test process excluded.
        """
        statement = f"SELECT host(client_addr) FROM pg_stat_activity WHERE datname = '{DatabaseCtx.DB_Name}' " \
            "AND client_addr IS NOT NULL AND client_addr <> '127.0.0.1' AND pid <> pg_backend_pid()"

        rows = self.query(statement)
        out:'strset' = set()

        for row in rows:
            address = row[0]
            out.add(address)

        return out

# ################################################################################################################################

    def remove_service(self) -> 'None':
        """ Deletes the Service of the primary and the Secret of the pods.
        """
        delete_manifest(ModuleCtx.Manifest, self.placeholders)
        _ = kubectl('delete', 'secret', ModuleCtx.Secret_Name, '-n', ClusterCtx.Namespace, '--ignore-not-found')

# ################################################################################################################################

    def stop(self) -> 'None':
        stop_pubsub_database(self.database)

# ################################################################################################################################
# ################################################################################################################################

def start_local_backend() -> 'KubeLocalPostgreSQL':
    """ Starts the local cluster, reachable from the network of kind, and creates the Service through which the pods reach
    its primary and the Secret with the Zato database settings of the pods.
    """
    namespace = ClusterCtx.Namespace
    gateway = get_kind_gateway()
    subnet = get_kind_subnet()

    # The primary listens on the address of the host on the network of kind and admits the nodes of the cluster ..
    database = start_reachable_local_database([gateway], [subnet])

    placeholders = {
        'namespace': namespace,
        'service_name': ModuleCtx.Service_Name,
        'service_port': str(ModuleCtx.Service_Port),
        'primary_port': str(database.port),
        'host_address': gateway,
    }

    out = KubeLocalPostgreSQL(database, placeholders)

    # .. the pods reach it through the Service ..
    apply_manifest(ModuleCtx.Manifest, placeholders)

    # .. under its name in the cluster, without TLS, which the local cluster does not offer.
    host = f'{ModuleCtx.Service_Name}.{namespace}.svc.cluster.local'

    create_secret(ModuleCtx.Secret_Name, {}, {
        'Zato_Database_Type': 'postgresql',
        'Zato_Database_Host': host,
        'Zato_Database_Port': str(ModuleCtx.Service_Port),
        'Zato_Database_Username': DatabaseCtx.Username,
        'Zato_Database_Password': database.password,
        'Zato_Database_Name': DatabaseCtx.DB_Name,
    })

    logger.info('Local PostgreSQL ready on %s:%s', gateway, database.port)

    return out

# ################################################################################################################################

def use_local_backend(session:'KubeSession', backend:'KubeLocalPostgreSQL') -> 'None':
    """ Makes the pairs of a session use the local cluster as their Zato database.
    """
    session.backends = [backend]
    session.database = backend.database
    session.placeholders['pubsub_db_secret'] = ModuleCtx.Secret_Name

# ################################################################################################################################
# ################################################################################################################################
