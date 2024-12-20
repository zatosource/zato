# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.common.api import NotGiven
from zato.common.util.open_ import open_r, open_w

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, anydict, callnone, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Some objects are re-defined here to avoid importing them from zato.common = improves CLI performance.
class MS_SQL:
    ZATO_DIRECT = 'zato+mssql1'

ZATO_INFO_FILE = '.zato-info'

SUPPORTED_DB_TYPES = ('mysql', 'postgresql', 'sqlite')

# ################################################################################################################################

_opts_odb_type = 'Operational database type, must be one of {}'.format(SUPPORTED_DB_TYPES) # noqa
_opts_odb_host = 'Operational database host'
_opts_odb_port = 'Operational database port'
_opts_odb_user = 'Operational database user'
_opts_odb_schema = 'Operational database schema'
_opts_odb_db_name = 'Operational database name'

# ################################################################################################################################

ca_defaults = {
    'organization': 'My Company',
    'organizational_unit': 'My Unit', # When it's an optional argument
    'organizational-unit': 'My Unit', # When it's a required one
    'locality': 'My Town',
    'state_or_province': 'My State',
    'country': 'US'
}

# ################################################################################################################################

default_ca_name = 'Sample CA'
default_common_name = 'localhost'

# ################################################################################################################################

common_odb_opts = [
    {'name':'--odb-type', 'help':_opts_odb_type, 'choices':SUPPORTED_DB_TYPES, 'default':'sqlite'}, # noqa
    {'name':'--odb-host', 'help':_opts_odb_host},
    {'name':'--odb-port', 'help':_opts_odb_port},
    {'name':'--odb-user', 'help':_opts_odb_user},
    {'name':'--odb-db-name', 'help':_opts_odb_db_name},
    {'name':'--postgresql-schema', 'help':_opts_odb_schema + ' (PostgreSQL only)'},
    {'name':'--odb-password', 'help':'ODB database password', 'default':''},
]

common_ca_create_opts = [
    {'name':'--organization', 'help':'Organization name (defaults to {organization})'.format(**ca_defaults)},
    {'name':'--locality', 'help':'Locality name (defaults to {locality})'.format(**ca_defaults)},
    {'name':'--state-or-province', 'help':'State or province name (defaults to {state_or_province})'.format(**ca_defaults)},
    {'name':'--country', 'help':'Country (defaults to {country})'.format(**ca_defaults)},
    {'name':'--common-name', 'help':'Common name (defaults to {default})'.format(default=default_common_name)},
]

common_totp_opts = [
    {'name': 'username', 'help': 'Username to reset the TOTP secret key of'},
    {'name': '--key', 'help': 'Key to use'},
    {'name': '--key-label', 'help': 'Label to apply to the key'},
]

common_scheduler_server_address_opts = [
    {'name':'--scheduler-address-for-server', 'help':'Address of the scheduler for servers to invoke'},
    {'name':'--server-address-for-scheduler', 'help':'Address of the server for a scheduler to invoke'},
]

common_scheduler_server_api_client_opts = [
    {
        'name':'--scheduler-api-client-for-server-username',
        'help':'Name of the API user that the server connects to the scheduler with'
    },

    {
        'name':'--scheduler-api-client-for-server-password',
        'help':'Password of the API user that the server connects to the scheduler with'
    },

    {
        'name':'--server-api-client-for-scheduler-username',
        'help':'Name of the API user that the scheduler connects to the server with'
    },

    {
        'name':'--server-api-client-for-scheduler-password',
        'help':'Password of the API user that the scheduler connects to the server with'
    },
]

# ################################################################################################################################

sql_conf_contents = """
# ######### ######################## ######### #
# ######### Engines defined by Zato  ######### #
# ######### ######################## ######### #

[mysql+pymysql]
display_name=MySQL
ping_query=SELECT 1+1

[postgresql+pg8000]
display_name=PostgreSQL
ping_query=SELECT 1

[oracle]
display_name=Oracle
ping_query=SELECT 1 FROM dual

[{}]
display_name="MS SQL (Direct)"
ping_query=SELECT 1

# ######### ################################# ######### #
# ######### User-defined SQL engines go below ######### #
# ######### ################################# ######### #

#[label]
#friendly_name=My DB
#sqlalchemy_driver=sa-name
""".lstrip().format(MS_SQL.ZATO_DIRECT) # nopep8

# ################################################################################################################################

