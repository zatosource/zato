# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from contextlib import closing
from logging import getLogger

# Zato
from zato.bunch import Bunch
from zato.common.api import RATE_LIMIT
from zato.common.const import SECRETS
from zato.common.util.api import asbool
from zato.common.util.sql import elems_with_opaque
from zato.common.util.url_dispatcher import get_match_target
from zato.server.config import ConfigDict
from zato.server.message import JSONPointerStore, NamespaceStore, XPathStore
from zato.url_dispatcher import Matcher

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ConfigLoader(object):
    """ Loads server's configuration.
    """

# ################################################################################################################################

    def set_up_config(self, server):

        # Which components are enabled
        self.component_enabled.stats = asbool(self.fs_server_config.component_enabled.stats)
        self.component_enabled.slow_response = asbool(self.fs_server_config.component_enabled.slow_response)

        #
        # Cassandra - start
        #

        query = self.odb.get_cassandra_conn_list(server.cluster.id, True)
        self.config.cassandra_conn = ConfigDict.from_query('cassandra_conn', query, decrypt_func=self.decrypt)

        query = self.odb.get_cassandra_query_list(server.cluster.id, True)
        self.config.cassandra_query = ConfigDict.from_query('cassandra_query', query, decrypt_func=self.decrypt)

        #
        # Cassandra - end
        #

        #
        # Search - start
        #

        query = self.odb.get_search_es_list(server.cluster.id, True)
        self.config.search_es = ConfigDict.from_query('search_es', query, decrypt_func=self.decrypt)

        query = self.odb.get_search_solr_list(server.cluster.id, True)
        self.config.search_solr = ConfigDict.from_query('search_solr', query, decrypt_func=self.decrypt)

        #
        # Search - end
        #

        #
        # SMS - start
        #

        query = self.odb.get_sms_twilio_list(server.cluster.id, True)
        self.config.sms_twilio = ConfigDict.from_query('sms_twilio', query, decrypt_func=self.decrypt)

        #
        # SMS - end
        #

        #
        # Cloud - start
        #

        # OpenStack - Swift

        query = self.odb.get_cloud_openstack_swift_list(server.cluster.id, True)
        self.config.cloud_openstack_swift = ConfigDict.from_query('cloud_openstack_swift', query, decrypt_func=self.decrypt)

        query = self.odb.get_cloud_aws_s3_list(server.cluster.id, True)
        self.config.cloud_aws_s3 = ConfigDict.from_query('cloud_aws_s3', query, decrypt_func=self.decrypt)

        #
        # Cloud - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Services
        query = self.odb.get_service_list(server.cluster.id, True)
        self.config.service = ConfigDict.from_query('service_list', query, decrypt_func=self.decrypt)

        #
        # Definitions - start
        #

        # AMQP
        query = self.odb.get_definition_amqp_list(server.cluster.id, True)
        self.config.definition_amqp = ConfigDict.from_query('definition_amqp', query, decrypt_func=self.decrypt)

        # IBM MQ
        query = self.odb.get_definition_wmq_list(server.cluster.id, True)
        self.config.definition_wmq = ConfigDict.from_query('definition_wmq', query, decrypt_func=self.decrypt)

        #
        # Definitions - end
        #

        #
        # Channels - start
        #

        # AMQP
        query = self.odb.get_channel_amqp_list(server.cluster.id, True)
        self.config.channel_amqp = ConfigDict.from_query('channel_amqp', query, decrypt_func=self.decrypt)

        # IBM MQ
        query = self.odb.get_channel_wmq_list(server.cluster.id, True)
        self.config.channel_wmq = ConfigDict.from_query('channel_wmq', query, decrypt_func=self.decrypt)

        #
        # Channels - end
        #

        #
        # Outgoing connections - start
        #

        # AMQP
        query = self.odb.get_out_amqp_list(server.cluster.id, True)
        self.config.out_amqp = ConfigDict.from_query('out_amqp', query, decrypt_func=self.decrypt)

        # Caches
        query = self.odb.get_cache_builtin_list(server.cluster.id, True)
        self.config.cache_builtin = ConfigDict.from_query('cache_builtin', query, decrypt_func=self.decrypt)

        query = self.odb.get_cache_memcached_list(server.cluster.id, True)
        self.config.cache_memcached = ConfigDict.from_query('cache_memcached', query, decrypt_func=self.decrypt)

        # FTP
        query = self.odb.get_out_ftp_list(server.cluster.id, True)
        self.config.out_ftp = ConfigDict.from_query('out_ftp', query, decrypt_func=self.decrypt)

        # IBM MQ
        query = self.odb.get_out_wmq_list(server.cluster.id, True)
        self.config.out_wmq = ConfigDict.from_query('out_wmq', query, decrypt_func=self.decrypt)

        # Odoo
        query = self.odb.get_out_odoo_list(server.cluster.id, True)
        self.config.out_odoo = ConfigDict.from_query('out_odoo', query, decrypt_func=self.decrypt)

        # SAP RFC
        query = self.odb.get_out_sap_list(server.cluster.id, True)
        self.config.out_sap = ConfigDict.from_query('out_sap', query, decrypt_func=self.decrypt)

        # REST
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'plain_http', True)
        self.config.out_plain_http = ConfigDict.from_query('out_plain_http', query, decrypt_func=self.decrypt)

        # SFTP
        query = self.odb.get_out_sftp_list(server.cluster.id, True)
        self.config.out_sftp = ConfigDict.from_query('out_sftp', query, decrypt_func=self.decrypt, drop_opaque=True)

        # SOAP
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'soap', True)
        self.config.out_soap = ConfigDict.from_query('out_soap', query, decrypt_func=self.decrypt)

        # SQL
        query = self.odb.get_out_sql_list(server.cluster.id, True)
        self.config.out_sql = ConfigDict.from_query('out_sql', query, decrypt_func=self.decrypt)

        # ZMQ channels
        query = self.odb.get_channel_zmq_list(server.cluster.id, True)
        self.config.channel_zmq = ConfigDict.from_query('channel_zmq', query, decrypt_func=self.decrypt)

        # ZMQ outgoing
        query = self.odb.get_out_zmq_list(server.cluster.id, True)
        self.config.out_zmq = ConfigDict.from_query('out_zmq', query, decrypt_func=self.decrypt)

        # WebSocket channels
        query = self.odb.get_channel_web_socket_list(server.cluster.id, True)
        self.config.channel_web_socket = ConfigDict.from_query('channel_web_socket', query, decrypt_func=self.decrypt)

        #
        # Outgoing connections - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #
        # Generic - start
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Connections
        query = self.odb.get_generic_connection_list(server.cluster.id, True)
        self.config.generic_connection = ConfigDict.from_query('generic_connection', query, decrypt_func=self.decrypt)

        #
        # Generic - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #
        # Notifications - start
        #

        # OpenStack Swift
        query = self.odb.get_notif_cloud_openstack_swift_list(server.cluster.id, True)
        self.config.notif_cloud_openstack_swift = ConfigDict.from_query('notif_cloud_openstack_swift',
            query, decrypt_func=self.decrypt)

        # SQL
        query = self.odb.get_notif_sql_list(server.cluster.id, True)
        self.config.notif_sql = ConfigDict.from_query('notif_sql', query, decrypt_func=self.decrypt)

        #
        # Notifications - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #
        # Security - start
        #

        # API keys
        query = self.odb.get_apikey_security_list(server.cluster.id, True)
        self.config.apikey = ConfigDict.from_query('apikey', query, decrypt_func=self.decrypt)

        # AWS
        query = self.odb.get_aws_security_list(server.cluster.id, True)
        self.config.aws = ConfigDict.from_query('aws', query, decrypt_func=self.decrypt)

        # HTTP Basic Auth
        query = self.odb.get_basic_auth_list(server.cluster.id, None, True)
        self.config.basic_auth = ConfigDict.from_query('basic_auth', query, decrypt_func=self.decrypt)

        # JWT
        query = self.odb.get_jwt_list(server.cluster.id, None, True)
        self.config.jwt = ConfigDict.from_query('jwt', query, decrypt_func=self.decrypt)

        # NTLM
        query = self.odb.get_ntlm_list(server.cluster.id, True)
        self.config.ntlm = ConfigDict.from_query('ntlm', query, decrypt_func=self.decrypt)

        # OAuth
        query = self.odb.get_oauth_list(server.cluster.id, True)
        self.config.oauth = ConfigDict.from_query('oauth', query, decrypt_func=self.decrypt)

        # OpenStack
        query = self.odb.get_openstack_security_list(server.cluster.id, True)
        self.config.openstack_security = ConfigDict.from_query('openstack_security', query, decrypt_func=self.decrypt)

        # RBAC - permissions
        query = self.odb.get_rbac_permission_list(server.cluster.id, True)
        self.config.rbac_permission = ConfigDict.from_query('rbac_permission', query, decrypt_func=self.decrypt)

        # RBAC - roles
        query = self.odb.get_rbac_role_list(server.cluster.id, True)
        self.config.rbac_role = ConfigDict.from_query('rbac_role', query, decrypt_func=self.decrypt)

        # RBAC - client roles
        query = self.odb.get_rbac_client_role_list(server.cluster.id, True)
        self.config.rbac_client_role = ConfigDict.from_query('rbac_client_role', query, decrypt_func=self.decrypt)

        # RBAC - role permission
        query = self.odb.get_rbac_role_permission_list(server.cluster.id, True)
        self.config.rbac_role_permission = ConfigDict.from_query('rbac_role_permission', query, decrypt_func=self.decrypt)

        # TLS CA certs
        query = self.odb.get_tls_ca_cert_list(server.cluster.id, True)
        self.config.tls_ca_cert = ConfigDict.from_query('tls_ca_cert', query, decrypt_func=self.decrypt)

        # TLS channel security
        query = self.odb.get_tls_channel_sec_list(server.cluster.id, True)
        self.config.tls_channel_sec = ConfigDict.from_query('tls_channel_sec', query, decrypt_func=self.decrypt)

        # TLS key/cert pairs
        query = self.odb.get_tls_key_cert_list(server.cluster.id, True)
        self.config.tls_key_cert = ConfigDict.from_query('tls_key_cert', query, decrypt_func=self.decrypt)

        # WS-Security
        query = self.odb.get_wss_list(server.cluster.id, True)
        self.config.wss = ConfigDict.from_query('wss', query, decrypt_func=self.decrypt)

        # Vault connections
        query = self.odb.get_vault_connection_list(server.cluster.id, True)
        self.config.vault_conn_sec = ConfigDict.from_query('vault_conn_sec', query, decrypt_func=self.decrypt)

        # XPath
        query = self.odb.get_xpath_sec_list(server.cluster.id, True)
        self.config.xpath_sec = ConfigDict.from_query('xpath_sec', query, decrypt_func=self.decrypt)

        # Encrypt all secrets
        self._encrypt_secrets()

        #
        # Security - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # All the HTTP/SOAP channels.
        http_soap = []

        for item in elems_with_opaque(self.odb.get_http_soap_list(server.cluster.id, 'channel')):

            hs_item = {}
            for key in item.keys():
                hs_item[key] = getattr(item, key)

            hs_item['match_target'] = get_match_target(hs_item, http_methods_allowed_re=self.http_methods_allowed_re)
            hs_item['match_target_compiled'] = Matcher(hs_item['match_target'], hs_item.get('match_slash', ''))

            http_soap.append(hs_item)

        self.config.http_soap = http_soap

        # Namespaces
        query = self.odb.get_namespace_list(server.cluster.id, True)
        self.config.msg_ns = ConfigDict.from_query('msg_ns', query, decrypt_func=self.decrypt)

        # XPath
        query = self.odb.get_xpath_list(server.cluster.id, True)
        self.config.xpath = ConfigDict.from_query('msg_xpath', query, decrypt_func=self.decrypt)

        # JSON Pointer
        query = self.odb.get_json_pointer_list(server.cluster.id, True)
        self.config.json_pointer = ConfigDict.from_query('json_pointer', query, decrypt_func=self.decrypt)

        # SimpleIO
        # In preparation for a SIO rewrite, we loaded SIO config from a file
        # but actual code paths require the pre-3.0 format so let's prepare it here.
        self.config.simple_io = ConfigDict('simple_io', Bunch())

        int_exact = self.sio_config.int_config.exact
        int_suffixes = self.sio_config.int_config.suffixes
        bool_prefixes = self.sio_config.bool_config.prefixes

        self.config.simple_io['int_parameters'] = int_exact
        self.config.simple_io['int_parameter_suffixes'] = int_suffixes
        self.config.simple_io['bool_parameter_prefixes'] = bool_prefixes

        # Maintain backward-compatibility with pre-3.1 versions that did not specify any particular encoding
        self.config.simple_io['bytes_to_str'] = {'encoding': self.sio_config.bytes_to_str_encoding or None}

        # Pub/sub
        self.config.pubsub = Bunch()

        # Pub/sub - endpoints
        query = self.odb.get_pubsub_endpoint_list(server.cluster.id, True)
        self.config.pubsub_endpoint = ConfigDict.from_query('pubsub_endpoint', query, decrypt_func=self.decrypt)

        # Pub/sub - topics
        query = self.odb.get_pubsub_topic_list(server.cluster.id, True)
        self.config.pubsub_topic = ConfigDict.from_query('pubsub_topic', query, decrypt_func=self.decrypt)

        # Pub/sub - subscriptions
        query = self.odb.get_pubsub_subscription_list(server.cluster.id, True)
        self.config.pubsub_subscription = ConfigDict.from_query('pubsub_subscription', query, decrypt_func=self.decrypt)

        # E-mail - SMTP
        query = self.odb.get_email_smtp_list(server.cluster.id, True)
        self.config.email_smtp = ConfigDict.from_query('email_smtp', query, decrypt_func=self.decrypt)

        # E-mail - IMAP
        query = self.odb.get_email_imap_list(server.cluster.id, True)
        self.config.email_imap = ConfigDict.from_query('email_imap', query, decrypt_func=self.decrypt)

        # Message paths
        self.config.msg_ns_store = NamespaceStore()
        self.config.json_pointer_store = JSONPointerStore()
        self.config.xpath_store = XPathStore()

        # HTTP access log should optionally ignore certain requests
        access_log_ignore = self.fs_server_config.get('logging', {}).get('http_access_log_ignore')
        if access_log_ignore:
            access_log_ignore = access_log_ignore if isinstance(access_log_ignore, list) else [access_log_ignore]
            self.needs_all_access_log = False
            self.access_log_ignore.update(access_log_ignore)

        # Assign config to worker
        self.worker_store.worker_config = self.config

