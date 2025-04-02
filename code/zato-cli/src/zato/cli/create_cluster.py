# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# type: ignore

# stdlib
import os
import random
from copy import deepcopy

# Zato
from zato.cli import common_odb_opts, is_arg_given, ZatoCommand
from zato.common.api import DATA_FORMAT, SSO
from zato.common.const import ServiceConst

# ################################################################################################################################

zato_services = {

    # Hot-deploy
    'zato.hot-deploy.create': 'zato.server.service.internal.hot_deploy.Create',
    'zato.ide-deploy.create': 'zato.server.service.internal.ide_deploy.Create',

    # JWT
    'zato.security.jwt.auto-clean-up':'zato.server.service.internal.security.jwt.AutoCleanUp',
    'zato.security.jwt.change-password':'zato.server.service.internal.security.jwt.ChangePassword',
    'zato.security.jwt.create':'zato.server.service.internal.security.jwt.Create',
    'zato.security.jwt.delete':'zato.server.service.internal.security.jwt.Delete',
    'zato.security.jwt.edit':'zato.server.service.internal.security.jwt.Edit',
    'zato.security.jwt.get-list':'zato.server.service.internal.security.jwt.GetList',
    'zato.security.jwt.log-in':'zato.server.service.internal.security.jwt.LogIn',
    'zato.security.jwt.log-out':'zato.server.service.internal.security.jwt.LogOut',

    # Service invocations
    'zato.service.invoke':'zato.server.service.internal.service.Invoke',
    'pub.zato.service.service-invoker':'zato.server.service.internal.service.ServiceInvoker',

}

# ################################################################################################################################

def get_random_integer():
    return random.randint(100_000, 1_000_000)

# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates a new Zato cluster in the ODB
    """
    opts = deepcopy(common_odb_opts)

    opts.append({'name':'cluster_name', 'help':'Name of the cluster to create'})
    opts.append({'name':'--lb-host', 'help':'Load-balancer host', 'default':'127.0.0.1'})
    opts.append({'name':'--lb-port', 'help':'Load-balancer port', 'default':'11223'})
    opts.append({'name':'--lb-agent_port', 'help':'Load-balancer agent\'s port', 'default':'20151'})
    opts.append({'name':'--secret-key', 'help':'Secret key that servers will use for decryption and decryption'})
    opts.append({'name':'--admin-invoke-password', 'help':'Password for config API clients to connect to servers with'})
    opts.append({'name':'--skip-if-exists',
        'help':'Return without raising an error if cluster already exists', 'action':'store_true'})

# ################################################################################################################################

    def execute(self, args, show_output=True):

        # stdlib
        from datetime import datetime
        from traceback import format_exc

        # SQLAlchemy
        from sqlalchemy.exc import IntegrityError

        # Zato
        from zato.common.api import IDEDeploy
        from zato.common.odb.model import Cluster, HTTPBasicAuth
        from zato.common.odb.post_process import ODBPostProcess
        from zato.common.pubsub import PUBSUB

        _pubsub_default = PUBSUB.DEFAULT

        engine = self._get_engine(args)
        session = self._get_session(engine)

        if engine.dialect.has_table(engine.connect(), 'install_state'):
            if is_arg_given(args, 'skip-if-exists', 'skip_if_exists'):
                if show_output:
                    if self.verbose:
                        self.logger.debug('Cluster already exists, skipped its creation')
                    else:
                        self.logger.info('OK')
                return

        with session.no_autoflush:

            cluster = Cluster()
            cluster.name = args.cluster_name
            cluster.description = 'Created by {} on {} (UTC)'.format(self._get_user_host(), datetime.utcnow().isoformat())

            for name in(
                  'odb_type', 'odb_host', 'odb_port', 'odb_user', 'odb_db_name',
                  'lb_host', 'lb_port', 'lb_agent_port'):
                setattr(cluster, name, getattr(args, name))
            session.add(cluster)

            # With a cluster object in place, we can construct the ODB post-processor
            odb_post_process = ODBPostProcess(session, cluster, None)

            # admin.invoke user's password may be possibly in one of these attributes,
            # but if it is now, generate a new one.

            admin_invoke_password = getattr(args, 'admin-invoke-password', None)

            if not admin_invoke_password:
                admin_invoke_password = getattr(args, 'admin_invoke_password', None)

            if not admin_invoke_password:
                admin_invoke_password = self.generate_password()

            admin_invoke_sec = HTTPBasicAuth(None, ServiceConst.API_Admin_Invoke_Username, True,
                ServiceConst.API_Admin_Invoke_Username, 'Zato admin invoke', admin_invoke_password, cluster)
            session.add(admin_invoke_sec)

            pubapi_sec = HTTPBasicAuth(None, _pubsub_default.PUBAPI_SECDEF_NAME, True, _pubsub_default.PUBAPI_USERNAME,
                'Zato public API', self.generate_password(), cluster)
            session.add(pubapi_sec)

            internal_invoke_sec = HTTPBasicAuth(None, 'zato.internal.invoke', True, 'zato.internal.invoke.user',
                'Zato internal invoker', self.generate_password(), cluster)
            session.add(internal_invoke_sec)

            self.add_default_rbac_permissions(session, cluster)
            root_rbac_role = self.add_default_rbac_roles(session, cluster)
            ide_pub_rbac_role = self.add_rbac_role_and_acct(
                session, cluster, root_rbac_role, 'IDE Publishers', IDEDeploy.Username, IDEDeploy.Username)

            # We need to flush the session here, after adding default RBAC permissions
            # which are needed by REST channels with security delegated to RBAC.
            session.flush()

            self.add_internal_services(session, cluster, admin_invoke_sec, pubapi_sec, internal_invoke_sec, ide_pub_rbac_role)

            ping_service = self.add_ping_services(session, cluster)
            self.add_cache_endpoints(session, cluster)
            self.add_crypto_endpoints(session, cluster)
            self.add_pubsub_sec_endpoints(session, cluster)

            # IBM MQ connections / connectors
            self.add_internal_callback_wmq(session, cluster)

            # SFTP connections / connectors
            self.add_sftp_credentials(session, cluster)

            # Account to access cache services with
            self.add_cache_credentials(session, cluster)

            # SSO
            self.add_sso_endpoints(session, cluster)

            # Rule Engine Security Group
            self.add_rule_engine_configuration(session, cluster, ping_service)

            # Run ODB post-processing tasks
            odb_post_process.run()

        try:
            session.commit()
        except IntegrityError as e:
            msg = 'SQL IntegrityError caught `{}`'.format(e.message)
            if self.verbose:
                msg += '\nDetails:`{}`'.format(format_exc().decode('utf-8'))
                self.logger.error(msg)
            self.logger.error(msg)
            session.rollback()

            return self.SYS_ERROR.CLUSTER_NAME_ALREADY_EXISTS

        if show_output:
            if self.verbose:
                msg = 'Successfully created a new cluster [{}]'.format(args.cluster_name)
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

# ################################################################################################################################

    def generate_password(self):

        # stdlib
        from uuid import uuid4

        # cryptography
        from cryptography.fernet import Fernet

        # Zato
        from zato.common.const import SECRETS

        # New password
        password = uuid4().hex

        # This is optional
        secret_key = getattr(self.args, 'secret_key', None)

        # Return encrypted if we have the secret key, otherwise, as it is.
        if secret_key:
            password = Fernet(secret_key).encrypt(password.encode('utf8'))
            password = password.decode('utf8')
            password = SECRETS.PREFIX + password

        return password

# ################################################################################################################################

    def add_api_invoke(self, session, cluster, service, pubapi_sec):

        from zato.common.api import APISPEC
        from zato.common.odb.model import HTTPSOAP

        for url_path in (APISPEC.GENERIC_INVOKE_PATH,):
            channel = HTTPSOAP(None, url_path, True, True, 'channel', 'plain_http',
                None, url_path, None, '', None, DATA_FORMAT.JSON, service=service, cluster=cluster)
            session.add(channel)

# ################################################################################################################################

    def add_internal_services(self, session, cluster, admin_invoke_sec, pubapi_sec, internal_invoke_sec, ide_pub_rbac_role):
        """ Adds these Zato internal services that can be accessed through SOAP requests.
        """
        #
        # HTTPSOAP + services
        #

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import Service
        from zato.common.util.api import get_http_json_channel

        for name, impl_name in iteritems(zato_services):

            service = Service(None, name, True, impl_name, True, cluster)
            session.add(service)

            if name == 'pub.zato.service.service-invoker':
                self.add_api_invoke(session, cluster, service, pubapi_sec)

            elif name == 'zato.service.invoke':
                self.add_admin_invoke(session, cluster, service, admin_invoke_sec)
                self.add_internal_invoke(session, cluster, service, internal_invoke_sec)

            elif name == 'zato.security.jwt.log-in':
                self.add_jwt_log_in(session, cluster, service)

            elif name == 'zato.security.jwt.log-out':
                self.add_jwt_log_out(session, cluster, service)

            elif name == 'zato.ide-deploy.create':
                self.add_rbac_channel(session, cluster, service, ide_pub_rbac_role, '/ide-deploy', permit_write=True,
                    data_format=DATA_FORMAT.JSON)

            elif 'check' in name:
                self.add_check(session, cluster, service, pubapi_sec)

            session.add(get_http_json_channel(name, service, cluster, pubapi_sec))

# ################################################################################################################################

    def add_ping_services(self, session, cluster):
        """ Adds a ping service and channels, with and without security checks.
        """

        # Zato
        from zato.common.api import SIMPLE_IO
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, Service

        passwords = {
            'ping.plain_http.basic_auth': None,
        }

        for password in passwords:
            passwords[password] = self.generate_password()

        ping_impl_name = 'zato.server.service.internal.Ping'
        ping_service_name = 'zato.ping'
        ping_service = Service(None, ping_service_name, True, ping_impl_name, True, cluster)
        session.add(ping_service)

        #
        # .. no security ..
        #
        # TODO
        # Change it to /zato/json/ping
        # and add an actual /zato/ping with no data format specified.
        ping_no_sec_channel = HTTPSOAP(
            None, 'zato.ping', True, True, 'channel',
            'plain_http', None, '/zato/ping', None, '', None, SIMPLE_IO.FORMAT.JSON, service=ping_service, cluster=cluster)
        session.add(ping_no_sec_channel)

        #
        # All the possible options
        #
        # Plain HTTP / Basic auth
        #

        transports = ['plain_http',]

        for transport in transports:
            data_format = SIMPLE_IO.FORMAT.JSON

            base_name = 'ping.{0}.basic_auth'.format(transport)
            zato_name = 'zato.{0}'.format(base_name)
            url = '/zato/{0}'.format(base_name)
            soap_action, soap_version = (zato_name, '1.1') if transport == 'soap' else ('', None)
            password = passwords[base_name]

            sec = HTTPBasicAuth(None, zato_name, True, zato_name, 'Zato ping', password, cluster)
            session.add(sec)

            channel = HTTPSOAP(
                None, zato_name, True, True, 'channel', transport, None, url, None, soap_action,
                soap_version, data_format, service=ping_service, security=sec, cluster=cluster)
            session.add(channel)

        return ping_service

# ################################################################################################################################

    def add_admin_invoke(self, session, cluster, service, admin_invoke_sec):
        """ Adds an admin channel for invoking services from web admin and CLI.
        """

        # Zato
        from zato.common.api import MISC, SIMPLE_IO
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(
            None, MISC.DefaultAdminInvokeChannel, True, True, 'channel', 'plain_http',
            None, ServiceConst.API_Admin_Invoke_Url_Path, None, '', None,
            SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster,
            security=admin_invoke_sec)
        session.add(channel)

# ################################################################################################################################

    def add_internal_invoke(self, session, cluster, service, internal_invoke_sec):
        """ Adds an internal channel for invoking services from other servers.
        """

        # Zato
        from zato.common.api import SIMPLE_IO
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(
            None, 'zato.internal.invoke', True, True, 'channel', 'plain_http',
            None, '/zato/internal/invoke', None, '', None, SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster,
            security=internal_invoke_sec)
        session.add(channel)

# ################################################################################################################################

    def add_default_rbac_permissions(self, session, cluster):
        """ Adds default CRUD permissions used by RBAC.
        """

        # Zato
        from zato.common.odb.model import RBACPermission

        for name in('Create', 'Read', 'Update', 'Delete'):
            item = RBACPermission()
            item.name = name
            item.cluster = cluster
            session.add(item)

# ################################################################################################################################

    def add_default_rbac_roles(self, session, cluster):
        """ Adds default roles used by RBAC.
        """

        # Zato
        from zato.common.odb.model import RBACRole

        root = RBACRole(name='Root', parent=None, cluster=cluster)
        session.add(root)
        return root

# ################################################################################################################################

    def add_rbac_role_and_acct(self, session, cluster, root_rbac_role, role_name, account_name, realm):
        """ Create an RBAC role alongside a default account and random password for accessing it via Basic Auth.

        :param session: SQLAlchemy session instance
        :param cluster: Cluster model instance
        :param root_rbac_role: RBACRole model instance for the root role
        :param role_name: "My Descriptive RBAC Role Name"
        :param account_name: "my_default_rbac_user"
        :param realm: "http_auth_service_realm"
        :return: New RBACRole model instance
        """

        # Zato
        from zato.common.api import MISC
        from zato.common.odb.model import HTTPBasicAuth, RBACClientRole, RBACRole

        role = RBACRole(name=role_name, parent=root_rbac_role, cluster=cluster)
        session.add(role)

        auth = HTTPBasicAuth(None, account_name, True, account_name, realm, self.generate_password(), cluster)
        session.add(auth)

        client_role_def = MISC.SEPARATOR.join(('sec_def', 'basic_auth', account_name))
        client_role_name = MISC.SEPARATOR.join((client_role_def, role.name))
        client_role = RBACClientRole(name=client_role_name, client_def=client_role_def, role=role, cluster=cluster)
        session.add(client_role)

        return role

# ################################################################################################################################

    def add_default_caches(self, session, cluster):
        """ Adds default caches to the cluster.
        """

        # Zato
        from zato.common.api import CACHE
        from zato.common.odb.model import CacheBuiltin

        # This is the default cache that is used if a specific one is not selected by users
        item = CacheBuiltin()
        item.cluster = cluster
        item.name = CACHE.Default_Name.Main
        item.is_active = True
        item.is_default = True
        item.max_size = CACHE.DEFAULT.MAX_SIZE
        item.max_item_size = CACHE.DEFAULT.MAX_ITEM_SIZE
        item.extend_expiry_on_get = True
        item.extend_expiry_on_set = True
        item.cache_type = CACHE.TYPE.BUILTIN
        item.sync_method = CACHE.SYNC_METHOD.IN_BACKGROUND.id
        item.persistent_storage = CACHE.PERSISTENT_STORAGE.SQL.id
        session.add(item)

        # This is used for Bearer tokens - note that it does not extend the key's expiration on .get.
        # Otherwise, it is the same as the default one.
        item = CacheBuiltin()
        item.cluster = cluster
        item.name = CACHE.Default_Name.Bearer_Token
        item.is_active = True
        item.is_default = True
        item.max_size = CACHE.DEFAULT.MAX_SIZE
        item.max_item_size = CACHE.DEFAULT.MAX_ITEM_SIZE
        item.extend_expiry_on_get = False
        item.extend_expiry_on_set = True
        item.cache_type = CACHE.TYPE.BUILTIN
        item.sync_method = CACHE.SYNC_METHOD.IN_BACKGROUND.id
        item.persistent_storage = CACHE.PERSISTENT_STORAGE.SQL.id
        session.add(item)

# ################################################################################################################################

    def add_jwt_log_in(self, session, cluster, service):

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(None, 'zato.security.jwt.log-in', True, True, 'channel', 'plain_http',
            None, '/zato/jwt/log-in', None, '', None, DATA_FORMAT.JSON, merge_url_params_req=True, service=service,
            cluster=cluster)
        session.add(channel)

# ################################################################################################################################

    def add_jwt_log_out(self, session, cluster, service):

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(None, 'zato.security.jwt.log-out', True, True, 'channel', 'plain_http',
            None, '/zato/jwt/log-out', None, '', None, DATA_FORMAT.JSON, merge_url_params_req=True, service=service,
            cluster=cluster)
        session.add(channel)

# ################################################################################################################################

    def add_rbac_channel(self, session, cluster, service, rbac_role, url_path, permit_read=True, permit_write=False, **kwargs):
        """ Create an RBAC-authenticated plain HTTP channel associated with a service.

        :param session: SQLAlchemy session instance
        :param cluster: Cluster model instance
        :param service: Service model instance
        :param rbac_role: RBACRole model instance
        :param url_path: "/url/path" to expose service as
        """

        # Zato
        from zato.common.odb.model import HTTPSOAP, RBACPermission, RBACRolePermission

        name = 'admin.' + service.name.replace('zato.', '')
        channel = HTTPSOAP(name=name, is_active=True, is_internal=True, connection='channel', transport='plain_http',
            url_path=url_path, soap_action='', has_rbac=True, sec_use_rbac=True, merge_url_params_req=True, service=service,
            cluster=cluster, **kwargs)
        session.add(channel)

        perms = []
        for permitted, perm_names in ((permit_read, ('Read',)), (permit_write, ('Create', 'Update'))):
            if permitted:
                perms.extend(session.query(RBACPermission).\
                    filter(RBACPermission.name.in_(perm_names)))

        for perm in perms:
            session.add(RBACRolePermission(role=rbac_role, perm=perm, service=service, cluster=cluster))

# ################################################################################################################################

    def add_check(self, session, cluster, service, pubapi_sec):

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPSOAP

        data_formats = [DATA_FORMAT.JSON]
        for data_format in data_formats:

            name = 'zato.checks.{}.{}'.format(data_format, service.name)
            url_path = '/zato/checks/{}/{}'.format(data_format, service.name)

            channel = HTTPSOAP(None, name, True, True, 'channel', 'plain_http', None, url_path, None, '', None, data_format,
                merge_url_params_req=True, service=service, cluster=cluster, security=pubapi_sec)
            session.add(channel)

# ################################################################################################################################

    def add_cache_endpoints(self, session, cluster):

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, Service

        service_to_endpoint = {

            # For single keys
            'zato.cache.builtin.pubapi.single-key-service':  '/zato/cache/{key}',

            # Multi-key get
            'zato.cache.builtin.pubapi.get-by-prefix':       '/zato/cache/get/by-prefix/{key}',
            'zato.cache.builtin.pubapi.get-by-regex':        '/zato/cache/get/by-regex/{key}',
            'zato.cache.builtin.pubapi.get-by-suffix':       '/zato/cache/get/by-suffix/{key}',
            'zato.cache.builtin.pubapi.get-contains':        '/zato/cache/get/contains/{key}',
            'zato.cache.builtin.pubapi.get-not-contains':    '/zato/cache/get/not-contains/{key}',
            'zato.cache.builtin.pubapi.get-contains-all':    '/zato/cache/get/contains-all',
            'zato.cache.builtin.pubapi.get-contains-any':    '/zato/cache/get/contains-any',

            # Multi-key set
            'zato.cache.builtin.pubapi.set-by-prefix':       '/zato/cache/set/by-prefix/{key}',
            'zato.cache.builtin.pubapi.set-by-regex':        '/zato/cache/set/by-regex/{key}',
            'zato.cache.builtin.pubapi.set-by-suffix':       '/zato/cache/set/by-suffix/{key}',
            'zato.cache.builtin.pubapi.set-contains':        '/zato/cache/set/contains/{key}',
            'zato.cache.builtin.pubapi.set-not-contains':    '/zato/cache/set/not-contains/{key}',
            'zato.cache.builtin.pubapi.set-contains-all':    '/zato/cache/set/contains-all',
            'zato.cache.builtin.pubapi.set-contains-any':    '/zato/cache/set/contains-any',

            # Multi-key delete
            'zato.cache.builtin.pubapi.delete-by-prefix':    '/zato/cache/delete/by-prefix/{key}',
            'zato.cache.builtin.pubapi.delete-by-regex':     '/zato/cache/delete/by-regex/{key}',
            'zato.cache.builtin.pubapi.delete-by-suffix':    '/zato/cache/delete/by-suffix/{key}',
            'zato.cache.builtin.pubapi.delete-contains':     '/zato/cache/delete/contains/{key}',
            'zato.cache.builtin.pubapi.delete-not-contains': '/zato/cache/delete/not-contains/{key}',
            'zato.cache.builtin.pubapi.delete-contains-all': '/zato/cache/delete/contains-all',
            'zato.cache.builtin.pubapi.delete-contains-any': '/zato/cache/delete/contains-any',

            # Multi-key expire
            'zato.cache.builtin.pubapi.expire-by-prefix':    '/zato/cache/expire/by-prefix/{key}',
            'zato.cache.builtin.pubapi.expire-by-regex':     '/zato/cache/expire/by-regex/{key}',
            'zato.cache.builtin.pubapi.expire-by-suffix':    '/zato/cache/expire/by-suffix/{key}',
            'zato.cache.builtin.pubapi.expire-contains':     '/zato/cache/expire/contains/{key}',
            'zato.cache.builtin.pubapi.expire-not-contains': '/zato/cache/expire/not-contains/{key}',
            'zato.cache.builtin.pubapi.expire-contains-all': '/zato/cache/expire/contains-all',
            'zato.cache.builtin.pubapi.expire-contains-any': '/zato/cache/expire/contains-any',

        }

        service_to_impl = {

            # For single keys
            'zato.cache.builtin.pubapi.single-key-service':  'zato.server.service.internal.cache.builtin.pubapi.SingleKeyService',

            # Multi-key get
            'zato.cache.builtin.pubapi.get-by-prefix':       'zato.server.service.internal.cache.builtin.pubapi.GetByPrefix',
            'zato.cache.builtin.pubapi.get-by-regex':        'zato.server.service.internal.cache.builtin.pubapi.GetByRegex',
            'zato.cache.builtin.pubapi.get-by-suffix':       'zato.server.service.internal.cache.builtin.pubapi.GetBySuffix',
            'zato.cache.builtin.pubapi.get-contains':        'zato.server.service.internal.cache.builtin.pubapi.GetContains',
            'zato.cache.builtin.pubapi.get-not-contains':    'zato.server.service.internal.cache.builtin.pubapi.GetNotContains',
            'zato.cache.builtin.pubapi.get-contains-all':    'zato.server.service.internal.cache.builtin.pubapi.GetContainsAll',
            'zato.cache.builtin.pubapi.get-contains-any':    'zato.server.service.internal.cache.builtin.pubapi.GetContainsAny',

            # Multi-key set
            'zato.cache.builtin.pubapi.set-by-prefix':       'zato.server.service.internal.cache.builtin.pubapi.SetByPrefix',
            'zato.cache.builtin.pubapi.set-by-regex':        'zato.server.service.internal.cache.builtin.pubapi.SetByRegex',
            'zato.cache.builtin.pubapi.set-by-suffix':       'zato.server.service.internal.cache.builtin.pubapi.SetBySuffix',
            'zato.cache.builtin.pubapi.set-contains':        'zato.server.service.internal.cache.builtin.pubapi.SetContains',
            'zato.cache.builtin.pubapi.set-not-contains':    'zato.server.service.internal.cache.builtin.pubapi.SetNotContains',
            'zato.cache.builtin.pubapi.set-contains-all':    'zato.server.service.internal.cache.builtin.pubapi.SetContainsAll',
            'zato.cache.builtin.pubapi.set-contains-any':    'zato.server.service.internal.cache.builtin.pubapi.SetContainsAny',

            # Multi-key delete
            'zato.cache.builtin.pubapi.delete-by-prefix':    'zato.server.service.internal.cache.builtin.pubapi.DeleteByPrefix',
            'zato.cache.builtin.pubapi.delete-by-regex':     'zato.server.service.internal.cache.builtin.pubapi.DeleteByRegex',
            'zato.cache.builtin.pubapi.delete-by-suffix':    'zato.server.service.internal.cache.builtin.pubapi.DeleteBySuffix',
            'zato.cache.builtin.pubapi.delete-contains':     'zato.server.service.internal.cache.builtin.pubapi.DeleteContains',
            'zato.cache.builtin.pubapi.delete-not-contains': 'zato.server.service.internal.cache.builtin.pubapi.DeleteNotContains',
            'zato.cache.builtin.pubapi.delete-contains-all': 'zato.server.service.internal.cache.builtin.pubapi.DeleteContainsAll',
            'zato.cache.builtin.pubapi.delete-contains-any': 'zato.server.service.internal.cache.builtin.pubapi.DeleteContainsAny',

            # Multi-key expire
            'zato.cache.builtin.pubapi.expire-by-prefix':    'zato.server.service.internal.cache.builtin.pubapi.ExpireByPrefix',
            'zato.cache.builtin.pubapi.expire-by-regex':     'zato.server.service.internal.cache.builtin.pubapi.ExpireByRegex',
            'zato.cache.builtin.pubapi.expire-by-suffix':    'zato.server.service.internal.cache.builtin.pubapi.ExpireBySuffix',
            'zato.cache.builtin.pubapi.expire-contains':     'zato.server.service.internal.cache.builtin.pubapi.ExpireContains',
            'zato.cache.builtin.pubapi.expire-not-contains': 'zato.server.service.internal.cache.builtin.pubapi.ExpireNotContains',
            'zato.cache.builtin.pubapi.expire-contains-all': 'zato.server.service.internal.cache.builtin.pubapi.ExpireContainsAll',
            'zato.cache.builtin.pubapi.expire-contains-any': 'zato.server.service.internal.cache.builtin.pubapi.ExpireContainsAny',

        }

        sec = HTTPBasicAuth(None, 'zato.default.cache.client', True, 'zato.cache', 'Zato cache', self.generate_password(), cluster)
        session.add(sec)

        for name, impl_name in iteritems(service_to_impl):

            service = Service(None, name, True, impl_name, True, cluster)
            session.add(service)

            url_path = service_to_endpoint[name]

            http_soap = HTTPSOAP(None, name, True, True, 'channel', 'plain_http', None, url_path, None, '',
                None, DATA_FORMAT.JSON, security=sec, service=service, cluster=cluster)

            session.add(http_soap)

# ################################################################################################################################

    def add_crypto_endpoints(self, session, cluster):

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, Service

        service_to_endpoint = {
            'zato.crypto.encrypt':  '/zato/crypto/encrypt',
            'zato.crypto.decrypt':  '/zato/crypto/decrypt',
            'zato.crypto.hash-secret':  '/zato/crypto/hash-secret',
            'zato.crypto.verify-hash':  '/zato/crypto/verify-hash',
            'zato.crypto.generate-secret':  '/zato/crypto/generate-secret',
            'zato.crypto.generate-password':  '/zato/crypto/generate-password',
        }

        service_to_impl = {
            'zato.crypto.encrypt':  'zato.server.service.internal.crypto.Encrypt',
            'zato.crypto.decrypt':  'zato.server.service.internal.crypto.Decrypt',
            'zato.crypto.hash-secret':  'zato.server.service.internal.crypto.HashSecret',
            'zato.crypto.verify-hash':  'zato.server.service.internal.crypto.VerifyHash',
            'zato.crypto.generate-secret':  'zato.server.service.internal.crypto.GenerateSecret',
            'zato.crypto.generate-password':  'zato.server.service.internal.crypto.GeneratePassword',
        }

        sec = HTTPBasicAuth(None, 'zato.default.crypto.client', True, 'zato.crypto', 'Zato crypto', self.generate_password(), cluster)
        session.add(sec)

        for name, impl_name in iteritems(service_to_impl):

            service = Service(None, name, True, impl_name, True, cluster)
            session.add(service)

            url_path = service_to_endpoint[name]

            http_soap = HTTPSOAP(None, name, True, True, 'channel', 'plain_http', None, url_path, None, '',
                None, DATA_FORMAT.JSON, security=sec, service=service, cluster=cluster)

            session.add(http_soap)

# ################################################################################################################################

    def add_pubsub_sec_endpoints(self, session, cluster):

        from zato.common.api import CONNECTION, DATA_FORMAT, PUBSUB, URL_TYPE
        from zato.common.json_internal import dumps
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, PubSubEndpoint, PubSubSubscription, PubSubTopic, \
             Service
        from zato.common.pubsub import new_sub_key
        from zato.common.util.time_ import utcnow_as_ms

        sec_pubsub_default = HTTPBasicAuth(
            None, PUBSUB.DEFAULT.DEFAULT_SECDEF_NAME, True, PUBSUB.DEFAULT.DEFAULT_USERNAME,
            'Zato pub/sub default', self.generate_password(), cluster)
        session.add(sec_pubsub_default)

        sec_pubsub_test = HTTPBasicAuth(
            None, PUBSUB.DEFAULT.TEST_SECDEF_NAME, True, PUBSUB.DEFAULT.TEST_USERNAME,
            'Zato pub/sub test', self.generate_password(), cluster)
        session.add(sec_pubsub_test)

        sec_default_internal = HTTPBasicAuth(None, PUBSUB.DEFAULT.INTERNAL_SECDEF_NAME, True, PUBSUB.DEFAULT.INTERNAL_USERNAME,
            'Zato pub/sub internal', self.generate_password(), cluster)
        session.add(sec_default_internal)

        impl_name1 = 'zato.server.service.internal.pubsub.pubapi.TopicService'
        impl_name2 = 'zato.server.service.internal.pubsub.pubapi.SubscribeService'
        impl_name3 = 'zato.server.service.internal.pubsub.pubapi.MessageService'
        impl_demo  = 'zato.server.service.internal.helpers.JSONRawRequestLogger'

        service_topic = Service(None, 'zato.pubsub.pubapi.topic-service', True, impl_name1, True, cluster)
        service_sub   = Service(None, 'zato.pubsub.pubapi.subscribe-service', True, impl_name2, True, cluster)
        service_msg   = Service(None, 'zato.pubsub.pubapi.message-service', True, impl_name3, True, cluster)
        service_demo  = Service(None, 'pub.helpers.raw-request-logger', True, impl_demo, True, cluster)
        service_test  = service_demo

        # Opaque data that lets clients use topic contain slash characters
        opaque = dumps({'match_slash':True})

        chan_topic = HTTPSOAP(None, 'zato.pubsub.topic.topic_name', True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, '/zato/pubsub/topic/{topic_name}',
            None, '', None, DATA_FORMAT.JSON, security=None, service=service_topic, opaque=opaque,
            cluster=cluster)

        chan_sub = HTTPSOAP(None, 'zato.pubsub.subscribe.topic.topic_name', True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, '/zato/pubsub/subscribe/topic/{topic_name}',
            None, '', None, DATA_FORMAT.JSON, security=None, service=service_sub, opaque=opaque,
            cluster=cluster)

        chan_msg = HTTPSOAP(None, 'zato.pubsub.msg.msg_id', True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, '/zato/pubsub/msg/{msg_id}',
            None, '', None, DATA_FORMAT.JSON, security=None, service=service_msg, opaque=opaque,
            cluster=cluster)

        chan_demo = HTTPSOAP(None, 'pubsub.demo.sample.channel', True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, '/zato/pubsub/zato.demo.sample',
            None, '', None, DATA_FORMAT.JSON, security=sec_pubsub_default, service=service_demo, opaque=opaque,
            cluster=cluster)

        chan_test = HTTPSOAP(None, 'pubsub.test.sample.channel', True, True, CONNECTION.CHANNEL,
            URL_TYPE.PLAIN_HTTP, None, '/zato/pubsub/zato.test.sample',
            None, '', None, DATA_FORMAT.JSON, security=sec_pubsub_test, service=service_test, opaque=opaque,
            cluster=cluster)

        outconn_demo = HTTPSOAP(None, 'pubsub.demo.sample.outconn', True, True, CONNECTION.OUTGOING,
            URL_TYPE.PLAIN_HTTP, 'http://127.0.0.1:17010', '/zato/pubsub/zato.demo.sample',
            None, '', None, DATA_FORMAT.JSON, security=sec_pubsub_default, opaque=opaque,
            cluster=cluster)

        outconn_test = HTTPSOAP(None, 'pubsub.test.sample.outconn', True, True, CONNECTION.OUTGOING,
            URL_TYPE.PLAIN_HTTP, 'http://127.0.0.1:17010', '/zato/pubsub/zato.test.sample',
            None, '', None, DATA_FORMAT.JSON, security=sec_pubsub_test, opaque=opaque,
            cluster=cluster)

        endpoint_default_internal = PubSubEndpoint()
        endpoint_default_internal.name = PUBSUB.DEFAULT.INTERNAL_ENDPOINT_NAME
        endpoint_default_internal.is_internal = True
        endpoint_default_internal.role = PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id
        endpoint_default_internal.topic_patterns = 'pub=/*\nsub=/*'
        endpoint_default_internal.security = sec_default_internal
        endpoint_default_internal.cluster = cluster
        endpoint_default_internal.endpoint_type = PUBSUB.ENDPOINT_TYPE.INTERNAL.id

        endpoint_default_rest = PubSubEndpoint()
        endpoint_default_rest.name = 'zato.pubsub.default.rest'
        endpoint_default_rest.is_internal = False
        endpoint_default_rest.role = PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id
        endpoint_default_rest.topic_patterns = 'pub=/*\nsub=/*'
        endpoint_default_rest.security = sec_pubsub_default
        endpoint_default_rest.cluster = cluster
        endpoint_default_rest.endpoint_type = PUBSUB.ENDPOINT_TYPE.REST.id

        endpoint_default_service = PubSubEndpoint()
        endpoint_default_service.name = 'zato.pubsub.default.service'
        endpoint_default_service.is_internal = False
        endpoint_default_service.role = PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id
        endpoint_default_service.topic_patterns = 'pub=/*\nsub=/*'
        endpoint_default_service.cluster = cluster
        endpoint_default_service.endpoint_type = PUBSUB.ENDPOINT_TYPE.SERVICE.id
        endpoint_default_service.service = service_demo

        endpoint_test = PubSubEndpoint()
        endpoint_test.name = 'zato.pubsub.test.endpoint'
        endpoint_test.is_internal = True
        endpoint_test.role = PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id
        endpoint_test.topic_patterns = 'pub=/zato/test/*\nsub=/zato/test/*'
        endpoint_test.security = sec_pubsub_test
        endpoint_test.cluster = cluster
        endpoint_test.endpoint_type = PUBSUB.ENDPOINT_TYPE.REST.id

        topic_demo = PubSubTopic()
        topic_demo.name = '/zato/demo/sample'
        topic_demo.is_active = True
        topic_demo.is_api_sub_allowed = True
        topic_demo.is_internal = True
        topic_demo.max_depth = 100
        topic_demo.has_gd = False
        topic_demo.cluster = cluster

        topic_unique = PubSubTopic()
        topic_unique.name = '/zato/demo/unique'
        topic_unique.is_active = True
        topic_unique.is_api_sub_allowed = True
        topic_unique.is_internal = True
        topic_unique.max_depth = 100
        topic_unique.has_gd = False
        topic_unique.cluster = cluster

        topic_test = PubSubTopic()
        topic_test.name = '/zato/test/sample'
        topic_test.is_active = True
        topic_test.is_api_sub_allowed = True
        topic_test.is_internal = False
        topic_test.max_depth = 100
        topic_test.has_gd = False
        topic_test.cluster = cluster

        sub_default_rest = PubSubSubscription()
        sub_default_rest.creation_time = utcnow_as_ms()
        sub_default_rest.topic = topic_demo
        sub_default_rest.endpoint = endpoint_default_rest
        sub_default_rest.sub_key = new_sub_key(endpoint_default_rest.endpoint_type)
        sub_default_rest.has_gd = False
        sub_default_rest.sub_pattern_matched = 'sub=/*'
        sub_default_rest.active_status = PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id
        sub_default_rest.cluster = cluster
        sub_default_rest.wrap_one_msg_in_list = False
        sub_default_rest.delivery_err_should_block = False
        sub_default_rest.out_http_soap = outconn_demo

        sub_default_service = PubSubSubscription()
        sub_default_service.creation_time = utcnow_as_ms()
        sub_default_service.topic = topic_demo
        sub_default_service.endpoint = endpoint_default_service
        sub_default_service.sub_key = new_sub_key(endpoint_default_service.endpoint_type)
        sub_default_service.has_gd = False
        sub_default_service.sub_pattern_matched = 'sub=/*'
        sub_default_service.active_status = PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id
        sub_default_service.cluster = cluster
        sub_default_service.wrap_one_msg_in_list = False
        sub_default_service.delivery_err_should_block = False

        sub_test = PubSubSubscription()
        sub_test.creation_time = utcnow_as_ms()
        sub_test.topic = topic_test
        sub_test.endpoint = endpoint_test
        sub_test.sub_key = new_sub_key(endpoint_test.endpoint_type)
        sub_test.has_gd = False
        sub_test.sub_pattern_matched = 'sub=/zato/test/*'
        sub_test.active_status = PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id
        sub_test.cluster = cluster
        sub_test.wrap_one_msg_in_list = False
        sub_test.delivery_err_should_block = False
        sub_test.out_http_soap = outconn_test

        session.add(endpoint_default_internal)
        session.add(endpoint_default_rest)
        session.add(topic_demo)
        session.add(topic_test)
        session.add(sub_default_rest)
        session.add(sub_default_service)
        session.add(sub_test)

        session.add(service_topic)
        session.add(service_sub)
        session.add(service_msg)

        session.add(chan_topic)
        session.add(chan_sub)
        session.add(chan_msg)

        session.add(chan_demo)
        session.add(chan_test)

        session.add(outconn_demo)
        session.add(outconn_test)

# ################################################################################################################################

    def add_internal_callback_wmq(self, session, cluster):

        from zato.common.api import IPC
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP, Service

        impl_name = 'zato.server.service.internal.channel.jms_wmq.OnMessageReceived'
        service = Service(None, 'zato.channel.jms-wmq.on-message-received', True, impl_name, True, cluster)

        username = IPC.CONNECTOR.USERNAME.IBM_MQ
        sec = HTTPBasicAuth(None, username, True, username, 'Zato IBM MQ', self.generate_password(), cluster)

        channel = HTTPSOAP(None, 'zato.internal.callback.wmq', True, True, 'channel', 'plain_http', None,
            '/zato/internal/callback/wmq',
            None, '', None, None, security=sec, service=service, cluster=cluster)

        session.add(sec)
        session.add(service)
        session.add(channel)

# ################################################################################################################################

    def add_sftp_credentials(self, session, cluster):

        from zato.common.api import IPC
        from zato.common.odb.model import HTTPBasicAuth

        username = IPC.CONNECTOR.USERNAME.SFTP
        sec = HTTPBasicAuth(None, username, True, username, 'Zato SFTP', self.generate_password(), cluster)
        session.add(sec)

# ################################################################################################################################

    def add_cache_credentials(self, session, cluster):

        from zato.common.api import CACHE
        from zato.common.odb.model import HTTPBasicAuth

        username = CACHE.API_USERNAME
        sec = HTTPBasicAuth(None, username, True, username, 'Zato Cache', self.generate_password(), cluster)
        session.add(sec)

# ################################################################################################################################

    def add_sso_endpoints(self, session, cluster):

        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPSOAP, Service

        prefix = SSO.Default.RESTPrefix

        data = [

            # Users
            ['zato.sso.user.create', 'zato.server.service.internal.sso.user.Create', f'{prefix}/user/create'],
            ['zato.sso.user.signup', 'zato.server.service.internal.sso.user.Signup', f'{prefix}/user/signup'],
            ['zato.sso.user.approve', 'zato.server.service.internal.sso.user.Approve', f'{prefix}/user/approve'],
            ['zato.sso.user.reject', 'zato.server.service.internal.sso.user.Reject', f'{prefix}/user/reject'],
            ['zato.sso.user.login', 'zato.server.service.internal.sso.user.Login', f'{prefix}/user/login'],
            ['zato.sso.user.logout', 'zato.server.service.internal.sso.user.Logout', f'{prefix}/user/logout'],
            ['zato.sso.user.user', 'zato.server.service.internal.sso.user.User', f'{prefix}/user'],
            ['zato.sso.user.password', 'zato.server.service.internal.sso.user.Password', f'{prefix}/user/password'],
            ['zato.sso.user.search', 'zato.server.service.internal.sso.user.Search', f'{prefix}/user/search'],
            ['zato.sso.user.totp', 'zato.server.service.internal.sso.user.TOTP', f'{prefix}/user/totp'],
            ['zato.sso.user.lock', 'zato.server.service.internal.sso.user.Lock', f'{prefix}/user/lock'],

            # Linked accounts
            ['zato.sso.user.linked-auth', 'zato.server.service.internal.sso.user.LinkedAuth', f'{prefix}/user/linked'],

            # User sessions
            ['zato.sso.session.session', 'zato.server.service.internal.sso.session.Session', f'{prefix}/user/session'],
            ['zato.sso.session.session-list', 'zato.server.service.internal.sso.session.SessionList', f'{prefix}/user/session/list'],

            # User attributes
            ['zato.sso.user-attr.user-attr', 'zato.server.service.internal.sso.user_attr.UserAttr', f'{prefix}/user/attr'],
            ['zato.sso.user-attr.user-attr-exists', 'zato.server.service.internal.sso.user_attr.UserAttrExists', f'{prefix}/user/attr/exists'],
            ['zato.sso.user-attr.user-attr-names', 'zato.server.service.internal.sso.user_attr.UserAttrNames', f'{prefix}/user/attr/names'],

            # Session attributes
            ['zato.sso.session-attr.session-attr', 'zato.server.service.internal.sso.session_attr.SessionAttr', f'{prefix}/session/attr'],
            ['zato.sso.session-attr.session-attr-exists', 'zato.server.service.internal.sso.session_attr.SessionAttrExists', f'{prefix}/session/attr/exists'],
            ['zato.sso.session-attr.session-attr-names', 'zato.server.service.internal.sso.session_attr.SessionAttrNames', f'{prefix}/session/attr/names'],

            # Password reset
            ['zato.sso.password-reset.password-reset', 'zato.server.service.internal.sso.password_reset.PasswordReset', f'{prefix}/password/reset'],
        ]

        for name, impl_name, url_path in data:
            service = Service(None, name, True, impl_name, True, cluster)
            channel = HTTPSOAP(None, url_path, True, True, 'channel', 'plain_http', None, url_path, None, '', None,
                DATA_FORMAT.JSON, security=None, service=service, cluster=cluster)

            session.add(service)
            session.add(channel)

# ################################################################################################################################

    def add_rule_engine_configuration(self, session, cluster, ping_service):

        # Zato
        from zato.common.api import DATA_FORMAT, Groups, SEC_DEF_TYPE
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP
        from zato.server.groups.base import GroupsManager
        from json import dumps

        # Create a Basic Auth security definition for rule engine
        basic_auth_id = get_random_integer()
        basic_auth_password = os.environ.get('Zato_Password') or self.generate_password()
        basic_auth = HTTPBasicAuth(
            basic_auth_id, 'Rule engine default user', True, 'rules', 'Rule engine', basic_auth_password, cluster)
        session.add(basic_auth)

        class FakeServer:
            cluster_id = 1

        def fake_server_session():
            return session

        # Create a GroupsManager instance with our fake server
        groups_manager = GroupsManager(FakeServer, fake_server_session)

        # Create a security group for the rule engine
        group_name = 'Rule engine API users'
        group_id = groups_manager.create_group(Groups.Type.API_Clients, group_name)

        # Format member IDs for the group
        member_id_list = [
            f'{SEC_DEF_TYPE.BASIC_AUTH}-{basic_auth_id}',
        ]

        # Add the security definitions to the group
        groups_manager.add_members_to_group(group_id, member_id_list)

        # Create the security_groups_ctx structure in opaque1
        opaque1_data = {
            'security_groups': [group_id],
        }

        # Create a REST channel for the rule engine
        rule_engine_channel = HTTPSOAP(
            None, 'Rule engine API', True, True, 'channel',
            'plain_http', None, '/api/rules{action}', None, '', None, DATA_FORMAT.JSON,
            service=ping_service, cluster=cluster)
        rule_engine_channel.opaque1 = dumps(opaque1_data) # type: ignore

        session.add(rule_engine_channel)


# ################################################################################################################################
