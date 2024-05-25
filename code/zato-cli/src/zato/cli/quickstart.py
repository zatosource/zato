# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy

# Zato
from zato.cli import common_odb_opts, common_scheduler_server_api_client_opts, common_scheduler_server_address_opts, ZatoCommand
from zato.common.typing_ import cast_
from zato.common.util.config import get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.platform_ import is_windows, is_non_windows
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

DEFAULT_NO_SERVERS=1

vscode_launch_json = """
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Remote Zato Main",
            "type": "python",
            "request": "launch",
            "program": "/opt/zato/current/zato-server/src/zato/server/main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "GEVENT_SUPPORT":"true",
                "ZATO_SERVER_BASE_DIR": "/opt/zato/env/qs-1/server1",
                "ZATO_SCHEDULER_BASE_DIR": "/opt/zato/env/qs-1/scheduler"
            }
        }
    ]
}
"""

vscode_settings_json = """
{
    "python.defaultInterpreterPath": "/opt/zato/current/bin/python"
}
"""

# ################################################################################################################################
# ################################################################################################################################

windows_qs_start_template = """
@echo off

set zato_cmd=zato
set env_dir="{env_dir}"

start /b %zato_cmd% start %env_dir%\\server1
start /b %zato_cmd% start %env_dir%\\web-admin
start /b %zato_cmd% start %env_dir%\\scheduler

echo:
echo *** Starting Zato in %env_dir%  ***
echo:
""".strip() # noqa: W605

# ################################################################################################################################
# ################################################################################################################################

# Taken from http://stackoverflow.com/a/246128
script_dir = """SOURCE="${BASH_SOURCE[0]}"
BASE_DIR="$( dirname "$SOURCE" )"
while [ -h "$SOURCE" ]
do
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$BASE_DIR/$SOURCE"
  BASE_DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd )"
done
BASE_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
"""

# ################################################################################################################################
# ################################################################################################################################

check_config_template = """$ZATO_BIN check-config $BASE_DIR/{server_name}"""

# ################################################################################################################################
# ################################################################################################################################

start_servers_template = """
$ZATO_BIN start $BASE_DIR/{server_name} --verbose
$ZATO_BIN wait --path $BASE_DIR/{server_name}
echo [{step_number}/$STEPS] {server_name} started
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_start_head_template = """#!/bin/bash

set -e
export ZATO_CLI_DONT_SHOW_OUTPUT=1

{script_dir}
ZATO_BIN={zato_bin}
STEPS={start_steps}
CLUSTER={cluster_name}

{cluster_starting}
echo Checking configuration
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_start_body_template = """
{check_config}
{check_config_extra}

# Make sure TCP ports are available
echo [{check_config_step_number}/$STEPS] Checking TCP ports availability

ZATO_BIN_PATH=`which zato`
ZATO_BIN_DIR=`python -c "import os; print(os.path.dirname('$ZATO_BIN_PATH'))"`
UTIL_DIR=`python -c "import os; print(os.path.join('$ZATO_BIN_DIR', '..', 'util'))"`

$ZATO_BIN_DIR/py $UTIL_DIR/check_tcp_ports.py {check_tcp_ports_suffix}

# .. load-balancer ..
{start_lb}

# .. scheduler ..
{start_scheduler}

# .. servers ..
{start_servers}
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_check_config_extra = """
echo [1/$STEPS] Redis connection OK
echo [2/$STEPS] SQL ODB connection OK
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_start_lb_windows = 'echo "[4/%STEPS%] (Skipped starting load balancer)"'

zato_qs_start_lb_non_windows = """
# Start the load balancer first ..
$ZATO_BIN start $BASE_DIR/load-balancer --verbose
echo [4/$STEPS] Load-balancer started
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_start_dashboard = """
# .. Dashboard comes as the last one because it may ask Django-related questions.
$ZATO_BIN start $BASE_DIR/web-admin --verbose
echo [$STEPS/$STEPS] Dashboard started
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_cluster_starting = """
echo Starting Zato cluster $CLUSTER
"""

zato_qs_cluster_started = """
echo Zato cluster $CLUSTER started
"""

