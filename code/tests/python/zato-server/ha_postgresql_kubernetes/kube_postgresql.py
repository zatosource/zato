# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The session of the Kubernetes suites of a pair on PostgreSQL. The session creates the cluster, the receivers,
# the quickstart environment and the referee, and one PostgreSQL instance in the zone without Zato pods
# is the Zato database of both pods. With Zato_Test_Kube_PostgreSQL_Backend=local, the local build
# of PostgreSQL on the host is the Zato database instead.

# stdlib
import json
import logging
import os
import time

# Zato
from kube_cluster import apply_manifest, ModuleCtx as ClusterCtx, wait_for_rollout
from kube_env import create_cluster_session, create_secret, KubeBackend, KubeSession, ModuleCtx as EnvCtx
from kube_local_postgresql import is_local_backend, start_local_backend, use_local_backend
from zato.common.crypto.api import CryptoManager
from zato.common.test.direct_sql.reset import recreate_public_schema
from zato.common.test.pubsub_database import connect, get_container_settings, ModuleCtx as DatabaseCtx, PubSubDatabase, \
    PubSubDBMode, write_tls_setup_script

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.postgresql')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The manifest of the instance
    Manifest_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifests', 'postgresql.yaml')

    # The StatefulSet of the instances, its pods, the headless Service that names each pod and the zone they run in
    StatefulSet_Name = 'postgresql'
    Pod_Name = 'postgresql-0'
    Standby_Pod_Name = 'postgresql-1'
    Replicas = 2
    Pods_Service = 'postgresql-pods'
    Zone = 'zone-c'

    # The settings that make each commit on the primary wait for the standby, which names itself after its pod
    Synchronous_Settings = [
        f'synchronous_standby_names="{Standby_Pod_Name}"',
        'cluster_name=$(POD_NAME)',
    ]

    # The state in which the primary reports a standby that each commit waits for
    Sync_State = 'sync'

    # The pg_hba.conf entry that admits the replication connection of the standby over TLS
    Replication_HBA = 'hostssl replication all all scram-sha-256'

    # The port of the instance and the node port through which the test process reaches it
    Port = 5432
    Node_Port = 30432

    # How long the instance may take to accept connections, and how often it is checked meanwhile, in seconds
    Ready_Timeout = 300
    Poll_Interval = 0.5

    # The shared memory of the pod, as large as that of the database containers of the other suites
    Shm_Size = '1Gi'

    # The directory of the node in which each pod keeps its data directory, which the host does not mount,
    # so that the cluster removes it together with the node
    Data_Dir = '/zato-ha-postgresql'

# ################################################################################################################################
# ################################################################################################################################

class KubePostgreSQL(KubeBackend):
    """ The PostgreSQL instance of the cluster, reached by the test process through its node port
    on the control plane node.
    """

    def __init__(self, session:'KubeSession') -> 'None':
        self.ip = session.control_plane_ip
        self.pod_names:'strlist' = [ModuleCtx.Pod_Name, ModuleCtx.Standby_Pod_Name]
        self.password = 'pubsub.' + CryptoManager.generate_hex_string()
        self.directory = os.path.join(session.base.run_dir, 'postgresql')

        self.database = PubSubDatabase(
            mode=PubSubDBMode.PostgreSQL_TLS,
            host=self.ip,
            port=ModuleCtx.Node_Port,
            password=self.password,
            admin_username=DatabaseCtx.Username,
            admin_password=self.password,
            work_dir=self.directory,
        )

        self.database.env['Zato_Database_SSL_CA_File'] = session.authority.cert_path

# ################################################################################################################################

    def wait_until_ready(self) -> 'None':
        """ Waits until the instance accepts connections over TLS through its node port.
        """
        deadline = time.monotonic() + ModuleCtx.Ready_Timeout

        while True:
            try:
                connection = connect(self.database)
                connection.close()
                return
            except Exception:
                if time.monotonic() > deadline:
                    raise
                time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def wait_for_synchronous_standby(self) -> 'None':
        """ Waits until the primary reports the standby as the synchronous one, which each commit then waits for.
        """
        deadline = time.monotonic() + ModuleCtx.Ready_Timeout

        while True:
            connection = connect(self.database, is_admin=True)

            try:
                cursor = connection.cursor()
                cursor.execute('SELECT sync_state FROM pg_stat_replication WHERE application_name = %s',
                    (ModuleCtx.Standby_Pod_Name,))
                rows = cursor.fetchall()
            finally:
                connection.close()

            if rows:
                if rows[0][0] == ModuleCtx.Sync_State:
                    logger.info('Synchronous standby %s connected', ModuleCtx.Standby_Pod_Name)
                    return

            assert time.monotonic() < deadline, f'No synchronous standby {ModuleCtx.Standby_Pod_Name} -> {rows}'
            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes every table, so that the pair of the next test begins with a database without data.
        """
        connection = connect(self.database, is_admin=True)
        connection.autocommit = True

        recreate_public_schema(connection)
        connection.close()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ The instance runs in the cluster, whose deletion removes it.
        """

# ################################################################################################################################
# ################################################################################################################################

