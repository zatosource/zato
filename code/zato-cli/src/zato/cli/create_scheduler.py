# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy

from zato.cli import common_odb_opts, is_arg_given, kvdb_opts, sql_conf_contents, ZatoCommand
from zato.common.api import SCHEDULER
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.crypto.const import well_known_data
from zato.common.odb.model import Cluster
from zato.common.scheduler import startup_jobs
from zato.common.util.open_ import open_w

# ################################################################################################################################

config_template = """[bind]
host=0.0.0.0
port=31530

[cluster]
id={cluster_id}
name={cluster_name}
stats_enabled=True

[server]
server_path={server_path}
server_host={server_host}
server_port={server_port}
server_username={server_username}
server_password={server_password}

[misc]
initial_sleep_time={initial_sleep_time}

[odb]
engine={odb_engine}
db_name={odb_db_name}
host={odb_host}
port={odb_port}
username={odb_username}
password={odb_password}
pool_size=1
extra=
use_async_driver=True
is_active=True

[secret_keys]
key1={secret_key1}

[crypto]
well_known_data={well_known_data}
use_tls={use_tls}
tls_protocol=TLSv1
tls_ciphers=EECDH+AES:EDH+AES:-SHA1:EECDH+RC4:EDH+RC4:RC4-SHA:EECDH+AES256:EDH+AES256:AES256-SHA:!aNULL:!eNULL:!EXP:!LOW:!MD5
tls_client_certs=optional
priv_key_location=zato-scheduler-priv-key.pem
pub_key_location=zato-scheduler-pub-key.pem
cert_location=zato-scheduler-cert.pem
ca_certs_location=zato-scheduler-ca-certs.pem

[api_users]
user1={user1_password}
"""

# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates a new scheduler instance.
    """
    needs_empty_dir = True

    # Redis options are no longer used by they are kept here for pre-3.2 backward compatibility
    opts = deepcopy(common_odb_opts) + deepcopy(kvdb_opts)

    opts.append({'name':'--pub_key_path', 'help':'Path to scheduler\'s public key in PEM'})
    opts.append({'name':'--priv_key_path', 'help':'Path to scheduler\'s private key in PEM'})
    opts.append({'name':'--cert_path', 'help':'Path to the admin\'s certificate in PEM'})
    opts.append({'name':'--ca_certs_path', 'help':'Path to a bundle of CA certificates to be trusted'})
    opts.append({'name':'--cluster_name', 'help':'Name of the cluster this scheduler will belong to'})
    opts.append({'name':'--cluster_id', 'help':'ID of the cluster this scheduler will belong to'})
    opts.append({'name':'--secret_key', 'help':'Scheduler\'s secret crypto key'})

    opts.append({'name':'--server_path', 'help':'Local path to a Zato server'})
    opts.append({'name':'--server_host', 'help':'Remote host of a Zato server'})
    opts.append({'name':'--server_port', 'help':'Remote TCP port of a Zato server'})
    opts.append({'name':'--server_username', 'help':'Username to connect to a remote server with'})
    opts.append({'name':'--server_password', 'help':'Password to connect to a remote server with'})

    opts.append({'name':'--initial_sleep_time', 'help':'How many seconds to sleep initially when the scheduler starts'})

# ################################################################################################################################

    def __init__(self, args):
        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

# ################################################################################################################################

    def _get_cluster_id_by_name(self, args, cluster_name):
        engine = self._get_engine(args)
        session = self._get_session(engine)

        cluster_id = session.query(Cluster.id).\
            filter(Cluster.name==cluster_name).\
            first()

        if not cluster_id:
            raise Exception('No such cluster name `{}`'.format(cluster_name))
        else:
            return cluster_id[0]

# ################################################################################################################################

    def execute(self, args, show_output=True, needs_created_flag=False):

        # Zato
        from zato.common.util.logging_ import get_logging_conf_contents

        os.chdir(self.target_dir)

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')
        conf_path = os.path.join(repo_dir, 'scheduler.conf')
        startup_jobs_conf_path = os.path.join(repo_dir, 'startup_jobs.conf')
        sql_conf_path = os.path.join(repo_dir, 'sql.conf')

        os.mkdir(os.path.join(self.target_dir, 'logs'))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(repo_dir)

        self.copy_scheduler_crypto(repo_dir, args)

        if hasattr(args, 'get'):
            secret_key = args.get('secret_key')
        else:
            secret_key = args.secret_key

        secret_key = secret_key or SchedulerCryptoManager.generate_key()
        cm = SchedulerCryptoManager.from_secret_key(secret_key)

        odb_engine=args.odb_type
        if odb_engine.startswith('postgresql'):
            odb_engine = 'postgresql+pg8000'

        if args.cluster_id:
            cluster_id = args.cluster_id
        else:
            cluster_id = self._get_cluster_id_by_name(args, args.cluster_name)

        odb_password = args.odb_password or ''

        odb_password = odb_password.encode('utf8')
        odb_password = cm.encrypt(odb_password)
        odb_password = odb_password.decode('utf8')

        kvdb_password = args.kvdb_password or ''
        kvdb_password = kvdb_password.encode('utf8')
        kvdb_password = cm.encrypt(kvdb_password)
        kvdb_password = kvdb_password.decode('utf8')

        user1_password = cm.generate_password()
        user1_password = cm.encrypt(user1_password)
        user1_password = user1_password.decode('utf8')

        zato_well_known_data = well_known_data.encode('utf8')
        zato_well_known_data = cm.encrypt(zato_well_known_data)
        zato_well_known_data = zato_well_known_data.decode('utf8')

        server_path     = self.get_arg('server_path')
        server_host     = self.get_arg('server_host', '127.0.0.1')
        server_port     = self.get_arg('server_port', 17010)
        server_username = self.get_arg('server_username', '')

        server_password = self.get_arg('server_password')
        server_password = server_password.encode('utf8')
        server_password = cm.encrypt(server_password)
        server_password = server_password.decode('utf8')

        initial_sleep_time = self.get_arg('initial_sleep_time', SCHEDULER.InitialSleepTime)

        if isinstance(secret_key, (bytes, bytearray)):
            secret_key = secret_key.decode('utf8')

        # We will use TLS only if we were given crypto material on input
        use_tls = is_arg_given(args, 'priv_key_path')

        config = {
            'odb_db_name': args.odb_db_name or args.sqlite_path,
            'odb_engine': odb_engine,
            'odb_host': args.odb_host or '',
            'odb_port': args.odb_port or '',
            'odb_password': odb_password,
            'odb_username': args.odb_user or '',
            'broker_host': args.kvdb_host,
            'broker_port': args.kvdb_port,
            'broker_password': kvdb_password,
            'user1_password': user1_password,
            'cluster_id': cluster_id,
            'cluster_name': args.cluster_name,
            'secret_key1': secret_key,
            'well_known_data': zato_well_known_data,
            'use_tls': 'true' if use_tls else 'false',
            'server_path': server_path,
            'server_host': server_host,
            'server_port': server_port,
            'server_username': server_username,
            'server_password': server_password,
            'initial_sleep_time': initial_sleep_time,
        }

        logging_conf_contents = get_logging_conf_contents()

        open_w(os.path.join(repo_dir, 'logging.conf')).write(logging_conf_contents)
        open_w(conf_path).write(config_template.format(**config))
        open_w(startup_jobs_conf_path).write(startup_jobs)
        open_w(sql_conf_path).write(sql_conf_contents)

        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.SCHEDULER.code)

        if show_output:
            if self.verbose:
                msg = """Successfully created a scheduler instance.
    You can start it with the 'zato start {path}' command.""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

        # We return it only when told to explicitly so when the command runs from CLI
        # it doesn't return a non-zero exit code.
        if needs_created_flag:
            return True

# ################################################################################################################################