# ################################################################################################################################

    def delete_object_rate_limiting(self, object_type, object_name):
        if self.rate_limiting.has_config(object_type, object_name):
            self.rate_limiting.delete(object_type, object_name)

# ################################################################################################################################

    def set_up_rate_limiting(self, _config_store=('apikey', 'basic_auth', 'jwt'), _sec_def=RATE_LIMIT.OBJECT_TYPE.SEC_DEF,
        _http_soap=RATE_LIMIT.OBJECT_TYPE.HTTP_SOAP):

        for config_store_name in _config_store:
            config_dict = self.config[config_store_name] # type: ConfigDict
            for object_name in config_dict: # type: unicode
                self.set_up_object_rate_limiting(_sec_def, object_name, config_store_name)

        for item in self.config['http_soap']: # type: dict
            # Do not try to set up rate limiting if we know there is no configuration for it available
            if 'is_rate_limit_active' in item:
                self.set_up_object_rate_limiting(_http_soap, item['name'], config=item)

# ################################################################################################################################

    def set_up_object_rate_limiting(self, object_type, object_name, config_store_name=None, config=None,
        _exact=RATE_LIMIT.TYPE.EXACT.id):
        # type: (unicode, unicode, unicode, dict) -> bool

        if not config:
            config = self.config[config_store_name].get(object_name) # type: ConfigDict
            config = config['config'] # type: dict

        is_rate_limit_active = config.get('is_rate_limit_active') or False # type: bool

        if is_rate_limit_active:

            # This is reusable no matter if it is edit or create action
            rate_limit_def = config['rate_limit_def']
            is_exact = config['rate_limit_type'] == _exact

            # Base dict that will be used as is, if we are to create the rate limiting configuration,
            # or it will be updated with existing configuration, if it already exists.
            rate_limit_config = {
                'id': '{}.{}'.format(object_type, config['id']),
                'is_active': is_rate_limit_active,
                'type_': object_type,
                'name': object_name,
                'parent_type': None,
                'parent_name': None,
            }

            # Do we have such configuration already?
            existing_config = self.rate_limiting.get_config(object_type, object_name)

            # .. if yes, we will be updating it
            if existing_config:
                rate_limit_config['parent_type'] = existing_config.parent_type
                rate_limit_config['parent_name'] = existing_config.parent_name

                self.rate_limiting.edit(object_type, object_name, rate_limit_config, rate_limit_def, is_exact)

            # .. otherwise, we will be creating a new one
            else:
                self.rate_limiting.create(rate_limit_config, rate_limit_def, is_exact)

        # We are not to have any rate limits, but it is possible that previously we were required to,
        # in which case this needs to be cleaned up.
        else:
            existing_config = self.rate_limiting.get_config(object_type, object_name)
            if existing_config:
                object_info = existing_config.object_info
                self.rate_limiting.delete(object_info.type_, object_info.name)

        return is_rate_limit_active

