# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import os
from logging import getLogger

# Zato
from zato.bunch import Bunch
from zato.common.api import PARAMS_PRIORITY, URL_PARAMS_PRIORITY
from zato.common.util.config import resolve_name
from zato.common.util.url_dispatcher import get_match_target
from zato.server.config import ConfigDict
from zato.url_dispatcher import Matcher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anyset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ConfigLoader:
    """ Loads server's configuration from the Rust ConfigStore.
    """

# ################################################################################################################################

    def set_up_security(self:'ParallelServer', _cluster_id:'int') -> 'None':
        self.config.apikey = ConfigDict(
            'apikey', config_manager=self.config_manager, entity_type='security', sec_type_filter='apikey')
        self.config.basic_auth = ConfigDict(
            'basic_auth', config_manager=self.config_manager, entity_type='security', sec_type_filter='basic_auth')
        self.config.ntlm = ConfigDict(
            'ntlm', config_manager=self.config_manager, entity_type='security', sec_type_filter='ntlm')
        self.config.oauth = ConfigDict(
            'oauth', config_manager=self.config_manager, entity_type='security', sec_type_filter='bearer_token')

# ################################################################################################################################

    def _config_dict_from_manager(self, name, entity_type):
        """ Build a delegating ConfigDict backed by the Rust ConfigStore.
        """
        return ConfigDict(name, config_manager=self.config_manager, entity_type=entity_type)

# ################################################################################################################################

    def set_up_config(
        self:'ParallelServer',  # type: ignore
        server:'object'
    ) -> 'None':

        # Search - ElasticSearch
        self.config.search_es = self._config_dict_from_manager('search_es', 'elastic_search')

        # Services
        self.config.service = self._config_dict_from_manager('service_list', 'service')

        # Channels - AMQP
        self.config.channel_amqp = self._config_dict_from_manager('channel_amqp', 'channel_amqp')

        # Outgoing - AMQP
        self.config.out_amqp = self._config_dict_from_manager('out_amqp', 'outgoing_amqp')

        # Caches
        self.config.cache_builtin = self._config_dict_from_manager('cache_builtin', 'cache')

        # FTP
        self.config.out_ftp = self._config_dict_from_manager('out_ftp', 'outgoing_ftp')

        # Odoo
        self.config.out_odoo = self._config_dict_from_manager('out_odoo', 'odoo')

        # SAP RFC
        self.config.out_sap = self._config_dict_from_manager('out_sap', 'outgoing_sap')

        # REST
        self.config.out_plain_http = self._config_dict_from_manager('out_plain_http', 'outgoing_rest')

        # SOAP
        self.config.out_soap = self._config_dict_from_manager('out_soap', 'outgoing_soap')

        # SQL
        self.config.out_sql = self._config_dict_from_manager('out_sql', 'sql')

        # Pub/sub subscriptions
        self.config.pubsub_subs = self._config_dict_from_manager('pubsub_subs', 'pubsub_subscription')

        # Generic connections
        self.config.generic_connection = self._config_dict_from_manager('generic_connection', 'generic_connection')

        # Security
        self.set_up_security(self.cluster_id)

        # HTTP/SOAP channels from ConfigStore (includes default-objects.yaml + any enmasse)
        http_soap = []

        for item in self.config_manager.get_list('channel_rest'):

            hs_item = dict(item)
            hs_item['name'] = resolve_name(hs_item.get('name', ''))
            hs_item.setdefault('soap_action', '')
            hs_item.setdefault('soap_version', None)
            hs_item.setdefault('transport', 'plain_http')
            hs_item.setdefault('connection', 'channel')
            hs_item.setdefault('data_format', 'json')
            hs_item.setdefault('sec_type', None)
            hs_item.setdefault('security_id', None)
            hs_item.setdefault('security_name', None)
            hs_item.setdefault('is_internal', False)
            hs_item.setdefault('is_active', True)
            hs_item.setdefault('id', 0)
            hs_item.setdefault('merge_url_params_req', True)
            hs_item.setdefault('match_slash', True)
            hs_item.setdefault('content_encoding', '')
            hs_item.setdefault('cache_type', None)
            hs_item.setdefault('cache_name', '')
            hs_item.setdefault('cache_expiry', 0)
            hs_item.setdefault('serialization_type', 'string')
            hs_item.setdefault('url_params_pri', URL_PARAMS_PRIORITY.DEFAULT)
            hs_item.setdefault('params_pri', PARAMS_PRIORITY.DEFAULT)
            hs_item.setdefault('method', '')

            service_name = hs_item.get('service_name') or hs_item.get('service') or ''
            hs_item['service_impl_name'] = self.service_store.name_to_impl_name[service_name]

            if 'service_name' not in hs_item and 'service' in hs_item:
                hs_item['service_name'] = hs_item['service']
            hs_item.setdefault('service_name', '')
            hs_item.setdefault('service_id', None)

            hs_item['match_target'] = get_match_target(hs_item, http_methods_allowed_re=self.http_methods_allowed_re)
            hs_item['match_target_compiled'] = Matcher(hs_item['match_target'], hs_item.get('match_slash', ''))

            gateway_service_list = hs_item.get('gateway_service_list') or []
            if isinstance(gateway_service_list, str):
                allowed = set(line.strip() for line in gateway_service_list.splitlines() if line.strip())
            else:
                allowed = set(gateway_service_list)
            self.gateway_services_allowed[hs_item.get('id', 0)] = allowed

            http_soap.append(hs_item)

        self.config.http_soap = http_soap

        self.config.simple_io = ConfigDict('simple_io', Bunch())

        # E-mail - SMTP
        self.config.email_smtp = self._config_dict_from_manager('email_smtp', 'email_smtp')

        # E-mail - IMAP
        self.config.email_imap = self._config_dict_from_manager('email_imap', 'email_imap')

        # Logging config
        _logging_stanza = self.fs_server_config.get('logging', {})

        access_log_ignore = _logging_stanza.get('http_access_log_ignore')
        if access_log_ignore:
            access_log_ignore = access_log_ignore if isinstance(access_log_ignore, list) else [access_log_ignore]
            self.needs_all_access_log = False
            self.access_log_ignore.update(access_log_ignore)

        _has_rest_log_ignore = 'rest_log_ignore' in _logging_stanza

        if not _has_rest_log_ignore:
            rest_log_ignore = ['/zato/api/invoke/', '/metrics', '/zato/ping']
        else:
            rest_log_ignore = _logging_stanza['rest_log_ignore']
            rest_log_ignore = rest_log_ignore if isinstance(rest_log_ignore, list) else [rest_log_ignore]

        self.rest_log_ignore.update(rest_log_ignore)

        # Assign config to worker
        self.worker_store.worker_config = self.config