command_imports = (
    ('apispec', 'zato.cli.apispec.APISpec'),
    ('ca_create_ca', 'zato.cli.ca_create_ca.Create'),
    ('ca_create_lb_agent', 'zato.cli.ca_create_lb_agent.Create'),
    ('ca_create_scheduler', 'zato.cli.ca_create_scheduler.Create'),
    ('ca_create_server', 'zato.cli.ca_create_server.Create'),
    ('ca_create_web_admin', 'zato.cli.ca_create_web_admin.Create'),
    ('cache_delete', 'zato.cli.cache.CacheDelete'),
    ('cache_get', 'zato.cli.cache.CacheGet'),
    ('cache_set', 'zato.cli.cache.CacheSet'),
    ('change_password', 'zato.cli.security.basic_auth.ChangePassword'),
    ('check_config', 'zato.cli.check_config.CheckConfig'),
    ('component_version', 'zato.cli.component_version.ComponentVersion'),
    ('create_api_key', 'zato.cli.security.api_key.CreateDefinition'),
    ('create_basic_auth', 'zato.cli.security.basic_auth.CreateDefinition'),
    ('create_cluster', 'zato.cli.create_cluster.Create'),
    ('create_lb', 'zato.cli.create_lb.Create'),
    ('create_odb', 'zato.cli.create_odb.Create'),
    ('create_rest_channel', 'zato.cli.rest.channel.CreateChannel'),
    ('create_scheduler', 'zato.cli.create_scheduler.Create'),
    ('create_server', 'zato.cli.create_server.Create'),
    ('create_secret_key', 'zato.cli.crypto.CreateSecretKey'),
    ('create_user', 'zato.cli.web_admin_auth.CreateUser'),
    ('create_web_admin', 'zato.cli.create_web_admin.Create'),
    ('create_wsx_channel', 'zato.cli.wsx.CreateChannel'),
    ('create_wsx_outconn', 'zato.cli.wsx.CreateOutconn'),
    ('crypto_create_secret_key', 'zato.cli.crypto.CreateSecretKey'),
    ('delete_odb', 'zato.cli.delete_odb.Delete'),
    ('delete_api_key', 'zato.cli.security.api_key.DeleteDefinition'),
    ('delete_basic_auth', 'zato.cli.security.basic_auth.DeleteDefinition'),
    ('delete_rest_channel', 'zato.cli.rest.channel.DeleteChannel'),
    ('delete_wsx_channel', 'zato.cli.wsx.DeleteChannel'),
    ('delete_wsx_outconn', 'zato.cli.wsx.DeleteOutconn'),
    ('decrypt', 'zato.cli.crypto.Decrypt'),
    ('encrypt', 'zato.cli.crypto.Encrypt'),
    ('enmasse', 'zato.cli.enmasse.Enmasse'),
    ('from_config', 'zato.cli.FromConfig'),
    ('hash_get_rounds', 'zato.cli.crypto.GetHashRounds'),
    ('hl7_mllp_send', 'zato.cli.hl7_.MLLPSend'),
    ('info', 'zato.cli.info.Info'),
    ('openapi', 'zato.cli.openapi_.OpenAPI'),
    ('pubsub_cleanup', 'zato.cli.pubsub.cleanup.Cleanup'),
    ('pubsub_create_endpoint', 'zato.cli.pubsub.endpoint.CreateEndpoint'),
    ('pubsub_create_topic', 'zato.cli.pubsub.topic.CreateTopic'),
    ('pubsub_create_test_topics', 'zato.cli.pubsub.topic.CreateTestTopics'),
    ('pubsub_delete_endpoint', 'zato.cli.pubsub.endpoint.DeleteEndpoint'),
    ('pubsub_delete_topic', 'zato.cli.pubsub.topic.DeleteTopics'),
    ('pubsub_delete_topics', 'zato.cli.pubsub.topic.DeleteTopics'),
    ('pubsub_get_topic', 'zato.cli.pubsub.topic.GetTopics'),
    ('pubsub_get_topics', 'zato.cli.pubsub.topic.GetTopics'),
    ('reset_totp_key', 'zato.cli.web_admin_auth.ResetTOTPKey'),
    ('quickstart_create', 'zato.cli.quickstart.Create'),
    ('service_invoke', 'zato.cli.service.Invoke'),
    ('set_ide_password', 'zato.cli.ide.SetIDEPassword'),
    ('set_admin_invoke_password', 'zato.cli.web_admin_auth.SetAdminInvokePassword'),
    ('sso_change_user_password', 'zato.cli.sso.ChangeUserPassword'),
    ('sso_create_odb', 'zato.cli.sso.CreateODB'),
    ('sso_create_user', 'zato.cli.sso.CreateUser'),
    ('sso_create_super_user', 'zato.cli.sso.CreateSuperUser'),
    ('sso_delete_user', 'zato.cli.sso.DeleteUser'),
    ('sso_login', 'zato.cli.sso.Login'),
    ('sso_logout', 'zato.cli.sso.Logout'),
    ('sso_lock_user', 'zato.cli.sso.LockUser'),
    ('sso_reset_totp_key', 'zato.cli.sso.ResetTOTPKey'),
    ('sso_reset_user_password', 'zato.cli.sso.ResetUserPassword'),
    ('sso_unlock_user', 'zato.cli.sso.UnlockUser'),
    ('start', 'zato.cli.start.Start'),
    ('stop', 'zato.cli.stop.Stop'),
    ('update_password', 'zato.cli.web_admin_auth.UpdatePassword'),
    ('wait', 'zato.cli.wait.Wait'),
)