# ################################################################################################################################

    def _after_init_accepted(self, locally_deployed):

        # Deploy missing services found on other servers
        if locally_deployed:
            self.deploy_missing_services(locally_deployed)

        # Signal to ODB that we are done with deploying everything
        self.odb.on_deployment_finished()

        # Populate default pub/sub endpoint data
        self.default_internal_pubsub_endpoint_id = self.odb.get_default_internal_pubsub_endpoint().id

        # Default content type
        self.json_content_type = self.fs_server_config.content_type.json
        self.plain_xml_content_type = self.fs_server_config.content_type.plain_xml
        self.soap11_content_type = self.fs_server_config.content_type.soap11
        self.soap12_content_type = self.fs_server_config.content_type.soap12

# ################################################################################################################################

    def get_lua_programs(self):
        for item in 'internal', 'user':
            dir_name = os.path.join(self.repo_location, 'lua', item)
            for file_name in os.listdir(dir_name):

                lua_idx = file_name.find('.lua')
                name = file_name[0:lua_idx] if lua_idx else file_name
                program = open(os.path.join(dir_name, file_name)).read()

                yield [name, program]

# ################################################################################################################################

    def get_config_odb_data(self, parallel_server):
        """ Returns configuration with regards to ODB data.
        """
        odb_data = Bunch()
        odb_data.db_name = parallel_server.odb_data['db_name']
        odb_data.extra = parallel_server.odb_data['extra']
        odb_data.engine = parallel_server.odb_data['engine']
        odb_data.token = parallel_server.fs_server_config.main.token

        odb_data.is_odb = True

        if odb_data.engine != 'sqlite':
            odb_data.password = parallel_server.odb_data['password']
            odb_data.host = parallel_server.odb_data['host']
            odb_data.port = parallel_server.odb_data['port']
            odb_data.engine = parallel_server.odb_data['engine']
            odb_data.pool_size = parallel_server.odb_data['pool_size']
            odb_data.username = parallel_server.odb_data['username']

        # Note that we don't read is_active off of anywhere - ODB always must
        # be active and it's not a regular connection pool anyway.
        odb_data.is_active = True

        return odb_data