# ################################################################################################################################

    def load_enmasse_yaml(self:'ParallelServer') -> 'None':
        """ Loads default objects and enmasse YAML into the config manager.
        """

        # Load local secrets first (security definitions with encrypted passwords)
        secrets_yaml_path = os.path.join(self.repo_location, 'secrets.yaml')
        if os.path.exists(secrets_yaml_path):
            logger.info('Loading secrets from %s', secrets_yaml_path)
            self.config_manager.load_yaml(secrets_yaml_path)

        # Then load default objects -- shipped with the codebase (channels referencing security by name)
        from zato.common.data import default_objects_yaml_path
        if os.path.exists(default_objects_yaml_path):
            logger.info('Loading default objects from %s', default_objects_yaml_path)
            self.config_manager.load_yaml(default_objects_yaml_path)

        # Then load any enmasse YAML from external directories (Docker, deploy_auto_from)
        enmasse_dirs = []

        docker_enmasse = '/opt/hot-deploy/enmasse'
        if os.path.isdir(docker_enmasse):
            enmasse_dirs.append(docker_enmasse)

        if self.deploy_auto_from:
            auto_enmasse = os.path.join(self.deploy_auto_from, 'enmasse')
            if os.path.isdir(auto_enmasse) and auto_enmasse not in enmasse_dirs:
                enmasse_dirs.append(auto_enmasse)

        for enmasse_dir in enmasse_dirs:
            for pattern in ('*.yaml', '*.yml'):
                for yaml_path in sorted(glob.glob(os.path.join(enmasse_dir, pattern))):
                    logger.info('Loading enmasse YAML from %s', yaml_path)
                    self.config_manager.load_yaml(yaml_path)

# ################################################################################################################################

    def _after_init_accepted(
        self: 'ParallelServer', # type: ignore
        locally_deployed        # type: anyset
    ) -> 'None':

        # Default content type
        self.json_content_type = self.fs_server_config.content_type.json

# ################################################################################################################################

    def _after_init_non_accepted(self, server:'ParallelServer') -> 'None':
        raise NotImplementedError("This Zato version doesn't support join states other than ACCEPTED")

# ################################################################################################################################
# ################################################################################################################################