# ################################################################################################################################

def run_command(args):

    # Zato
    from zato.common.util.import_ import import_string

    # This may be needed in two places.
    sorted_command_imports = sorted(command_imports)

    # Iterate over all the commands that we know ..
    for command_name, class_dotted_name in sorted_command_imports:

        # Try to match the command given with our configuration ..
        if command_name == args.command:
            class_ = import_string(class_dotted_name)
            instance = class_(args)

            # .. we found a match so we can run the command.
            return instance.run(args)

    # .. if we are here, it means that configuration from zato_command.py does not much our.
    else:
        raise Exception('Could not find `{}` among `{}`'.format(args.command, [elem[0] for elem in sorted_command_imports]))

# ################################################################################################################################

class ZatoCommand:
    """ A base class for all Zato CLI commands. Handles common things like parsing
    the arguments, checking whether a config file or command line switches should
    be used, asks for passwords etc.
    """
    needs_empty_dir = False
    file_needed = None
    needs_secrets_confirm = True
    add_config_file = True
    target_dir = None
    show_output = True
    opts = []

# ################################################################################################################################

    class SYS_ERROR:
        """ All non-zero sys.exit return codes the commands may use.
        """
        ODB_EXISTS = 1
        FILE_MISSING = 2
        NOT_A_ZATO_COMPONENT = 3
        NO_ODB_FOUND = 4
        DIR_NOT_EMPTY = 5
        CLUSTER_NAME_ALREADY_EXISTS = 6
        SERVER_NAME_ALREADY_EXISTS = 7
        NO_SUCH_CLUSTER = 8
        COMPONENT_ALREADY_RUNNING = 9
        NO_PID_FOUND = 10
        NO_SUCH_WEB_ADMIN_USER = 11
        NO_INPUT = 12
        CONFLICTING_OPTIONS = 13
        NO_OPTIONS = 14
        INVALID_INPUT = 15
        EXCEPTION_CAUGHT = 16
        CANNOT_MIGRATE = 17
        FAILED_TO_START = 18
        FOUND_PIDFILE = 19
        USER_EXISTS = 20
        VALIDATION_ERROR = 21
        NO_SUCH_SSO_USER = 22
        NOT_A_ZATO_SERVER = 23
        NOT_A_ZATO_WEB_ADMIN = 24
        NOT_A_ZATO_LB = 25
        NOT_A_ZATO_SCHEDULER = 26
        CACHE_KEY_NOT_FOUND = 27
        SERVER_TIMEOUT = 28
        PARAMETER_MISSING = 29
        PATH_NOT_A_FILE = 30
        NO_SUCH_PATH = 31

# ################################################################################################################################

    class COMPONENTS:

        class _ComponentName:
            def __init__(self, code, name):
                self.code = code
                self.name = name

        CA = _ComponentName('CA', 'Certificate authority')
        LOAD_BALANCER = _ComponentName('LOAD_BALANCER', 'Load balancer')
        SCHEDULER = _ComponentName('SCHEDULER', 'Scheduler')
        SERVER = _ComponentName('SERVER', 'Server')
        WEB_ADMIN = _ComponentName('WEB_ADMIN', 'Dashboard')

# ################################################################################################################################

    def __init__(self, args):

        # stdlib
        import os

        # Zato
        from zato.common.util.cli import read_stdin_data

        self.args = args
        self.original_dir = os.getcwd()
        self.show_output = False if 'ZATO_CLI_DONT_SHOW_OUTPUT' in os.environ else True
        self.verbose = args.verbose
        self.reset_logger(args)
        self.engine = None

        if args.store_config:
            self.store_config(args)

        # Get input from sys.stdin, if any was provided at all. It needs to be read once here,
        # because subprocesses will not be able to do it once we read it all in in the parent
        # one, so we read it here and give other processes explicitly on input, if they need it.
        self.stdin_data = read_stdin_data()