# ################################################################################################################################

    def _encrypt_secrets(self):
        """ All passwords are always encrypted so we need to look up any that are not,
        for instance, because it is a cluster newly migrated from 2.0 to 3.0, and encrypt them now in ODB.
        """
        sec_config_dict_types = ('apikey', 'aws', 'basic_auth', 'jwt', 'ntlm', 'oauth', 'openstack_security',
            'tls_key_cert', 'wss', 'vault_conn_sec', 'xpath_sec')

        # Global lock to make sure only one server attempts to do it at a time
        with self.zato_lock_manager('zato_encrypt_secrets'):

            # An SQL session shared by all updates
            with closing(self.odb.session()) as session:

                # Iterate over all security definitions
                for sec_config_dict_type in sec_config_dict_types:
                    config_dicts = getattr(self.config, sec_config_dict_type)
                    for config in config_dicts.values():
                        config = config['config']

                        # Continue to encryption only if needed and not already encrypted
                        if config.get('_encryption_needed'):
                            if not config['_encrypted_in_odb']:
                                odb_func = getattr(self.odb, '_migrate_30_encrypt_sec_{}'.format(sec_config_dict_type))

                                # Encrypt all params that are applicable
                                for secret_param in SECRETS.PARAMS:
                                    if secret_param in config:
                                        data = config[secret_param]
                                        if data:
                                            encrypted = self.encrypt(data)
                                            odb_func(session, config['id'], secret_param, encrypted)

                        # Clean up config afterwards
                        config.pop('_encryption_needed', None)
                        config.pop('_encrypted_in_odb', None)

                # Commit to SQL now that all updates are made
                session.commit()

# ################################################################################################################################

    def _after_init_non_accepted(self, server):
        raise NotImplementedError("This Zato version doesn't support join states other than ACCEPTED")

# ################################################################################################################################
# ################################################################################################################################
