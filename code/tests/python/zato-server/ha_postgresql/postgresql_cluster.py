# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The PostgreSQL database that both nodes of a pair share as the pub/sub database - a primary
# with TLS and two standbys streaming from it, each built from a base backup of the primary, with each commit
# waiting for the first standby that streams. The containers are on the network of the pair, and the nodes reach
# the instance accepting writes under a network alias that a failover moves to the promoted standby.

# stdlib
import logging
import os
import shutil
import time

# Zato
from topology import Backend, docker, ModuleCtx as TopologyCtx, remove_container
from zato.common.crypto.api import CryptoManager
from zato.common.test.pubsub_certs import generate_certificates
from zato.common.test.pubsub_database import _directory_mode, _shm_size, _write_tls_setup_script, connect, \
    get_container_settings, ModuleCtx as DatabaseCtx, PubSubDatabase, PubSubDBMode
from zato.common.test.pubsub_replication import _primary_settings, _write_replication_script

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.cluster')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The instances, by the name under which each streams from the primary, and their addresses on the network
    Instance_IPs = {
        'p1': '10.231.77.12',
        's1': '10.231.77.13',
        's2': '10.231.77.14',
    }

    # The instance that is the primary when the cluster starts, and its standbys in the order of their priority
    First_Primary = 'p1'
    Standby_Names = ['s1', 's2']

    # Each commit waits for the first standby in this list that streams
    Synchronous_Standby_Names = 'FIRST 1 (s1, s2)'

    # The name under which the nodes reach the instance accepting writes
    Endpoint_Name = 'postgresql'

    # The port of every instance
    Port = 5432

    # The prefix of the containers of the instances
    Container_Prefix = 'zato-ha-test-postgresql-'

    # Where each container keeps its data
    Container_Data_Dir = '/var/lib/postgresql/data'

    # Where the instances keep their data on the host, in memory, so that the syncs of three instances on one disk
    # do not delay each other and the syncs of the nodes, as instances on hosts of their own do not
    Host_Data_Dir = '/dev/shm/zato-ha-test-postgresql'

    # How long an instance may take to accept connections or to stream, and how long a promotion may take, in seconds
    Ready_Timeout = 120
    Promote_Timeout = 60

    # How often an instance is checked while the cluster waits for it, in seconds
    Poll_Interval = 0.5

    # How long an instance may take to shut down, in seconds
    Stop_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

class Instance:
    """ One PostgreSQL instance of the cluster and its container.
    """

    def __init__(self, name:'str', directory:'str') -> 'None':
        self.name = name
        self.ip = ModuleCtx.Instance_IPs[name]
        self.container_name = f'{ModuleCtx.Container_Prefix}{name}'
        self.data_dir = os.path.join(directory, name)

# ################################################################################################################################
# ################################################################################################################################

class PostgreSQLCluster(Backend):
    """ The primary and the two standbys of the pub/sub database of a pair.
    """

    def __init__(self, run_dir:'str') -> 'None':
        self.directory = os.path.join(run_dir, 'postgresql')
        self.certs_dir = os.path.join(self.directory, 'certs')
        self.ca_path = os.path.join(self.certs_dir, 'ca.crt')
        self.password = 'pubsub.' + CryptoManager.generate_hex_string()

        self.instances:'dict[str, Instance]' = {}
        self.container_names:'strlist' = []

        for name in ModuleCtx.Instance_IPs:
            instance = Instance(name, ModuleCtx.Host_Data_Dir)
            self.instances[name] = instance
            self.container_names.append(instance.container_name)

        self.primary_name = ModuleCtx.First_Primary
        self.ip = self.instances[self.primary_name].ip

        # The test process reads the instance accepting writes at its address, over TLS ..
        self.database = PubSubDatabase(
            mode=PubSubDBMode.PostgreSQL_TLS,
            host=self.ip,
            port=ModuleCtx.Port,
            password=self.password,
            admin_username=DatabaseCtx.Username,
            admin_password=self.password,
            work_dir=self.directory,
            certs_dir=self.certs_dir,
        )

        self.database.env['Zato_PubSub_DB_SSL_CA_File'] = self.ca_path

        # .. and the nodes reach it under the name of the endpoint.
        self.node_env = {
            'Zato_PubSub_DB_Type': 'postgresql',
            'Zato_PubSub_DB_Host': ModuleCtx.Endpoint_Name,
            'Zato_PubSub_DB_Port': str(ModuleCtx.Port),
            'Zato_PubSub_DB_Username': DatabaseCtx.Username,
            'Zato_PubSub_DB_Password': self.password,
            'Zato_PubSub_DB_Name': DatabaseCtx.DB_Name,
            'Zato_PubSub_DB_SSL': 'true',
            'Zato_PubSub_DB_SSL_CA_File': self.ca_path,
        }