# ################################################################################################################################

    def exit(self, exit_code:'int'=0) -> 'None':

        # stdlib
        import sys

        _ = sys.exit(exit_code)

# ################################################################################################################################

    def allow_empty_secrets(self):
        return False

# ################################################################################################################################

    def get_arg(self, name:'str', default:'any_'='') -> 'any_':
        if hasattr(self.args, 'get'):
            return self.args.get(name) or default
        else:
            return getattr(self.args, name, default)

# ################################################################################################################################

    def _extract_address_data(
        self,
        args:'any_',
        main_arg_name:'str',
        host_arg_name:'str',
        port_arg_name:'str',
        default_host:'str',
        default_port:'int'
    ) -> 'any_':

        # stdlib
        from urllib.parse import urlparse

        # Local variables
        use_tls = NotGiven

        # Try to extract the scheduler's address from a single option
        if address := getattr(args, main_arg_name, None):

            # Make sure we have a scheme ..
            if not '://' in address:
                address = 'https://' + address

            # .. parse out the individual components ..
            address = urlparse(address)

            # .. now we know if TLS should be used ..
            use_tls = address.scheme == 'https'

            # .. extract the host and port ..
            address = address.netloc.split(':')
            host = address[0]

            if len(address) == 2:
                port = address[1]
                port = int(port)
            else:
                port = default_port

        else:
            # Extract the scheduler's address from individual pieces
            host = self.get_arg(host_arg_name, default_host)
            port = self.get_arg(port_arg_name, default_port)

        if use_tls is NotGiven:
            use_tls = False

        return use_tls, host, port

# ################################################################################################################################

    def _encrypt(self, CryptoManagerClass, args, to_encrypt=None, needs_log_info=True):

        # stdlib
        import os

        os.chdir(self.original_dir)
        repo_dir = os.path.abspath(os.path.join(args.path, 'config', 'repo'))
        cm = CryptoManagerClass(repo_dir=repo_dir)

        encrypted = cm.encrypt(to_encrypt or args.data)

        if needs_log_info:
            self.logger.info(encrypted.decode('utf8'))

        return encrypted

# ################################################################################################################################

    def reset_logger(self, args, reload_=False):

        # stdlib
        import logging
        import sys
        from importlib import reload

        # Zato
        from zato.common.util.file_system import fs_safe_now

        if reload_:
            logging.shutdown() # noqa
            reload(logging) # noqa

        self.logger = logging.getLogger(self.__class__.__name__) # noqa
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO) # noqa
        self.logger.handlers[:] = []

        console_handler = logging.StreamHandler(sys.stdout) # noqa
        console_formatter = logging.Formatter('%(message)s') # noqa
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        if args.store_log:
            verbose_handler = logging.FileHandler('zato.{}.log'.format(fs_safe_now())) # noqa
            verbose_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # noqa
            verbose_handler.setFormatter(verbose_formatter)
            self.logger.addHandler(verbose_handler)

# ################################################################################################################################

    def _get_secret(self, template, needs_confirm, allow_empty, secret_name='password'):
        """ Runs an infinite loop until a user enters the secret. User needs
        to confirm the secret if 'needs_confirm' is True. New line characters
        are always stripped before returning the secret, so that "\n" becomes
        "", "\nsecret\n" becomes "secret" and "\nsec\nret\n" becomes "sec\nret".
        """

        # stdlib
        from getpass import getpass

        self.logger.info('')

        while True:
            secret1 = getpass(template + ' (will not echo): ')
            if not needs_confirm:
                return secret1.strip('\n')

            secret2 = getpass('{} again (will not echo): '.format(template))

            if secret1 != secret2:
                self.logger.info('{}s do not match'.format(template))
            else:
                if not secret1 and not allow_empty:
                    self.logger.info('No {} entered'.format(secret_name))
                else:
                    return secret1.strip('\n')

# ################################################################################################################################

    def get_confirmation(self, template, yes_char='y', no_char='n'):

        # stdlib
        from builtins import input as raw_input

        template = '{} [{}/{}] '.format(template, yes_char, no_char)
        while True:
            value = raw_input(template)
            if value == yes_char:
                return True
            elif value == no_char:
                return False

# ################################################################################################################################

    def _get_now(self, time_=None):

        # stdlib
        import time

        if not time_:
            time_ = time.gmtime() # noqa

        return time.strftime('%Y-%m-%d_%H-%M-%S', time_) # noqa

# ################################################################################################################################

    def _get_user_host(self):

        # stdlib
        from getpass import getuser
        from socket import gethostname

        return getuser() + '@' + gethostname()