def get_manifest_placeholders(database:'PubSubDatabase') -> 'strstrdict':
    """ Returns the values of the placeholders of the manifest of the instance, with the settings of the database
    containers of the other suites as the arguments of the instance.
    """
    args = ['postgres']

    for setting in get_container_settings(database, ModuleCtx.Synchronous_Settings):
        args.append('-c')
        args.append(setting)

    out = {
        'namespace': ClusterCtx.Namespace,
        'postgresql_primary': ModuleCtx.Pod_Name,
        'postgresql_pods_service': ModuleCtx.Pods_Service,
        'postgresql_replicas': str(ModuleCtx.Replicas),
        'postgresql_image': DatabaseCtx.PostgreSQL_Image,
        'postgresql_args': json.dumps(args),
        'postgresql_user': DatabaseCtx.Username,
        'postgresql_db': DatabaseCtx.DB_Name,
        'postgresql_port': str(ModuleCtx.Port),
        'postgresql_node_port': str(ModuleCtx.Node_Port),
        'postgresql_zone': ModuleCtx.Zone,
        'postgresql_shm_size': ModuleCtx.Shm_Size,
        'postgresql_data_dir': ModuleCtx.Data_Dir,
    }

    return out

# ################################################################################################################################

def _write_replication_script(path:'str') -> 'None':
    """ Writes the init script that admits the replication connection of the standby to the primary.
    """
    script = '\n'.join([
        '#!/bin/bash',
        'set -e',
        f'echo "{ModuleCtx.Replication_HBA}" >> "$PGDATA"/pg_hba.conf',
        '',
    ])

    with open(path, 'w') as script_file:
        _ = script_file.write(script)

# ################################################################################################################################

def _start_postgresql(session:'KubeSession') -> 'KubePostgreSQL':
    """ Starts the instance with its certificate, issued by the authority whose CA the pods mount, and creates
    the Secret with the pub/sub database settings of the pods.
    """
    namespace = ClusterCtx.Namespace
    out = KubePostgreSQL(session)

    os.makedirs(out.directory)

    # The certificate is valid under the name of the Service in the pods and at the control plane node ..
    dns_names = [
        ModuleCtx.StatefulSet_Name,
        f'{ModuleCtx.StatefulSet_Name}.{namespace}.svc',
        f'{ModuleCtx.StatefulSet_Name}.{namespace}.svc.cluster.local',
        'localhost',
    ]

    issued = session.authority.issue(ModuleCtx.StatefulSet_Name, dns_names, ['127.0.0.1', session.control_plane_ip])

    create_secret('postgresql-tls', {
        'server.crt': issued.cert_path,
        'server.key': issued.key_path,
        'ca.crt': session.authority.cert_path,
    }, {})

    # .. the instances accept connections over TLS only, the replication connection of the standby included ..
    tls_script = os.path.join(out.directory, 'tls-setup.sh')
    write_tls_setup_script(tls_script, False)

    replication_script = os.path.join(out.directory, 'replication-setup.sh')
    _write_replication_script(replication_script)

    create_secret('postgresql-init', {'tls-setup.sh': tls_script, 'replication-setup.sh': replication_script}, {})
    create_secret('postgresql-auth', {}, {'password': out.password})

    # .. with the settings of the database containers of the other suites ..
    placeholders = get_manifest_placeholders(out.database)
    start_time = time.monotonic()
    apply_manifest(ModuleCtx.Manifest_Path, placeholders)
    wait_for_rollout('statefulset', ModuleCtx.StatefulSet_Name)
    logger.info('PostgreSQL rollout: %.1fs', time.monotonic() - start_time)

    # .. the primary accepts connections and each of its commits waits for the standby ..
    start_time = time.monotonic()
    out.wait_until_ready()
    out.wait_for_synchronous_standby()
    logger.info('PostgreSQL synchronous standby: %.1fs', time.monotonic() - start_time)

    # .. and the pods reach it under the name of its Service.
    host = f'{ModuleCtx.StatefulSet_Name}.{namespace}.svc.cluster.local'

    create_secret(EnvCtx.PubSub_DB_Secret, {}, {
        'Zato_Database_Type': 'postgresql',
        'Zato_Database_Host': host,
        'Zato_Database_Port': str(ModuleCtx.Port),
        'Zato_Database_Username': DatabaseCtx.Username,
        'Zato_Database_Password': out.password,
        'Zato_Database_Name': DatabaseCtx.DB_Name,
        'Zato_Database_SSL': 'true',
        'Zato_Database_SSL_CA_File': EnvCtx.Pod_CA_File,
    })

    logger.info('PostgreSQL ready in %s', ModuleCtx.Zone)

    return out

# ################################################################################################################################

def create_postgresql_session() -> 'KubeSession':
    """ Creates the cluster, the receivers, the quickstart environment of the pods and the Zato database of the pods,
    which is the PostgreSQL instance in the cluster or, with the local backend, the local build on the host.
    """
    # The local build runs on the host, so the nodes of the cluster receive no image of the database ..
    if is_local_backend():
        out = create_cluster_session('', ModuleCtx.Zone)

        local_backend = start_local_backend()
        use_local_backend(out, local_backend)

    # .. whereas the instance in the cluster runs from its image.
    else:
        out = create_cluster_session(DatabaseCtx.PostgreSQL_Image, ModuleCtx.Zone)

        postgresql = _start_postgresql(out)

        out.backends = [postgresql]
        out.database = postgresql.database

    return out

# ################################################################################################################################
# ################################################################################################################################
