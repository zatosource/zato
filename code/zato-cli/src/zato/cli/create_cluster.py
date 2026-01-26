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
from zato.cli import common_odb_opts, ZatoCommand
from zato.common.const import ServiceConst
from zato.common.util.api import utcnow

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
        from traceback import format_exc

        # SQLAlchemy
        from sqlalchemy.exc import IntegrityError

        # Zato
        from zato.common.api import IDEDeploy
        from zato.common.odb.model import Cluster, HTTPBasicAuth, Service
        from zato.common.odb.post_process import ODBPostProcess

        engine = self._get_engine(args)
        session = self._get_session(engine)

        with session.no_autoflush:

            cluster = Cluster()
            cluster.name = args.cluster_name
            cluster.description = 'Created by {} on {} (UTC)'.format(self._get_user_host(), utcnow().isoformat())

            for name in('odb_type', 'odb_host', 'odb_port', 'odb_user', 'odb_db_name'):
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

            admin_invoke_sec = HTTPBasicAuth(
                None, ServiceConst.API_Admin_Invoke_Username, True, ServiceConst.API_Admin_Invoke_Username,
                'Zato admin invoke', admin_invoke_password, cluster)

            ide_publisher_sec = HTTPBasicAuth(
                None, IDEDeploy.Username, True, IDEDeploy.Username, 'IDE Publishers', self.generate_password(), cluster)

            streaming_password = os.environ.get('Zato_Log_Streaming_Password')
            if not streaming_password:
                streaming_password = self.generate_password()

            streaming_sec = HTTPBasicAuth(
                None, 'zato.log.streaming', True, 'zato.log.streaming', 'Log streaming API', streaming_password, cluster)

            session.add(admin_invoke_sec)
            session.add(ide_publisher_sec)
            session.add(streaming_sec)

            session.flush()

            # Create services
            admin_invoke_service_name = 'zato.server.service.internal.service.Invoke'
            admin_invoke_service = Service(None, admin_invoke_service_name, True, admin_invoke_service_name, True, cluster)
            session.add(admin_invoke_service)

            ide_publisher_service_name = 'zato.server.service.internal.hot_deploy.Create'
            ide_publisher_service = Service(None, ide_publisher_service_name, True, ide_publisher_service_name, True, cluster)
            session.add(ide_publisher_service)

            metrics_service_name = 'zato.server.service.internal.helpers.GetMetrics'
            metrics_service = Service(None, metrics_service_name, True, metrics_service_name, True, cluster)
            session.add(metrics_service)

            openapi_handler_service_name = 'zato.server.service.internal.helpers.OpenAPIHandler'
            openapi_handler_service = Service(None, openapi_handler_service_name, True, openapi_handler_service_name, True, cluster)
            session.add(openapi_handler_service)

            ping_service = self.add_ping_service(session, cluster)

            # Create channels
            self.add_admin_invoke(session, cluster, admin_invoke_service, admin_invoke_sec)
            self.add_ide_publisher_channel(session, cluster, ide_publisher_service, ide_publisher_sec)
            self.add_metrics_channel(session, cluster, metrics_service)
            self.add_streaming_channels(session, cluster, ping_service, streaming_sec)
            self.add_openapi_handler_channel(session, cluster, openapi_handler_service)

            # Add other configurations
            self.add_default_caches(session, cluster)
            self.add_rule_engine_configuration(session, cluster, ping_service)

            # Run ODB post-processing tasks
            odb_post_process.run()

        try:
            session.commit()
        except IntegrityError as e:
            msg = 'SQL IntegrityError caught `{}`'.format(e.args[0])
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

    def add_ping_service(self, session, cluster):
        """ Adds a channel for the ping service.
        """

        # Zato
        from zato.common.api import SIMPLE_IO
        from zato.common.odb.model import HTTPSOAP, Service

        ping_impl_name = 'zato.server.service.internal.Ping'
        ping_service_name = 'demo.ping'
        ping_service = Service(None, ping_service_name, True, ping_impl_name, True, cluster)
        session.add(ping_service)

        ping_no_sec_channel = HTTPSOAP(
            None, 'zato.ping', True, True, 'channel',
            'plain_http', None, '/zato/ping', None, '', None, SIMPLE_IO.FORMAT.JSON, service=ping_service, cluster=cluster)
        session.add(ping_no_sec_channel)

        return ping_service