# ################################################################################################################################

    def store_initial_info(self, target_dir, component):

        # stdlib
        import os
        from datetime import datetime

        # Zato
        from zato.common.json_internal import dumps
        from zato.common.version import get_version

        zato_version = get_version()

        info = {'version': zato_version, # noqa
                'created_user_host': self._get_user_host(),
                'created_ts': datetime.utcnow().isoformat(), # noqa
                'component': component
                }
        open_w(os.path.join(target_dir, ZATO_INFO_FILE)).write(dumps(info))

# ################################################################################################################################

    def store_config(self, args):
        """ Stores the config options in a config file for a later use.
        """

        # stdlib
        import os
        from io import StringIO

        # Zato
        from zato.common.util.file_system import fs_safe_now

        now = fs_safe_now() # noqa
        file_name = 'zato.{}.config'.format(now)
        file_args = StringIO()

        for arg, value in args._get_kwargs():
            if value:
                file_args.write('{}={}\n'.format(arg, value))

        body = '# {} - {}\n{}'.format(now, self._get_user_host(), file_args.getvalue())

        open_w(file_name).write(body)
        file_args.close()

        self.logger.debug('Options saved in file {file_name}'.format(
            file_name=os.path.abspath(file_name)))

# ################################################################################################################################

    def _get_engine(self, args):

        # SQLAlchemy
        import sqlalchemy

        # Zato
        from zato.common.util import api as util_api
        from zato.common.util.api import get_engine_url

        if not args.odb_type.startswith('postgresql'):
            connect_args = {}
        else:
            connect_args = {'application_name':util_api.get_component_name('enmasse')}

        return sqlalchemy.create_engine(get_engine_url(args), connect_args=connect_args)

# ################################################################################################################################

    def _get_session(self, engine):

        # Zato
        from zato.common.util.api import get_session

        return get_session(engine)

# ################################################################################################################################

    def _check_passwords(self, args, check_password):
        """ Get the password from a user for each argument that needs a password.
        """
        for opt_name, opt_help in check_password:
            opt_name = opt_name.replace('--', '').replace('-', '_')
            password_arg = getattr(args, opt_name, None)

            # It is OK if password is an empty string and empty secrets are allowed
            if not password_arg:

                if isinstance(self.allow_empty_secrets, bool):
                    allow_empty = self.allow_empty_secrets
                else:
                    allow_empty = self.allow_empty_secrets()

                if allow_empty:
                    continue

                password = self._get_secret(opt_help, self.needs_secrets_confirm, allow_empty, opt_name)
                setattr(args, opt_name, password)

        return args

# ################################################################################################################################

    def _get_arg(self, args, name, default):
        value = getattr(args, name, None)
        return value if value else default

# ################################################################################################################################

    def run(self, args, offer_save_opts=True, work_args=None, needs_sys_exit=True):
        """ Parses the command line or the args passed in and figures out
        whether the user wishes to use a config file or command line switches.
        """

        # stdlib
        import os
        import sys

        try:
            # Do we need to have a clean directory to work in?
            if self.needs_empty_dir:
                work_dir = os.path.abspath(args.path)

                if not os.path.exists(work_dir):
                    self.logger.info('Creating directory `%s`', work_dir)
                    os.makedirs(work_dir)

                for elem in os.listdir(work_dir):
                    if elem.startswith('zato') and elem.endswith('config'):
                        # This is a zato.{}.config file. The had been written there
                        # before we got to this point and it's OK to skip it.
                        continue
                    else:
                        self.logger.info('Directory `%s` is not empty, please choose a different one or empty it out', work_dir)
                        sys.exit(self.SYS_ERROR.DIR_NOT_EMPTY) # noqa

            # Do we need the directory to contain any specific files?
            if self.file_needed:
                full_path = os.path.join(args.path, self.file_needed)
                if not os.path.exists(full_path):
                    msg = 'Could not find file {}'.format(full_path)
                    self.logger.info(msg)
                    sys.exit(self.SYS_ERROR.FILE_MISSING) # noqa

            check_password = []
            for opt_dict in self.opts:
                name = opt_dict['name']
                if 'password' in name or 'secret' in name:

                    # Don't require a component's secret key
                    if name == '--secret-key':
                        continue

                    # Don't require passwords with SQLite
                    if 'odb' in name and args.odb_type == 'sqlite':
                        continue

                    check_password.append((name, opt_dict['help']))

            self.before_execute(args)

            if check_password and self.is_password_required():
                args = self._check_passwords(args, check_password)

            # GH #328 - zato create web_admin treats boolean admin_created as an exit code
            # https://github.com/zatosource/zato/issues/328

            return_code = self.execute(args)
            if needs_sys_exit:
                if isinstance(return_code, int):
                    sys.exit(return_code)
                else:
                    sys.exit(0)

        except Exception as e:
            self.reset_logger(self.args)
            if self.verbose:

                # Zato
                from zato.common.util.python_ import get_full_stack
                msg = get_full_stack()

            else:
                msg = '{}: {} (Hint: re-run with --verbose for full traceback)'.format(e.__class__.__name__, e.args)
            self.logger.error(msg)
            sys.exit(self.SYS_ERROR.EXCEPTION_CAUGHT)