zato_qs_cluster_stopping = """
echo Stopping Zato cluster $CLUSTER
"""

zato_qs_cluster_stopped = """
echo Zato cluster $CLUSTER stopped
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_start_tail_template = """
{start_dashboard}

cd $BASE_DIR
{cluster_started}
echo Visit https://zato.io/support for more information and support options
exit 0
"""

stop_servers_template = """
$ZATO_BIN stop $BASE_DIR/{server_name}
echo [{step_number}/$STEPS] {server_name} stopped
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_start_scheduler = """
$ZATO_BIN start $BASE_DIR/scheduler --verbose
echo [{scheduler_step_count}/$STEPS] Scheduler started
"""

zato_qs_stop_scheduler = """
$ZATO_BIN stop $BASE_DIR/scheduler
echo [$STEPS/$STEPS] Scheduler stopped
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_stop_template = """#!/bin/bash

export ZATO_CLI_DONT_SHOW_OUTPUT=1

{script_dir}

if [[ "$1" = "--delete-pidfiles" ]]
then
  echo Deleting PID files

  rm -f $BASE_DIR/load-balancer/pidfile
  rm -f $BASE_DIR/load-balancer/zato-lb-agent.pid
  rm -f $BASE_DIR/server1/pidfile
  rm -f $BASE_DIR/server2/pidfile
  rm -f $BASE_DIR/web-admin/pidfile
  rm -f $BASE_DIR/scheduler/pidfile

  echo PID files deleted
fi

ZATO_BIN={zato_bin}
STEPS={stop_steps}
CLUSTER={cluster_name}

{cluster_stopping}

# Start the load balancer first ..
$ZATO_BIN stop $BASE_DIR/load-balancer
echo [1/$STEPS] Load-balancer stopped

# .. servers ..
{stop_servers}

$ZATO_BIN stop $BASE_DIR/web-admin
echo [{web_admin_step_count}/$STEPS] Dashboard stopped

# .. scheduler ..
{stop_scheduler}

cd $BASE_DIR
{cluster_stopped}
"""

# ################################################################################################################################
# ################################################################################################################################

zato_qs_restart = """#!/bin/bash

{script_dir}
cd $BASE_DIR