# ################################################################################################################################

    def add_metrics_channel(self, session, cluster, service):
        """ Adds a channel for the metrics service.
        """
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP

        metrics_password = os.environ['Zato_Server_Metrics_Password']

        security = HTTPBasicAuth(None, 'metrics', True, 'metrics', 'Metrics user', metrics_password, cluster)
        session.add(security)

        channel = HTTPSOAP(
            None, 'zato.metrics', True, True, 'channel',
            'plain_http', None, '/metrics', None, '', None, DATA_FORMAT.JSON,
            service=service, cluster=cluster, security=security)
        session.add(channel)

# ################################################################################################################################

    def add_admin_invoke(self, session, cluster, service, security):
        """ Adds an admin channel for invoking services from web admin and CLI.
        """

        # Zato
        from zato.common.api import MISC, SIMPLE_IO
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(
            None, MISC.DefaultAdminInvokeChannel, True, True, 'channel', 'plain_http',
            None, ServiceConst.API_Admin_Invoke_Url_Path, None, '', None,
            SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster,
            security=security)
        session.add(channel)

# ################################################################################################################################

    def add_ide_publisher_channel(self, session, cluster, service, security):
        """ Adds a channel for IDE deployments.
        """

        # Zato
        from zato.common.api import SIMPLE_IO
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(
            None, 'zato.ide_publisher', True, True, 'channel', 'plain_http',
            None, '/ide-deploy', None, '', None,
            SIMPLE_IO.FORMAT.JSON, service=service, cluster=cluster,
            security=security)
        session.add(channel)

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
        groups_manager = GroupsManager(FakeServer, fake_server_session) # type: ignore

        # Create a security group for the rule engine
        group_name = 'Rule engine API users'
        group_id = groups_manager.create_group(Groups.Type.API_Clients, group_name)

        # Format member IDs for the group
        member_id_list = [
            f'{SEC_DEF_TYPE.BASIC_AUTH}-{basic_auth_id}',
        ]

        # Add the security definitions to the group
        groups_manager.add_members_to_group(group_id, member_id_list) # type: ignore

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

    def add_streaming_channels(self, session, cluster, service, security):
        """ Adds channels for log streaming API.
        """

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPSOAP

        # Toggle log streaming on/off
        toggle_channel = HTTPSOAP(
            None, 'zato.log.streaming.toggle', True, True, 'channel',
            'plain_http', None, '/api/log/streaming/toggle', None, '', None, DATA_FORMAT.JSON,
            service=service, cluster=cluster, security=security)
        session.add(toggle_channel)

        # Get log streaming status
        status_channel = HTTPSOAP(
            None, 'zato.log.streaming.status', True, True, 'channel',
            'plain_http', None, '/api/log/streaming/status', None, '', None, DATA_FORMAT.JSON,
            service=service, cluster=cluster, security=security)
        session.add(status_channel)

# ################################################################################################################################

    def add_openapi_handler_channel(self, session, cluster, service):
        """ Adds a channel for OpenAPI specification retrieval.
        """

        # Zato
        from zato.common.api import DATA_FORMAT
        from zato.common.odb.model import HTTPSOAP

        channel = HTTPSOAP(
            None, 'zato.channel.openapi.get', True, True, 'channel',
            'plain_http', None, '/openapi/{name}', None, '', None, DATA_FORMAT.JSON,
            service=service, cluster=cluster)
        session.add(channel)

# ################################################################################################################################