# ################################################################################################################################

    def is_password_required(self):
        return True

# ################################################################################################################################

    def before_execute(self, args):
        """ A hooks that lets commands customize their input before they are actually executed.
        """
        # Update odb_type if it's MySQL so that users don't have to think about the particular client implementation.
        if getattr(args, 'odb_type', None) == 'mysql':
            args.odb_type = 'mysql+pymysql'

# ################################################################################################################################

    def _copy_crypto(self, repo_dir, args, middle_part):

        # stdlib
        import shutil
        import os

        for name in('pub-key', 'priv-key', 'cert', 'ca-certs'):
            arg_name = '{}_path'.format(name.replace('-', '_'))
            target_path = os.path.join(repo_dir, 'zato-{}-{}.pem'.format(middle_part, name))

            source_path = getattr(args, arg_name, None)
            if source_path:
                source_path = os.path.abspath(source_path)
                if os.path.exists(source_path):
                    shutil.copyfile(source_path, target_path)

# ################################################################################################################################

    def copy_lb_crypto(self, repo_dir, args):
        self._copy_crypto(repo_dir, args, 'lba')

# ################################################################################################################################

    def copy_server_crypto(self, repo_dir, args):
        self._copy_crypto(repo_dir, args, 'server')

# ################################################################################################################################

    def copy_scheduler_crypto(self, repo_dir, args):
        self._copy_crypto(repo_dir, args, 'scheduler')

# ################################################################################################################################

    def copy_web_admin_crypto(self, repo_dir, args):

        # stdlib
        import shutil
        import os

        for attr, name in (('pub_key_path', 'pub-key'), ('priv_key_path', 'priv-key'), ('cert_path', 'cert'),
            ('ca_certs_path', 'ca-certs')):
            file_name = os.path.join(repo_dir, 'web-admin-{}.pem'.format(name))
            shutil.copyfile(os.path.abspath(getattr(args, attr)), file_name)

# ################################################################################################################################

    def get_crypto_manager_from_server_config(self, config, repo_dir):

        # Zato
        from zato.common.util.api import get_crypto_manager_from_server_config

        return get_crypto_manager_from_server_config(config, repo_dir)

# ################################################################################################################################

    def get_odb_session_from_server_config(self, config, cm):

        # Zato
        from zato.common.util.api import get_odb_session_from_server_config

        return get_odb_session_from_server_config(config, cm, False)

# ################################################################################################################################

    def ensure_path_is_a_server(self, path):

        # stdlib
        import os
        import sys

        # Zato
        from zato.common.util.api import get_config

        repo_location = os.path.join(path, 'config', 'repo')
        secrets_conf = get_config(repo_location, 'secrets.conf', needs_user_config=False)

        # This file must exist, otherwise it's not a path to a server
        if not secrets_conf:
            self.logger.warning('No server found at `%s`', path)
            sys.exit(self.SYS_ERROR.NOT_A_ZATO_SERVER)

# ################################################################################################################################

class FromConfig(ZatoCommand):
    """ Executes commands from a command config file.
    """
    def execute(self, args):
        """ Runs the command with arguments read from a config file.
        """
        f = open_r(args.path)
        for line in f:
            if line.lstrip().startswith('#'):
                continue
            arg, value = line.split('=', 1)

            arg = arg.strip()
            value = value.strip()

            setattr(args, arg, value)

        run_command(args)

# ################################################################################################################################

class CACreateCommand(ZatoCommand):
    """ A base class for all commands that create new crypto material.
    """
    file_needed = '.zato-ca-dir'

# ################################################################################################################################

    def __init__(self, args):

        # stdlib
        import os

        super(CACreateCommand, self).__init__(args)
        self.target_dir = os.path.abspath(args.path)

# ################################################################################################################################

    def _on_file_missing(self):
        msg = "{} doesn't seem to be a CA directory, the '{}' file is missing."
        return msg.format(self.target_dir, self.file_needed)

