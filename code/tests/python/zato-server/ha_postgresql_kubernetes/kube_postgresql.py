# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The session of the Kubernetes suites of a pair on PostgreSQL. The cluster, the receivers, the quickstart
# environment and the referee are those of the SQLite suites, and one PostgreSQL instance in the zone without Zato pods
# is the pub/sub database of both pods.

# stdlib
import json
import logging
import os
import time

# Zato
from kube_cluster import apply_manifest, load_image, ModuleCtx as ClusterCtx, wait_for_rollout
from kube_env import create_cluster_session, create_secret, KubeBackend, KubeSession, ModuleCtx as EnvCtx
from zato.common.crypto.api import CryptoManager
from zato.common.test.pubsub_database import _write_tls_setup_script, connect, get_container_settings, \
    ModuleCtx as DatabaseCtx, PubSubDatabase, PubSubDBMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.postgresql')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The manifest of the instance
    Manifest_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifests', 'postgresql.yaml')

    # The StatefulSet of the instance, its only pod and the zone it runs in
    StatefulSet_Name = 'postgresql'
    Pod_Name = 'postgresql-0'
    Zone = 'zone-c'

    # The port of the instance and the node port through which the test process reaches it
    Port = 5432
    Node_Port = 30432

    # How long the instance may take to accept connections, and how often it is checked meanwhile, in seconds
    Ready_Timeout = 300
    Poll_Interval = 0.5

    # The shared memory of the pod, as large as that of the database containers of the other suites
    Shm_Size = '1Gi'

# ################################################################################################################################
# ################################################################################################################################

class KubePostgreSQL(KubeBackend):
    """ The PostgreSQL instance of the cluster, reached by the test process through its node port
    on the control plane node.
    """

    def __init__(self, session:'KubeSession') -> 'None':
        self.ip = session.control_plane_ip
        self.pod_names:'strlist' = [ModuleCtx.Pod_Name]
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

        self.database.env['Zato_PubSub_DB_SSL_CA_File'] = session.authority.cert_path

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

    def clear(self) -> 'None':
        """ Removes every table, so that the pair of the next test begins with a database without data,
        as the pair of each SQLite test begins with a copy of the quickstart environment.
        """
        connection = connect(self.database, is_admin=True)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute('drop schema public cascade')
        cursor.execute('create schema public')
        connection.close()

# ################################################################################################################################
# ################################################################################################################################

def _start_postgresql(session:'KubeSession') -> 'KubePostgreSQL':
    """ Starts the instance with its certificate, issued by the authority whose CA the pods mount, and creates
    the Secret with the pub/sub database settings of the pods.
    """
    namespace = ClusterCtx.Namespace
    out = KubePostgreSQL(session)

    os.makedirs(out.directory)

    for node_name, zone in ClusterCtx.Zones.items():
        if zone == ModuleCtx.Zone:
            load_image(DatabaseCtx.PostgreSQL_Image, [node_name])

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

    # .. the instance accepts connections over TLS only ..
    tls_script = os.path.join(out.directory, 'tls-setup.sh')
    _write_tls_setup_script(tls_script, False)

    create_secret('postgresql-init', {'tls-setup.sh': tls_script}, {})
    create_secret('postgresql-auth', {}, {'password': out.password})

    # .. with the settings of the database containers of the other suites ..
    args = ['postgres']

    for setting in get_container_settings(out.database, None):
        args.append('-c')
        args.append(setting)

    placeholders = {
        'namespace': namespace,
        'postgresql_image': DatabaseCtx.PostgreSQL_Image,
        'postgresql_args': json.dumps(args),
        'postgresql_user': DatabaseCtx.Username,
        'postgresql_db': DatabaseCtx.DB_Name,
        'postgresql_port': str(ModuleCtx.Port),
        'postgresql_node_port': str(ModuleCtx.Node_Port),
        'postgresql_zone': ModuleCtx.Zone,
        'postgresql_shm_size': ModuleCtx.Shm_Size,
    }

    apply_manifest(ModuleCtx.Manifest_Path, placeholders)
    wait_for_rollout('statefulset', ModuleCtx.StatefulSet_Name)

    out.wait_until_ready()

    # .. and the pods reach it under the name of its Service.
    host = f'{ModuleCtx.StatefulSet_Name}.{namespace}.svc.cluster.local'

    create_secret(EnvCtx.PubSub_DB_Secret, {}, {
        'Zato_PubSub_DB_Type': 'postgresql',
        'Zato_PubSub_DB_Host': host,
        'Zato_PubSub_DB_Port': str(ModuleCtx.Port),
        'Zato_PubSub_DB_Username': DatabaseCtx.Username,
        'Zato_PubSub_DB_Password': out.password,
        'Zato_PubSub_DB_Name': DatabaseCtx.DB_Name,
        'Zato_PubSub_DB_SSL': 'true',
        'Zato_PubSub_DB_SSL_CA_File': EnvCtx.Pod_CA_File,
    })

    logger.info('PostgreSQL ready in %s', ModuleCtx.Zone)

    return out

# ################################################################################################################################

def create_postgresql_session() -> 'KubeSession':
    """ Creates the cluster, the receivers, the quickstart environment of the pods and the PostgreSQL instance.
    """
    out = create_cluster_session()

    postgresql = _start_postgresql(out)

    out.backends = [postgresql]
    out.database = postgresql.database

    return out

# ################################################################################################################################
# ################################################################################################################################
