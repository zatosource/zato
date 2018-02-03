# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# stdlib
import os
from copy import deepcopy

from zato.cli import common_logging_conf_contents, common_odb_opts, sql_conf_contents, ZatoCommand
from zato.common.crypto import SchedulerCryptoManager, well_known_data

config_template = """[bind]
host=0.0.0.0
port=31530

[cluster]
id={cluster_id}
stats_enabled=True

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

[broker]
host={broker_host}
port={broker_port}
password={broker_password}
db=0

[secret_keys]
key1={secret_key1}

[crypto]
well_known_data={well_known_data}
use_tls=True
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

startup_jobs="""[zato.stats.process-raw-times]
seconds=90
service=zato.stats.process-raw-times
extra=max_batch_size=99999

[zato.stats.aggregate-by-minute]
seconds=60
service=zato.stats.aggregate-by-minute

[zato.stats.aggregate-by-hour]
minutes=10
service=zato.stats.aggregate-by-hour

[zato.stats.aggregate-by-day]
minutes=60
service=zato.stats.aggregate-by-day

[zato.stats.aggregate-by-month]
minutes=60
service=zato.stats.aggregate-by-month

[zato.stats.summary.create-summary-by-day]
minutes=10
service=zato.stats.summary.create-summary-by-day

[zato.stats.summary.create-summary-by-week]
minutes=10
service=zato.stats.summary.create-summary-by-week

[zato.stats.summary.create-summary-by-month]
minutes=60
service=zato.stats.summary.create-summary-by-month

[zato.stats.summary.create-summary-by-year]
minutes=60
service=zato.stats.summary.create-summary-by-year

[zato.outgoing.sql.auto-ping]
minutes=3
service=zato.outgoing.sql.auto-ping
"""

class Create(ZatoCommand):
    """ Creates a new scheduler instance.
    """
    needs_empty_dir = True
    allow_empty_secrets = True

    opts = deepcopy(common_odb_opts)

    opts.append({'name':'pub_key_path', 'help':"Path to scheduler's public key in PEM"})
    opts.append({'name':'priv_key_path', 'help':"Path to scheduler's private key in PEM"})
    opts.append({'name':'cert_path', 'help':"Path to the admin's certificate in PEM"})
    opts.append({'name':'ca_certs_path', 'help':"Path to a bundle of CA certificates to be trusted"})
    opts.append({'name':'cluster_id', 'help':"ID of the cluster this scheduler will belong to"})
    opts.append({'name':'secret_key', 'help':"Scheduler's secret crypto key"})

    def __init__(self, args):
        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

    def execute(self, args, show_output=True, needs_created_flag=False):
        os.chdir(self.target_dir)

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')
        conf_path = os.path.join(repo_dir, 'scheduler.conf')
        startup_jobs_conf_path = os.path.join(repo_dir, 'startup_jobs.conf')
        sql_conf_path = os.path.join(repo_dir, 'sql.conf')

        os.mkdir(os.path.join(self.target_dir, 'logs'))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(repo_dir)

        self.copy_scheduler_crypto(repo_dir, args)

        secret_key = args.get('secret_key') or SchedulerCryptoManager.generate_key()
        cm = SchedulerCryptoManager.from_secret_key(secret_key)

        config = {
            'odb_db_name': args.odb_db_name or args.sqlite_path,
            'odb_engine': args.odb_type,
            'odb_host': args.odb_host or '',
            'odb_port': args.odb_port or '',
            'odb_password': cm.encrypt(args.odb_password) if args.odb_password else '',
            'odb_username': args.odb_user or '',
            'broker_host': args.kvdb_host,
            'broker_port': args.kvdb_port,
            'broker_password': cm.encrypt(args.kvdb_password) if args.kvdb_password else '',
            'user1_password': cm.encrypt(cm.generate_password()),
            'cluster_id': args.cluster_id,
            'secret_key1': secret_key,
            'well_known_data': cm.encrypt(well_known_data)
        }

        open(os.path.join(repo_dir, 'logging.conf'), 'w').write(
            common_logging_conf_contents.format(log_path='./logs/scheduler.log'))
        open(conf_path, 'w').write(config_template.format(**config))
        open(startup_jobs_conf_path, 'w').write(startup_jobs)
        open(sql_conf_path, 'w').write(sql_conf_contents)

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