# ################################################################################################################################

    def _write_files(self) -> 'tuple[str, str]':
        """ Writes the certificates and the init scripts of the primary, returning the paths of both scripts.
        """
        shutil.rmtree(self.directory, ignore_errors=True)
        shutil.rmtree(ModuleCtx.Host_Data_Dir, ignore_errors=True)
        os.makedirs(self.certs_dir)
        os.chmod(self.directory, _directory_mode)
        os.chmod(self.certs_dir, _directory_mode)

        # The certificate is valid for the endpoint and for each instance, which a failover makes the endpoint ..
        host_names = [ModuleCtx.Endpoint_Name, 'localhost', '127.0.0.1']

        for instance in self.instances.values():
            host_names.append(instance.name)
            host_names.append(instance.ip)

        generate_certificates(self.certs_dir, host_names, DatabaseCtx.Username)

        # .. and the primary accepts connections and replication over TLS only.
        tls_script = os.path.join(self.certs_dir, 'tls-setup.sh')
        _write_tls_setup_script(tls_script, False)

        replication_script = os.path.join(self.certs_dir, 'replication-setup.sh')
        _write_replication_script(replication_script, PubSubDBMode.PostgreSQL_TLS)

        out = (tls_script, replication_script)
        return out

# ################################################################################################################################

    def _network_args(self, instance:'Instance') -> 'strlist':
        out = [
            '--name', instance.container_name,
            '--hostname', instance.name,
            '--network', TopologyCtx.Network_Name,
            '--ip', instance.ip,
            '--user', f'{os.getuid()}:{os.getgid()}',
            '--shm-size', _shm_size,
            '-v', f'{instance.data_dir}:{ModuleCtx.Container_Data_Dir}',
        ]

        return out

# ################################################################################################################################

    def _settings(self, extra_settings:'strlist') -> 'strlist':
        out = get_container_settings(self.database, extra_settings)
        return out

# ################################################################################################################################

    def _start_primary(self, tls_script:'str', replication_script:'str') -> 'None':
        instance = self.instances[self.primary_name]
        os.makedirs(instance.data_dir)

        command = ['run', '-d']
        command.extend(self._network_args(instance))
        command.extend(['--network-alias', ModuleCtx.Endpoint_Name])
        command.extend(['-e', 'POSTGRES_USER=' + DatabaseCtx.Username])
        command.extend(['-e', 'POSTGRES_PASSWORD=' + self.password])
        command.extend(['-e', 'POSTGRES_DB=' + DatabaseCtx.DB_Name])
        command.extend(['-v', f'{self.certs_dir}:/certs-in:ro'])
        command.extend(['-v', f'{tls_script}:/docker-entrypoint-initdb.d/tls-setup.sh:ro'])
        command.extend(['-v', f'{replication_script}:/docker-entrypoint-initdb.d/replication-setup.sh:ro'])
        command.extend([DatabaseCtx.PostgreSQL_Image, 'postgres'])

        for setting in self._settings(_primary_settings()):
            command.extend(['-c', setting])

        _ = docker(*command)
        self._wait_until_ready(instance)

# ################################################################################################################################

    def _get_conninfo(self, instance:'Instance') -> 'str':
        """ Returns how a standby connects to the instance accepting writes, under the name of the endpoint.
        """
        out = f'host={ModuleCtx.Endpoint_Name} port={ModuleCtx.Port} user={DatabaseCtx.Username} ' + \
              f'password={self.password} application_name={instance.name} sslmode=require'

        return out