# ################################################################################################################################

    def _execute(self, args, extension, show_output=True):

        # stdlib
        import os
        import tempfile

        now = self._get_now()
        openssl_template = open_r(os.path.join(self.target_dir, 'ca-material', 'openssl-template.conf')).read()

        ou_attrs = ('organizational_unit', 'organizational-unit')
        template_args = {}
        for name in('organization', 'locality', 'state_or_province', 'country'):
            value = self._get_arg(args, name, ca_defaults[name])
            template_args[name.replace('-', '_')] = value

        for name in ou_attrs:
            has_name = self._get_arg(args, name, None)
            if has_name:
                value = self._get_arg(args, name, ca_defaults[name])
                template_args[name.replace('-', '_')] = value
                break
        else:
            if hasattr(self, 'get_organizational_unit'):
                template_args['organizational_unit'] = self.get_organizational_unit(args)
            else:
                template_args['organizational_unit'] = ca_defaults['organizational_unit']

        template_args['common_name'] = self._get_arg(args, 'common_name', default_common_name)
        template_args['target_dir'] = self.target_dir

        template_args['ca_serial'] = '$dir/ca-material/ca-serial'
        template_args['ca_certindex'] = '$dir/ca-material/ca-certindex'
        template_args['target_dir_rel'] = '$dir'
        template_args['ca_key'] = '$dir/ca-material/ca-cert.pem'
        template_args['private_key'] = '$dir/ca-material/ca-key.pem'

        import platform
        system = platform.system()
        is_windows = 'windows' in system.lower()

        if is_windows:
            template_args['ca_serial'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-serial')).replace('\\','/')
            template_args['ca_certindex'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-certindex')).replace('\\','/')
            template_args['target_dir_rel'] = os.path.relpath(self.target_dir).replace('\\','/')
            template_args['ca_key'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-cert.pem')).replace('\\','/')
            template_args['private_key'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-key.pem')).replace('\\','/')

        f = tempfile.NamedTemporaryFile(mode='w+') # noqa
        f.write(openssl_template.format(**template_args))
        f.flush()

        file_args = {
            'now':now,
            'target_dir':self.target_dir
        }

        for arg in('cluster_name', 'server_name', 'scheduler_name'):
            if hasattr(args, arg):
                file_args[arg] = getattr(args, arg)

        file_args['file_prefix'] = self.get_file_prefix(file_args)

        csr_name = os.path.join(self.target_dir, 'out-csr', '{file_prefix}-csr-{now}.pem'.format(**file_args))
        priv_key_name = os.path.join(self.target_dir, 'out-priv', '{file_prefix}-priv-{now}.pem'.format(**file_args))
        pub_key_name = os.path.join(self.target_dir, 'out-pub', '{file_prefix}-pub-{now}.pem'.format(**file_args))
        cert_name = os.path.join(self.target_dir, 'out-cert', '{file_prefix}-cert-{now}.pem'.format(**file_args))

        format_args = {
            'config': f.name,
            'extension': extension,
            'csr_name': csr_name,
            'priv_key_name': priv_key_name,
            'pub_key_name': pub_key_name,
            'cert_name': cert_name,
            'target_dir': self.target_dir,
            'ca_password': os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-password'))
        }
        if is_windows:
            format_args['ca_password'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-password')).replace('\\','\\\\')

        # Create the CSR and keys ..
        cmd = """openssl req -batch -new -nodes -extensions {extension} \
                  -out {csr_name} \
                  -keyout {priv_key_name} \
                  -pubkey \
                  -newkey rsa:2048 -config {config} """.format(**format_args)
        os.system(cmd)

        # .. note that we were using "-pubkey" flag above so we now have to extract
        # the public key from the CSR.

        split_line = '-----END PUBLIC KEY-----'
        csr_pub = open_r(csr_name).read()
        csr_pub = csr_pub.split(split_line)

        pub = csr_pub[0] + split_line
        csr = csr_pub[1].lstrip()

        open_w(csr_name).write(csr)
        open_w(pub_key_name).write(pub)

        # Generate the certificate
        cmd = """openssl ca -batch -passin file:{ca_password} -config {config} \
                 -out {cert_name} \
                 -extensions {extension} \
                 -in {csr_name}""".format(**format_args)

        os.system(cmd)
        f.close()

        # Now delete the default certificate stored in '.\', we don't really
        # need it because we have its copy in '.\out-cert' anyway.
        last_serial = open_r(os.path.join(self.target_dir, 'ca-material', 'ca-serial.old')).read().strip()
        os.remove(os.path.join(self.target_dir, last_serial + '.pem'))

        msg = """Crypto material generated and saved in:
  - private key: {priv_key_name}
  - public key: {pub_key_name}
  - certificate {cert_name}
  - CSR: {csr_name}""".format(**format_args)

        if show_output:
            if self.verbose:
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

        # Make sure permissions are tight (GH #440)
        os.chmod(priv_key_name, 0o640)

        # In case someone needs to invoke us directly and wants to find out
        # what the format_args were.
        return format_args

# ################################################################################################################################

class ManageCommand(ZatoCommand):
    add_config_file = False

# ################################################################################################################################

    def _get_dispatch(self):
        return {
            self.COMPONENTS.LOAD_BALANCER.code: self._on_lb,
            self.COMPONENTS.SERVER.code: self._on_server,
            self.COMPONENTS.WEB_ADMIN.code: self._on_web_admin,
            self.COMPONENTS.SCHEDULER.code: self._on_scheduler,
        }

    command_files = {ZATO_INFO_FILE}

# ################################################################################################################################

    def _on_lb(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError('Should be implemented by subclasses')

# ################################################################################################################################

    _on_web_admin = _on_server = _on_scheduler = _on_lb

# ################################################################################################################################

    def execute(self, args):

        # pylint: disable=attribute-defined-outside-init

        # stdlib
        import os
        import sys

        # Zato
        from zato.common.json_internal import load

        args_path = os.path.expanduser(args.path)
        args_path = os.path.expandvars(args_path)

        self.component_dir = os.path.abspath(args_path)
        self.config_dir = os.path.join(self.component_dir, 'config')
        listing = set(os.listdir(self.component_dir))

        # Do we have any files we're looking for?
        found = self.command_files & listing

        if not found:
            msg = """Directory {} doesn't seem to belong to a Zato component. Expected one of the following to exist {}""".format(
                self.component_dir, sorted(self.command_files))
            self.logger.info(msg)
            sys.exit(self.SYS_ERROR.NOT_A_ZATO_COMPONENT) # noqa

        found = list(found)[0]
        with open_r(os.path.join(self.component_dir, found)) as f:
            json_data = load(f)

        os.chdir(self.component_dir)

        handler = self._get_dispatch()[json_data['component']]
        return handler(args)

# ################################################################################################################################

def is_arg_given(args, *arg_names):

    for arg_name in arg_names:
        try:
            result = args.get(arg_name)
            if result:
                return True
        except AttributeError:
            result = getattr(args, arg_name, None)
            if result:
                return True

# ################################################################################################################################
# ################################################################################################################################

class ServerAwareCommand(ZatoCommand):
    """ A subclass that knows how to assign a Zato client object based on command line arguments.
    """
    zato_client: 'ZatoClient'

    def before_execute(self, args):

        # stdlib
        import os

        # Zato
        from zato.common.util.api import get_client_from_server_conf

        server_path = args.path or '.'
        server_path = os.path.abspath(server_path)

        # This will exist the process if path does not point to a server
        self.ensure_path_is_a_server(server_path)

        self.zato_client = get_client_from_server_conf(server_path)

# ################################################################################################################################

    def _invoke_service(
        self,
        service:'str',
        request:'anydict',
        hook_func:'callnone'=None
    ) -> 'stranydict':

        # Pass all the data to the underlying service and get its response ..
        response = self.zato_client.invoke(**{
            'name':    service,
            'payload': request
        })

        # We enter here if there is genuine business data to process
        if response.data:

            # .. let's extract it ..
            data = response.data

            # .. if we have a hook callable to pre-process data, let's invoke it ..
            if hook_func:
                data = hook_func(data)

        # We enter here if there was an invocation error
        else:
            data = response.details or '{}'
            data = loads(data)

        return data

# ################################################################################################################################

    def _log_response(
        self,
        data:'any_',
        needs_stdout:'bool'=True
    ) -> 'None':

        # stdlib
        import sys

        # We are ready to serialize the data to JSON ..
        data = dumps(data, indent=2)

        # .. no matter what data we have, we can log it now if we are told to do so.
        if needs_stdout:
            sys.stdout.write(data + '\n')

# ################################################################################################################################

    def _invoke_service_and_log_response(
        self,
        service:'str',
        request:'anydict',
        hook_func:'callnone'=None,
        needs_stdout:'bool'=True
    ) -> 'any_':

        # Invoke the service first ..
        data = self._invoke_service(service, request, hook_func)

        # .. log its output ..
        self._log_response(data, needs_stdout)

        # .. and return the output to our caller.
        return data

# ################################################################################################################################
# ################################################################################################################################
