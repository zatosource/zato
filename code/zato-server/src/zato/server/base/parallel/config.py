# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from logging import getLogger

# Zato
from zato.bunch import Bunch
from zato.common.const import SECRETS, ServiceConst
from zato.common.util.config import resolve_name
from zato.common.util.sql import elems_with_opaque
from zato.common.util.url_dispatcher import get_match_target
from zato.server.config import ConfigDict
from zato.url_dispatcher import Matcher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.model import Server as ServerModel
    from zato.common.typing_ import anydict, anydictnone, anyset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Config_Store = ('apikey', 'basic_auth',)

# ################################################################################################################################
# ################################################################################################################################

class ConfigLoader:
    """ Loads server's configuration.
    """

# ################################################################################################################################

    def set_up_security(self:'ParallelServer', cluster_id:'int') -> 'None':

        # API keys
        query = self.odb.get_apikey_security_list(cluster_id, True)
        self.config.apikey = ConfigDict.from_query('apikey', query, decrypt_func=self.decrypt)

        # HTTP Basic Auth
        query = self.odb.get_basic_auth_list(cluster_id, None, True)
        self.config.basic_auth = ConfigDict.from_query('basic_auth', query, decrypt_func=self.decrypt)

        # NTLM
        query = self.odb.get_ntlm_list(cluster_id, True)
        self.config.ntlm = ConfigDict.from_query('ntlm', query, decrypt_func=self.decrypt)

        # OAuth
        query = self.odb.get_oauth_list(cluster_id, True)
        self.config.oauth = ConfigDict.from_query('oauth', query, decrypt_func=self.decrypt)

        # Encrypt all secrets
        self._encrypt_secrets()

# ################################################################################################################################

    def set_up_config(
        self:'ParallelServer',  # type: ignore
        server:'ServerModel'
    ) -> 'None':

        #
        # Search - start
        #

        query = self.odb.get_search_es_list(server.cluster.id, True)
        self.config.search_es = ConfigDict.from_query('search_es', query, decrypt_func=self.decrypt)

        #
        # Search - end
        #

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Services
        query = self.odb.get_service_list(server.cluster.id, True)
        self.config.service = ConfigDict.from_query('service_list', query, decrypt_func=self.decrypt)

        #
        # Channels - start
        #

        # AMQP
        query = self.odb.get_channel_amqp_list(server.cluster.id, True)
        self.config.channel_amqp = ConfigDict.from_query('channel_amqp', query, decrypt_func=self.decrypt)

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

        # FTP
        query = self.odb.get_out_ftp_list(server.cluster.id, True)
        self.config.out_ftp = ConfigDict.from_query('out_ftp', query, decrypt_func=self.decrypt)

        # Odoo
        query = self.odb.get_out_odoo_list(server.cluster.id, True)
        self.config.out_odoo = ConfigDict.from_query('out_odoo', query, decrypt_func=self.decrypt)

        # SAP RFC
        query = self.odb.get_out_sap_list(server.cluster.id, True)
        self.config.out_sap = ConfigDict.from_query('out_sap', query, decrypt_func=self.decrypt)

        # REST
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'plain_http', True)
        self.config.out_plain_http = ConfigDict.from_query('out_plain_http', query, decrypt_func=self.decrypt)

        # SOAP
        query = self.odb.get_http_soap_list(server.cluster.id, 'outgoing', 'soap', True)
        self.config.out_soap = ConfigDict.from_query('out_soap', query, decrypt_func=self.decrypt)

        # SQL
        query = self.odb.get_out_sql_list(server.cluster.id, True)
        self.config.out_sql = ConfigDict.from_query('out_sql', query, decrypt_func=self.decrypt)

        # Pub/sub
        query = self.odb.get_pubsub_subscription_list(server.cluster.id, True)
        self.config.pubsub_subs = ConfigDict.from_query('pubsub_subs', query, decrypt_func=self.decrypt)

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
        # Security - start
        #

        self.set_up_security(server.cluster_id)

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

            hs_item['name'] = resolve_name(hs_item['name'])
            hs_item['match_target'] = get_match_target(hs_item, http_methods_allowed_re=self.http_methods_allowed_re)
            hs_item['match_target_compiled'] = Matcher(hs_item['match_target'], hs_item.get('match_slash', ''))

            http_soap.append(hs_item)

        self.config.http_soap = http_soap

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

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # E-mail - SMTP
        query = self.odb.get_email_smtp_list(server.cluster.id, True)
        self.config.email_smtp = ConfigDict.from_query('email_smtp', query, decrypt_func=self.decrypt)

        # E-mail - IMAP
        query = self.odb.get_email_imap_list(server.cluster.id, True)
        self.config.email_imap = ConfigDict.from_query('email_imap', query, decrypt_func=self.decrypt)

        # .. reusable ..
        _logging_stanza = self.fs_server_config.get('logging', {})

        # HTTP access log should optionally ignore certain requests ..
        access_log_ignore = _logging_stanza.get('http_access_log_ignore')
        if access_log_ignore:
            access_log_ignore = access_log_ignore if isinstance(access_log_ignore, list) else [access_log_ignore]
            self.needs_all_access_log = False
            self.access_log_ignore.update(access_log_ignore)

        # .. same goes for REST log entries that go to the server log ..

        # .. if it does not exist, we need to populate it ourselves ..
        _has_rest_log_ignore = 'rest_log_ignore' in _logging_stanza

        if not _has_rest_log_ignore:
            rest_log_ignore = [ServiceConst.API_Admin_Invoke_Url_Path, '/metrics', '/zato/ping']
        else:
            rest_log_ignore = _logging_stanza['rest_log_ignore']
            rest_log_ignore = rest_log_ignore if isinstance(rest_log_ignore, list) else [rest_log_ignore]

        # .. now, update the set of channels to ignore the REST log for ..
        self.rest_log_ignore.update(rest_log_ignore)

        # Assign config to worker
        self.worker_store.worker_config = self.config

# ################################################################################################################################

    def _after_init_accepted(
        self: 'ParallelServer', # type: ignore
        locally_deployed        # type: anyset
    ) -> 'None':

        # Signal to ODB that we are done with deploying everything
        self.odb.on_deployment_finished()

        # Default content type
        self.json_content_type = self.fs_server_config.content_type.json

# ################################################################################################################################

    def get_config_odb_data(self, parallel_server:'ParallelServer') -> 'Bunch':
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

    def _encrypt_secrets(
        self: 'ParallelServer' # type: ignore
    ) -> 'None':

        sec_config_dict_types = ('apikey', 'basic_auth', 'ntlm', 'oauth',)

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
                                odb_func = getattr(self.odb, 'encrypt_sec_{}'.format(sec_config_dict_type))

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

    def _after_init_non_accepted(self, server:'ParallelServer') -> 'None':
        raise NotImplementedError("This Zato version doesn't support join states other than ACCEPTED")

# ################################################################################################################################
# ################################################################################################################################