# ################################################################################################################################

    def _start_standby(self, instance:'Instance') -> 'None':
        """ Builds a standby from a base backup of the primary and starts it streaming from the primary.
        """
        os.makedirs(instance.data_dir)
        os.chmod(instance.data_dir, 0o700)

        conninfo = self._get_conninfo(instance)
        data_dir = ModuleCtx.Container_Data_Dir

        replication_settings = [
            'hot_standby=on',
            f'primary_conninfo={conninfo}',
            f'primary_slot_name={instance.name}',
        ]

        postgres_command = ['postgres', '-D', data_dir]

        for setting in self._settings(replication_settings):
            postgres_command.append(f'-c "{setting}"')

        script = ' && '.join([
            f'pg_basebackup -d "{conninfo}" -D {data_dir} -X stream -c fast -C -S {instance.name} -R',
            'exec ' + ' '.join(postgres_command),
        ])

        command = ['run', '-d']
        command.extend(self._network_args(instance))
        command.extend(['--entrypoint', 'bash', DatabaseCtx.PostgreSQL_Image, '-c', script])

        _ = docker(*command)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the primary, both standbys streaming from it, and makes each commit wait for the first of them.
        """
        tls_script, replication_script = self._write_files()
        self._start_primary(tls_script, replication_script)

        for name in ModuleCtx.Standby_Names:
            self._start_standby(self.instances[name])

        self._wait_until_streaming(ModuleCtx.Standby_Names[0], 'async')
        self._wait_until_streaming(ModuleCtx.Standby_Names[1], 'async')

        # The initialization of the primary committed before any standby existed, so commits wait from here on.
        standby_names = "'" + ModuleCtx.Synchronous_Standby_Names + "'"

        self._run_on_primary([
            f'alter system set synchronous_standby_names = {standby_names}',
            "alter system set synchronous_commit = 'on'",
            'select pg_reload_conf()',
        ])

        self._wait_until_streaming(ModuleCtx.Standby_Names[0], 'sync')

        logger.info('PostgreSQL ready with primary %s at %s', self.primary_name, self.ip)

# ################################################################################################################################

    def _connect(self, instance:'Instance') -> 'any_':
        out = connect(self.database, host=instance.ip, port=ModuleCtx.Port, is_admin=True)
        return out

# ################################################################################################################################

    def _wait_until_ready(self, instance:'Instance') -> 'None':
        """ Waits until an instance accepts connections over TLS.
        """
        deadline = time.monotonic() + ModuleCtx.Ready_Timeout

        while True:
            try:
                connection = self._connect(instance)
                connection.close()
                return
            except Exception:
                if time.monotonic() > deadline:
                    raise
                time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def _wait_until_streaming(self, standby_name:'str', expected_state:'str') -> 'None':
        """ Waits until the primary reports a standby as streaming in the expected synchronization state.
        """
        deadline = time.monotonic() + ModuleCtx.Ready_Timeout
        query = 'select state, sync_state from pg_stat_replication where application_name = %s'

        while True:
            connection = self._connect(self.instances[self.primary_name])
            cursor = connection.cursor()
            cursor.execute(query, (standby_name,))
            rows = cursor.fetchall()
            connection.close()

            for state, sync_state in rows:
                if state == 'streaming':
                    if sync_state == expected_state:
                        return

            if time.monotonic() > deadline:
                raise Exception(f'Standby {standby_name} is not streaming as {expected_state}, rows `{rows}`')

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def _run_on_primary(self, statements:'strlist') -> 'None':
        """ Runs statements outside of a transaction on the instance accepting writes.
        """
        connection = self._connect(self.instances[self.primary_name])
        connection.autocommit = True
        cursor = connection.cursor()

        for statement in statements:
            cursor.execute(statement)

        connection.close()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Shuts the primary down, which makes the database unavailable to both nodes.
        """
        instance = self.instances[self.primary_name]
        _ = docker('stop', '-t', str(ModuleCtx.Stop_Timeout), instance.container_name)

# ################################################################################################################################

    def resume(self) -> 'None':
        """ Starts the stopped primary again, with its data and under the name of the endpoint.
        """
        instance = self.instances[self.primary_name]
        _ = docker('start', instance.container_name)
        self._wait_until_ready(instance)

# ################################################################################################################################

    def kill(self, name:'str') -> 'None':
        """ Ends an instance at once, the way a crash of its host would.
        """
        _ = docker('kill', self.instances[name].container_name)

# ################################################################################################################################

    def disconnect(self, name:'str') -> 'None':
        """ Removes an instance from the network, after which it reaches neither the primary nor the nodes.
        """
        _ = docker('network', 'disconnect', '--force', TopologyCtx.Network_Name, self.instances[name].container_name)

# ################################################################################################################################

    def _connect_to_network(self, instance:'Instance', options:'strlist') -> 'None':
        """ Connects an instance to the network again at its own address, with the given options of the connection,
        replacing the connection it has, if any.
        """
        _ = docker('network', 'disconnect', '--force', TopologyCtx.Network_Name, instance.container_name, check=False)
        network = TopologyCtx.Network_Name
        _ = docker('network', 'connect', '--ip', instance.ip, *options, network, instance.container_name)

# ################################################################################################################################

    def promote(self, name:'str') -> 'float':
        """ Promotes a standby whose primary is no longer reachable, moves the name of the endpoint to it
        and returns how long the promotion took, in seconds.
        """
        instance = self.instances[name]
        former = self.instances[self.primary_name]
        start = time.monotonic()

        # The former primary leaves the network, so that it never accepts a write after the promotion ..
        self.disconnect(former.name)

        # .. the standby is on the network under its own address only, including one that left it to fall behind ..
        self._connect_to_network(instance, [])

        # .. it is promoted ..
        connection = self._connect(instance)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute('select pg_promote(true, %s)', (ModuleCtx.Promote_Timeout,))
        row:'any_' = cursor.fetchone()
        connection.close()

        is_promoted = row[0]

        if not is_promoted:
            raise Exception(f'Standby {name} was not promoted')

        # .. and the nodes reach it under the name of the endpoint only once it accepts writes.
        self._connect_to_network(instance, ['--alias', ModuleCtx.Endpoint_Name])

        self.primary_name = name
        self.ip = instance.ip
        self.database.host = instance.ip

        out = time.monotonic() - start
        logger.info('PostgreSQL standby %s promoted in %.2fs', name, out)

        return out

# ################################################################################################################################

    def remove(self) -> 'None':
        for container_name in self.container_names:
            remove_container(container_name)

        shutil.rmtree(ModuleCtx.Host_Data_Dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