$BASE_DIR/zato-qs-stop.sh
$BASE_DIR/zato-qs-start.sh
"""

# ################################################################################################################################
# ################################################################################################################################

class CryptoMaterialLocation:
    """ Locates and remembers location of various crypto material for Zato components.
    """
    def __init__(self, ca_dir:'str', component_pattern:'str') -> 'None':
        self.ca_dir = ca_dir
        self.component_pattern = component_pattern
        self.ca_certs_path = os.path.join(self.ca_dir, 'ca-material', 'ca-cert.pem')
        self.cert_path = None
        self.pub_path = None
        self.priv_path = None
        self.locate()

    def locate(self) -> 'None':
        for crypto_name in('cert', 'priv', 'pub'):
            path = os.path.join(self.ca_dir, 'out-{}'.format(crypto_name))
            for name in os.listdir(path):
                full_path = os.path.join(path, name)
                if '{}-{}'.format(self.component_pattern, crypto_name) in full_path:
                    setattr(self, '{}_path'.format(crypto_name), full_path)

# ################################################################################################################################

class Create(ZatoCommand):
    """ Quickly creates a working cluster
    """
    needs_empty_dir = True
    opts:'any_' = deepcopy(common_odb_opts)
    opts.append({'name':'--cluster-name', 'help':'Name to be given to the new cluster'})
    opts.append({'name':'--servers', 'help':'How many servers to create', 'default':1}) # type: ignore
    opts.append({'name':'--threads-per-server', 'help':'How many main threads to use per server', 'default':1}) # type: ignore
    opts.append({'name':'--secret-key', 'help':'Main secret key the server(s) will use'})
    opts.append({'name':'--jwt-secret-key', 'help':'Secret key for JWT (JSON Web Tokens)'})
    opts.append({'name':'--no-scheduler', 'help':'Create all the components but not a scheduler', 'action':'store_true'})
    opts.append({'name':'--scheduler-only', 'help':'Only create a scheduler, without other components', 'action':'store_true'})

    opts += deepcopy(common_scheduler_server_address_opts)
    opts += deepcopy(common_scheduler_server_api_client_opts)

    def _bunch_from_args(self, args:'any_', admin_invoke_password:'str', cluster_name:'str'='') -> 'Bunch':

        # Bunch
        from bunch import Bunch

        out = Bunch()
        out.path = args.path
        out.verbose = args.verbose
        out.store_log = args.store_log
        out.store_config = args.store_config
        out.odb_type = args.odb_type
        out.odb_host = args.odb_host
        out.odb_port = args.odb_port
        out.odb_user = args.odb_user
        out.odb_db_name = args.odb_db_name
        out.kvdb_host = self.get_arg('kvdb_host')
        out.kvdb_port = self.get_arg('kvdb_port')
        out.sqlite_path = getattr(args, 'sqlite_path', None)
        out.postgresql_schema = getattr(args, 'postgresql_schema', None)
        out.odb_password = args.odb_password
        out.kvdb_password = self.get_arg('kvdb_password')
        out.cluster_name = cluster_name
        out.scheduler_name = 'scheduler1'
        out.scheduler_address_for_server = getattr(args, 'scheduler_address_for_server', '')
        out.server_address_for_scheduler = getattr(args, 'server_address_for_scheduler', '')

        out['admin-invoke-password'] = admin_invoke_password
        out.admin_invoke_password = admin_invoke_password
        out.server_password = admin_invoke_password
        out.server_api_client_for_scheduler_password = admin_invoke_password

        return out

# ################################################################################################################################

    def allow_empty_secrets(self) -> 'bool':
        return True

# ################################################################################################################################

    def _set_pubsub_server(self, args:'any_', server_id:'int', cluster_name:'str', topic_name:'str') -> 'None':

        # Zato
        from zato.common.odb.model import Cluster, PubSubSubscription, PubSubTopic

        engine = self._get_engine(args) # type: ignore
        session = self._get_session(engine) # type: ignore

        sub_list:'any_' = session.query(PubSubSubscription).\
            filter(PubSubTopic.id==PubSubSubscription.topic_id).\
            filter(PubSubTopic.name==topic_name).\
            filter(PubSubTopic.cluster_id==Cluster.id).\
            filter(Cluster.name==cluster_name).\
            all()

        for sub in sub_list: # type: ignore

            # Set publishing server for that subscription
            sub.server_id = server_id

            session.add(sub)
        session.commit()

# ################################################################################################################################

    def execute(self, args:'any_') -> 'None':
        """ Quickly creates Zato components
        1) CA and crypto material
        2) ODB
        3) ODB initial data
        4) Servers
        5) Load-balancer
        6) Dashboard
        7) Scheduler
        8) Scripts
        """

        # stdlib
        import os
        import random
        import stat
        from collections import OrderedDict
        from contextlib import closing
        from copy import deepcopy
        from itertools import count
        from uuid import uuid4

        # Cryptography
        from cryptography.fernet import Fernet

        # These are shared by all servers
        secret_key = getattr(args, 'secret_key', None) or Fernet.generate_key()
        jwt_secret = getattr(args, 'jwt_secret_key', None) or Fernet.generate_key()

        # Zato
        from zato.cli import ca_create_ca, ca_create_lb_agent, ca_create_scheduler, ca_create_server, \
             ca_create_web_admin, create_cluster, create_lb, create_odb, create_scheduler, create_server, create_web_admin
        from zato.common.crypto.api import CryptoManager
        from zato.common.defaults import http_plain_server_port
        from zato.common.odb.model import Cluster
        from zato.common.util.api import get_engine, get_session

        random.seed()

        # We handle both ..
        admin_invoke_password = self.get_arg('admin_invoke_password')
        server_api_client_for_scheduler_password = self.get_arg('server_api_client_for_scheduler_password')

        # .. but we prefer the latter ..
        admin_invoke_password = admin_invoke_password or server_api_client_for_scheduler_password

        # .. and we build it ourselves if it is not given.
        admin_invoke_password = admin_invoke_password or 'admin.invoke.' + uuid4().hex

        scheduler_api_client_for_server_auth_required = getattr(args, 'scheduler_api_client_for_server_auth_required', None)
        scheduler_api_client_for_server_username = get_scheduler_api_client_for_server_username(args)
        scheduler_api_client_for_server_password = get_scheduler_api_client_for_server_password(
            args,
            cast_('CryptoManager', None),
            initial_password=cast_('str', CryptoManager.generate_password(to_str=True)),
            needs_encrypt=False
        )

        # Make sure we always work with absolute paths
        args_path = os.path.abspath(args.path)

        if args.odb_type == 'sqlite':
            args.sqlite_path = os.path.join(args_path, 'zato.db')

        next_step = count(1)
        next_port = count(http_plain_server_port)
        cluster_name = getattr(args, 'cluster_name', None) or 'quickstart-{}'.format(random.getrandbits(20)).zfill(7)
        servers = int(getattr(args, 'servers', 0) or DEFAULT_NO_SERVERS)

        server_names = OrderedDict() # type: ignore
        for idx in range(1, servers+1):
            server_names['{}'.format(idx)] = 'server{}'.format(idx)

        try:
            threads_per_server = int(args.threads_per_server)
        except Exception:
            threads_per_server = 1

        lb_host = '127.0.0.1'
        lb_port = 11223
        lb_agent_port = 20151

        # This could've been set to True by user in the command-line so we'd want
        # to unset it so that individual commands quickstart invokes don't attempt
        # to store their own configs.
        args.store_config = False

        # We use TLS only on systems other than Windows
        has_tls = is_non_windows

        # This will be True if the scheduler does not have to be created
        no_scheduler:'bool' = self.get_arg('no_scheduler', False)

        # This will be True if we create only the scheduler, without any other components
        scheduler_only:'bool' = self.get_arg('scheduler_only', False)

        # Shortcuts for later use
        should_create_scheduler = not no_scheduler
        create_components_other_than_scheduler = not scheduler_only

        # Under Windows, even if the load balancer is created, we do not log this information.
        total_non_servers_steps = 5 if is_windows else 7
        total_steps = total_non_servers_steps + servers

        # Take the scheduler into account
        if no_scheduler:
            total_steps -= 1
        elif scheduler_only:
            # 1 for servers
            # 1 for Dashboard
            # 1 for the load-balancer
            total_steps -= 3

# ################################################################################################################################

        #
        # 1) CA
        #

        if has_tls:

            ca_path = os.path.join(args_path, 'ca')
            os.mkdir(ca_path)

            ca_args = self._bunch_from_args(args, admin_invoke_password, cluster_name)
            ca_args.path = ca_path

            ca_create_ca.Create(ca_args).execute(ca_args, False)
            ca_create_lb_agent.Create(ca_args).execute(ca_args, False)
            ca_create_web_admin.Create(ca_args).execute(ca_args, False)
            ca_create_scheduler.Create(ca_args).execute(ca_args, False)

            server_crypto_loc = {}

            for name in server_names: # type: ignore
                ca_args_server = deepcopy(ca_args)
                ca_args_server.server_name = server_names[name]
                ca_create_server.Create(ca_args_server).execute(ca_args_server, False)
                server_crypto_loc[name] = CryptoMaterialLocation(ca_path, '{}-{}'.format(cluster_name, server_names[name]))

            lb_agent_crypto_loc = CryptoMaterialLocation(ca_path, 'lb-agent')
            web_admin_crypto_loc = CryptoMaterialLocation(ca_path, 'web-admin')
            scheduler_crypto_loc = CryptoMaterialLocation(ca_path, 'scheduler1')

        self.logger.info('[{}/{}] Certificate authority created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 2) ODB
        #
        if create_odb.Create(args).execute(args, False) == self.SYS_ERROR.ODB_EXISTS:
            self.logger.info('[{}/{}] ODB schema already exists'.format(next(next_step), total_steps))
        else:
            self.logger.info('[{}/{}] ODB schema created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 3) ODB initial data
        #
        create_cluster_args = self._bunch_from_args(args, admin_invoke_password, cluster_name)
        create_cluster_args.lb_host = lb_host
        create_cluster_args.lb_port = lb_port
        create_cluster_args.lb_agent_port = lb_agent_port
        create_cluster_args.secret_key = secret_key
        create_cluster.Create(create_cluster_args).execute(create_cluster_args, False) # type: ignore

        self.logger.info('[{}/{}] ODB initial data created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 4) servers
        #

        # This is populated below in order for the scheduler to use it.
        first_server_path = ''

        if create_components_other_than_scheduler:

            for idx, name in enumerate(server_names): # type: ignore
                server_path = os.path.join(args_path, server_names[name])
                os.mkdir(server_path)

                create_server_args = self._bunch_from_args(args, admin_invoke_password, cluster_name)
                create_server_args.server_name = server_names[name]
                create_server_args.path = server_path
                create_server_args.jwt_secret = jwt_secret
                create_server_args.secret_key = secret_key
                create_server_args.threads = threads_per_server
                create_server_args.scheduler_api_client_for_server_auth_required = scheduler_api_client_for_server_auth_required
                create_server_args.scheduler_api_client_for_server_username = scheduler_api_client_for_server_username
                create_server_args.scheduler_api_client_for_server_password = scheduler_api_client_for_server_password

                if has_tls:
                    create_server_args.cert_path = server_crypto_loc[name].cert_path # type: ignore
                    create_server_args.pub_key_path = server_crypto_loc[name].pub_path # type: ignore
                    create_server_args.priv_key_path = server_crypto_loc[name].priv_path # type: ignore
                    create_server_args.ca_certs_path = server_crypto_loc[name].ca_certs_path # type: ignore

                server_id:'int' = create_server.Create(
                    create_server_args).execute(create_server_args, next(next_port), False, True) # type: ignore

                # We special case the first server ..
                if idx == 0:

                    # .. make it a delivery server for sample pub/sub topics ..
                    self._set_pubsub_server(args, server_id, cluster_name, '/zato/demo/sample') # type: ignore

                    # .. make the scheduler use it.
                    first_server_path = server_path

                self.logger.info('[{}/{}] server{} created'.format(next(next_step), total_steps, name))

# ################################################################################################################################

        #
        # 5) load-balancer
        #

        if create_components_other_than_scheduler:

            lb_path = os.path.join(args_path, 'load-balancer')
            os.mkdir(lb_path)

            create_lb_args = self._bunch_from_args(args, admin_invoke_password, cluster_name)
            create_lb_args.path = lb_path

            if has_tls:
                create_lb_args.cert_path = lb_agent_crypto_loc.cert_path # type: ignore
                create_lb_args.pub_key_path = lb_agent_crypto_loc.pub_path # type: ignore
                create_lb_args.priv_key_path = lb_agent_crypto_loc.priv_path # type: ignore
                create_lb_args.ca_certs_path = lb_agent_crypto_loc.ca_certs_path # type: ignore

            # Need to substract 1 because we've already called .next() twice
            # when creating servers above.
            servers_port = next(next_port) - 1

            create_lb.Create(create_lb_args).execute(create_lb_args, True, servers_port, False)

            # Under Windows, we create the directory for the load-balancer
            # but we do not advertise it because we do not start it.
            if is_non_windows:
                self.logger.info('[{}/{}] Load-balancer created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 6) Dashboard
        #

        if create_components_other_than_scheduler:
            web_admin_path = os.path.join(args_path, 'web-admin')
            os.mkdir(web_admin_path)

            create_web_admin_args = self._bunch_from_args(args, admin_invoke_password, cluster_name)
            create_web_admin_args.path = web_admin_path
            create_web_admin_args.admin_invoke_password = admin_invoke_password

            if has_tls:
                create_web_admin_args.cert_path = web_admin_crypto_loc.cert_path # type: ignore
                create_web_admin_args.pub_key_path = web_admin_crypto_loc.pub_path # type: ignore
                create_web_admin_args.priv_key_path = web_admin_crypto_loc.priv_path # type: ignore
                create_web_admin_args.ca_certs_path = web_admin_crypto_loc.ca_certs_path # type: ignore

            web_admin_password:'bytes' = CryptoManager.generate_password() # type: ignore
            admin_created = create_web_admin.Create(create_web_admin_args).execute(
                create_web_admin_args, False, web_admin_password, True)

            # Need to reset the logger here because executing the create_web_admin command
            # loads the Dashboard's logger which doesn't like that of ours.
            self.reset_logger(args, True)
            self.logger.info('[{}/{}] Dashboard created'.format(next(next_step), total_steps))
        else:
            admin_created = False

# ################################################################################################################################

        #
        # 7) Scheduler
        #

        # Creation of a scheduler is optional
        if should_create_scheduler:

            scheduler_path = os.path.join(args_path, 'scheduler')
            os.mkdir(scheduler_path)

            session = get_session(get_engine(args)) # type: ignore

            with closing(session):
                cluster_id:'int' = session.query(Cluster.id).\
                    filter(Cluster.name==cluster_name).\
                    one()[0]

            create_scheduler_args = self._bunch_from_args(args, admin_invoke_password, cluster_name)
            create_scheduler_args.path = scheduler_path
            create_scheduler_args.cluster_id = cluster_id
            create_scheduler_args.server_path = first_server_path
            create_scheduler_args.scheduler_api_client_for_server_auth_required = scheduler_api_client_for_server_auth_required
            create_scheduler_args.scheduler_api_client_for_server_username = scheduler_api_client_for_server_username
            create_scheduler_args.scheduler_api_client_for_server_password = scheduler_api_client_for_server_password

            if has_tls:
                create_scheduler_args.cert_path = scheduler_crypto_loc.cert_path # type: ignore
                create_scheduler_args.pub_key_path = scheduler_crypto_loc.pub_path # type: ignore
                create_scheduler_args.priv_key_path = scheduler_crypto_loc.priv_path # type: ignore
                create_scheduler_args.ca_certs_path = scheduler_crypto_loc.ca_certs_path # type: ignore

            _ = create_scheduler.Create(create_scheduler_args).execute(create_scheduler_args, False, True) # type: ignore
            self.logger.info('[{}/{}] Scheduler created'.format(next(next_step), total_steps))

# ################################################################################################################################

        #
        # 8) Scripts
        #
        zato_bin = 'zato.bat' if is_windows else 'zato'

        # Visual Studio integration
        vscode_dir = os.path.join(args_path, '.vscode')
        vscode_launch_json_path = os.path.join(vscode_dir, 'launch.json')
        vscode_settings_json_path = os.path.join(vscode_dir, 'settings.json')

        os.mkdir(vscode_dir)
        _ = open_w(vscode_launch_json_path).write(vscode_launch_json)
        _ = open_w(vscode_settings_json_path).write(vscode_settings_json)

        # This will exist for Windows and other systems
        zato_qs_start_path = 'zato-qs-start.bat' if is_windows else 'zato-qs-start.sh'
        zato_qs_start_path = os.path.join(args_path, zato_qs_start_path)

        # These commands are generated for non-Windows systems only
        zato_qs_stop_path = os.path.join(args_path, 'zato-qs-stop.sh')
        zato_qs_restart_path = os.path.join(args_path, 'zato-qs-restart.sh')

        check_config = []
        start_servers = []
        stop_servers = []

        if create_components_other_than_scheduler:
            for name in server_names: # type: ignore
                check_config.append(check_config_template.format(server_name=server_names[name]))
                start_servers.append(start_servers_template.format(server_name=server_names[name], step_number=int(name)+5))
                stop_servers.append(stop_servers_template.format(server_name=server_names[name], step_number=int(name)+1))

        check_config = '\n'.join(check_config)
        start_servers = '\n'.join(start_servers)
        stop_servers = '\n'.join(stop_servers)

        if scheduler_only:
            start_servers = '# No servers to start'
            start_lb = '# No load-balancer to start'
            check_config_extra = ''
            check_tcp_ports_suffix = 'scheduler-only'
            cluster_starting = ''
            cluster_started = ''
            cluster_stopping = ''
            cluster_stopped = ''
            check_config_step_number = 1
            scheduler_step_count = 2
            start_steps = 2
            stop_steps = 3
            start_scheduler = zato_qs_start_scheduler.format(scheduler_step_count=scheduler_step_count)
            stop_scheduler = zato_qs_stop_scheduler

        else:
            start_lb = zato_qs_start_lb_windows if is_windows else zato_qs_start_lb_non_windows
            check_config_extra = zato_qs_check_config_extra
            check_tcp_ports_suffix = ''
            cluster_starting = zato_qs_cluster_started
            cluster_started = zato_qs_cluster_started
            cluster_stopping = zato_qs_cluster_stopping
            cluster_stopped = zato_qs_cluster_stopped
            check_config_step_number = 3
            start_steps = 6 + servers
            stop_steps = 3 + servers
            scheduler_step_count = start_steps - 2

            if no_scheduler:
                start_steps -= 1
                stop_steps -= 1
                start_scheduler = '# No scheduler to start'
                stop_scheduler = '# No scheduler to stop'
            else:
                start_scheduler = zato_qs_start_scheduler.format(scheduler_step_count=scheduler_step_count)
                stop_scheduler = zato_qs_stop_scheduler

        web_admin_step_count = stop_steps
        if create_components_other_than_scheduler and should_create_scheduler:
            web_admin_step_count -= 1

        zato_qs_start_head = zato_qs_start_head_template.format(
            zato_bin=zato_bin,
            script_dir=script_dir,
            cluster_name=cluster_name,
            start_steps=start_steps,
            cluster_starting=cluster_starting,
        )

        zato_qs_start_body = zato_qs_start_body_template.format(
            check_config=check_config,
            check_config_extra=check_config_extra,
            check_tcp_ports_suffix=check_tcp_ports_suffix,
            start_lb=start_lb,
            scheduler_step_count=scheduler_step_count,
            start_servers=start_servers,
            check_config_step_number=check_config_step_number,
            start_scheduler=start_scheduler,
        )

        if scheduler_only:
            start_dashboard = ''
        else:
            start_dashboard = zato_qs_start_dashboard

        zato_qs_start_tail = zato_qs_start_tail_template.format(
            start_dashboard=start_dashboard,
            cluster_started=cluster_started,
        )
        zato_qs_start = zato_qs_start_head + zato_qs_start_body + zato_qs_start_tail

        zato_qs_stop = zato_qs_stop_template.format(
            zato_bin=zato_bin,
            script_dir=script_dir,
            cluster_name=cluster_name,
            web_admin_step_count=web_admin_step_count,
            stop_steps=stop_steps,
            stop_servers=stop_servers,
            cluster_stopping=cluster_stopping,
            cluster_stopped=cluster_stopped,
            stop_scheduler=stop_scheduler,
        )

        if is_windows:

            windows_qs_start = windows_qs_start_template.format(env_dir=args_path)
            _ = open_w(zato_qs_start_path).write(windows_qs_start)

        else:
            _ = open_w(zato_qs_start_path).write(zato_qs_start)
            _ = open_w(zato_qs_stop_path).write(zato_qs_stop)
            _ = open_w(zato_qs_restart_path).write(zato_qs_restart.format(script_dir=script_dir, cluster_name=cluster_name))

            file_mod = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP

            os.chmod(zato_qs_start_path, file_mod)
            os.chmod(zato_qs_stop_path, file_mod)
            os.chmod(zato_qs_restart_path, file_mod)

            self.logger.info('[{}/{}] Management scripts created'.format(next(next_step), total_steps))

        self.logger.info('Quickstart cluster {} created'.format(cluster_name))

        if admin_created:
            self.logger.info('Dashboard user:[admin], password:[%s]', web_admin_password.decode('utf8')) # type: ignore
        else:
            self.logger.info('User [admin] already exists in the ODB')

        self.logger.info('Start the cluster by issuing this command: %s', zato_qs_start_path)
        self.logger.info('Visit https://zato.io/support for more information and support options')

# ################################################################################################################################
# ################################################################################################################################
