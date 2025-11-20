# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.client import wait_for_services, Default_Service_Wait_Timeout
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.cli.enmasse.importers.jira import JiraImporter
from zato.cli.enmasse.importers.ldap import LDAPImporter
from zato.cli.enmasse.importers.microsoft_365 import Microsoft365Importer
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter
from zato.common.odb.model import Cluster

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

for importer_module in ['zato.cli.enmasse.importers.security', 'zato.cli.enmasse.importers.channel_rest',
                        'zato.cli.enmasse.importers.group', 'zato.cli.enmasse.importers.cache',
                        'zato.cli.enmasse.importers.email_smtp', 'zato.cli.enmasse.importers.email_imap',
                        'zato.cli.enmasse.importers.es', 'zato.cli.enmasse.importers.odoo',
                        'zato.cli.enmasse.importers.scheduler', 'zato.cli.enmasse.importers.sql',
                        'zato.cli.enmasse.importers.confluence', 'zato.cli.enmasse.importers.jira',
                        'zato.cli.enmasse.importers.ldap', 'zato.cli.enmasse.importers.microsoft_365',
                        'zato.cli.enmasse.importers.outgoing_rest', 'zato.cli.enmasse.importers.outgoing_soap',
                        'zato.cli.enmasse.importers.pubsub_topic', 'zato.cli.enmasse.importers.pubsub_permission',
                        'zato.cli.enmasse.importers.pubsub_subscription']:
    importer_logger = logging.getLogger(importer_module)
    importer_logger.setLevel(logging.INFO)
    importer_logger.addHandler(handler)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseYAMLImporter:
    """ Imports enmasse YAML configuration files and builds an in-memory representation.
    """
    def __init__(self) -> 'None':

        # This is always the same
        self.cluster_id = ModuleCtx.Cluster_ID

        self.object_type = ModuleCtx.ObjectType
        self.object_alias = ModuleCtx.ObjectAlias

        self.sec_defs = {}
        self.group_defs = {}
        self.cache_defs = {}
        self.odoo_defs = {}
        self.smtp_defs = {}
        self.imap_defs = {}
        self.es_defs = {}
        self.sql_defs = {}
        self.job_defs = {}
        self.confluence_defs = {}
        self.jira_defs = {}
        self.ldap_defs = {}
        self.microsoft_365_defs = {}
        self.outgoing_rest_defs = {}
        self.outgoing_soap_defs = {}
        self.pubsub_topic_defs = {}
        self.pubsub_permission_defs = {}
        self.pubsub_subscription_defs = {}
        self.objects = {}
        self.cluster = None

        # Track created and updated objects for reporting
        self.created_objects = {}
        self.updated_objects = {}

        # Initialize importers
        self.security_importer = SecurityImporter(self)
        self.channel_importer = ChannelImporter(self)
        self.group_importer = GroupImporter(self)
        self.cache_importer = CacheImporter(self)
        self.odoo_importer = OdooImporter(self)
        self.smtp_importer = SMTPImporter(self)
        self.imap_importer = IMAPImporter(self)
        self.es_importer = ElasticSearchImporter(self)
        self.sql_importer = SQLImporter(self)
        self.scheduler_importer = SchedulerImporter(self)
        self.confluence_importer = ConfluenceImporter(self)
        self.jira_importer = JiraImporter(self)
        self.ldap_importer = LDAPImporter(self)
        self.microsoft_365_importer = Microsoft365Importer(self)
        self.outgoing_rest_importer = OutgoingRESTImporter(self)
        self.outgoing_soap_importer = OutgoingSOAPImporter(self)
        self.pubsub_topic_importer = PubSubTopicImporter(self)
        self.pubsub_permission_importer = PubSubPermissionImporter(self)
        self.pubsub_subscription_importer = PubSubSubscriptionImporter(self)

# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter_by(id=self.cluster_id).one()
        return self.cluster

# ################################################################################################################################

    def from_path(self, path:'str') -> 'stranydict':
        """ Imports YAML configuration from a file path.
        """
        if not os.path.exists(path):
            raise ValueError(f'Path does not exist -> {path}')

        # Convert the path to an absolute path
        path = os.path.abspath(path)
        base_dir = os.path.dirname(path)

        with open(path, 'r') as f:
            yaml_content = f.read()

        # Parse the YAML content
        config = yaml.safe_load(yaml_content)

        # Process includes if present
        if 'include' in config:
            config = self._process_includes(config, base_dir)

        return self._process_config(config)

# ################################################################################################################################

    def from_string(self, yaml_string:'str') -> 'stranydict':
        """ Imports YAML configuration from a string.
        """
        # Parse YAML into Python data structure
        config = yaml.safe_load(yaml_string)

        # Process the config (without include handling since we don't have a base directory)
        return self._process_config(config)

# ################################################################################################################################

    def _process_includes(self, config:'stranydict', base_dir:'str', processed_paths:'set | None'=None) -> 'stranydict':

        # Initialize set of processed paths to prevent recursive includes
        if processed_paths is None:
            processed_paths = set()

        # Get the list of files to include
        include_files = config.get('include', [])
        if not include_files:
            return config

        # Remove the include directive since we're processing it
        merged_config = {key: value for key, value in config.items() if key != 'include'}

        # Process each included file
        for include_path in include_files:

            # Resolve the path (absolute or relative to base_dir)
            if os.path.isabs(include_path):
                resolved_path = include_path
            else:
                resolved_path = os.path.normpath(os.path.join(base_dir, include_path))

            # Check if path exists
            if not os.path.exists(resolved_path):
                raise ValueError(f'Included file does not exist -> {resolved_path}')

            # Check for recursive/circular includes
            if resolved_path in processed_paths:
                raise ValueError(f'Circular include detected -> {resolved_path}')

            # Mark this path as processed
            processed_paths.add(resolved_path)

            # Read and parse the included file
            with open(resolved_path, 'r') as f:
                include_content = f.read()

            include_config = yaml.safe_load(include_content)

            # If the included file itself has includes, process them recursively
            include_dir = os.path.dirname(resolved_path)

            if 'include' in include_config:
                include_config = self._process_includes(include_config, include_dir, processed_paths)

            # Merge the included config with our current config
            self._merge_configs(merged_config, include_config)

        return merged_config

# ################################################################################################################################

    def _merge_configs(self, target:'stranydict', source:'stranydict') -> None:
        """ Merge source config into target config.
            This combines the lists for each section rather than overwriting.
        """

        for key, items in source.items():

            # Skip if no items for this object type
            if not items:
                continue

            # Initialize section if it doesn't exist
            if key not in target:
                target[key] = []

            # Add all items for this object type
            target[key].extend(items)

# ################################################################################################################################

    def _process_config(self, config:'stranydict') -> 'stranydict':
        """ Process a config dict into the expected result format.
            This is the final processing step after handling includes.
        """
        # Convert the raw YAML into a structured representation
        result = {}

        # Process each object type from the YAML
        for key, items in config.items():
            # Skip if no items for this object type
            if not items:
                continue

            # Process all items for this object type
            if key not in result:
                result[key] = []

            # Add all items for this object type
            result[key].extend(items)

        return result

# ################################################################################################################################

    def sync_security(self, security_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes security definitions from a YAML configuration with the database.
        """
        if not security_list:
            return [], []

        count = len(security_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} security {noun}')
        security_created, security_updated = self.security_importer.sync_security_definitions(security_list, session)

        created_count = len(security_created)
        updated_count = len(security_updated)
        logger.info(f'Processed security definitions: created={created_count} updated={updated_count}')

        return security_created, security_updated

# ################################################################################################################################

    def sync_groups(self, group_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes security groups from a YAML configuration with the database.
        """
        if not group_list:
            return [], []

        count = len(group_list)
        noun = 'group' if count == 1 else 'groups'
        logger.info(f'Processing {count} security {noun}')

        # Process each group item
        for idx, item in enumerate(group_list):
            logger.info('Group item %d: %s', idx, item)

        processed_groups = self.group_importer.sync_groups(group_list, session)

        # Get group definitions from the group importer and store them in our instance
        self.group_defs = self.group_importer.group_defs

        logger.info('Processed security groups: %d', len(processed_groups))

        return processed_groups

# ################################################################################################################################

    def sync_channel_rest(self, channel_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes REST channels from a YAML configuration with the database.
        """
        if not channel_list:
            return [], []

        count = len(channel_list)
        noun = 'channel' if count == 1 else 'channels'
        logger.info(f'Processing {count} REST {noun}')
        channels_created, channels_updated = self.channel_importer.sync_channel_rest(channel_list, session)
        created_count = len(channels_created)
        updated_count = len(channels_updated)
        logger.info(f'Processed REST channels: created={created_count} updated={updated_count}')

        return channels_created, channels_updated

# ################################################################################################################################

    def sync_cache(self, cache_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes cache definitions from a YAML configuration with the database.
        """
        if not cache_list:
            return [], []

        # Examine each cache item in detail
        for idx, item in enumerate(cache_list):
            if not item.get('name'):
                # Skip items without a name or log them if needed
                logger.warning('Cache item %d has no name, skipping', idx)
                continue

        cache_created, cache_updated = self.cache_importer.sync_cache_definitions(cache_list, session)

        # Get cache definitions from the cache importer
        self.cache_defs = self.cache_importer.cache_defs
        logger.info('Processed cache definitions: created=%d updated=%d', len(cache_created), len(cache_updated))

        return cache_created, cache_updated

# ################################################################################################################################

    def sync_odoo(self, odoo_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Odoo connection definitions from a YAML configuration with the database.
        """
        if not odoo_list:
            return [], []

        count = len(odoo_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Odoo connection {noun}')

        # Examine each Odoo item
        for idx, item in enumerate(odoo_list):
            logger.info('Odoo connection item %d: %s', idx, item)

        odoo_created, odoo_updated = self.odoo_importer.sync_odoo_definitions(odoo_list, session)

        # Get Odoo definitions from the Odoo importer
        self.odoo_defs = self.odoo_importer.odoo_defs
        logger.info('Processed Odoo connection definitions: created=%d updated=%d', len(odoo_created), len(odoo_updated))

        return odoo_created, odoo_updated

# ################################################################################################################################

    def sync_smtp(self, smtp_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SMTP connection definitions from a YAML configuration with the database.
        """
        if not smtp_list:
            return [], []

        count = len(smtp_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} SMTP connection {noun}')

        # Examine each SMTP item
        for idx, item in enumerate(smtp_list):
            logger.info('SMTP connection item %d: %s', idx, item)

        smtp_created, smtp_updated = self.smtp_importer.sync_smtp_definitions(smtp_list, session)

        # Get SMTP definitions from the SMTP importer
        self.smtp_defs = self.smtp_importer.smtp_defs
        logger.info('Processed SMTP connection definitions: created=%d updated=%d', len(smtp_created), len(smtp_updated))

        return smtp_created, smtp_updated

# ################################################################################################################################

    def sync_imap(self, imap_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes IMAP connection definitions from a YAML configuration with the database.
        """
        if not imap_list:
            return [], []

        count = len(imap_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} IMAP connection {noun}')

        # Examine each IMAP item
        for idx, item in enumerate(imap_list):
            logger.info('IMAP connection item %d: %s', idx, item)

        imap_created, imap_updated = self.imap_importer.sync_imap_definitions(imap_list, session)

        # Get IMAP definitions from the IMAP importer
        self.imap_defs = self.imap_importer.imap_defs
        logger.info('Processed IMAP connection definitions: created=%d updated=%d', len(imap_created), len(imap_updated))

        return imap_created, imap_updated

# ################################################################################################################################

    def sync_sql(self, sql_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes SQL connection pool definitions from a YAML configuration with the database.
        """
        if not sql_list:
            return [], []

        count = len(sql_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} SQL connection pool {noun}')

        # Examine each SQL connection pool item
        for idx, item in enumerate(sql_list):
            logger.info('SQL connection pool item %d: %s', idx, item)

        sql_created, sql_updated = self.sql_importer.sync_sql_definitions(sql_list, session)

        # Get SQL definitions from the SQL importer
        self.sql_defs = self.sql_importer.sql_defs
        logger.info('Processed SQL connection pool definitions: created=%d updated=%d', len(sql_created), len(sql_updated))

        return sql_created, sql_updated

# ################################################################################################################################

    def sync_scheduler(self, job_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes scheduler job definitions from a YAML configuration with the database.
        """
        if not job_list:
            return [], []

        count = len(job_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} scheduler job {noun}')

        # Examine each scheduler job item
        for idx, item in enumerate(job_list):
            logger.info('Scheduler job item %d: %s', idx, item)

        job_created, job_updated = self.scheduler_importer.sync_job_definitions(job_list, session)

        # Get scheduler job definitions from the scheduler importer
        self.job_defs = self.scheduler_importer.job_defs
        logger.info('Processed scheduler job definitions: created=%d updated=%d', len(job_created), len(job_updated))

        return job_created, job_updated

# ################################################################################################################################

    def sync_confluence(self, confluence_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Confluence connection definitions from a YAML configuration with the database.
        """
        if not confluence_list:
            return [], []

        count = len(confluence_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Confluence connection {noun}')

        # Examine each Confluence connection item
        for idx, item in enumerate(confluence_list):
            logger.info('Confluence connection item %d: %s', idx, item)

        confluence_created, confluence_updated = self.confluence_importer.sync_definitions(confluence_list, session)

        # Get Confluence definitions from the Confluence importer
        self.confluence_defs = self.confluence_importer.connection_defs
        logger.info('Processed Confluence connection definitions: created=%d updated=%d', len(confluence_created), len(confluence_updated))

        return confluence_created, confluence_updated

# ################################################################################################################################

    def sync_jira(self, jira_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Jira connection definitions from a YAML configuration with the database.
        """
        if not jira_list:
            return [], []

        count = len(jira_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Jira connection {noun}')

        # Examine each Jira connection item
        for idx, item in enumerate(jira_list):
            logger.info('Jira connection item %d: %s', idx, item)

        jira_created, jira_updated = self.jira_importer.sync_definitions(jira_list, session)

        # Get Jira definitions from the Jira importer
        self.jira_defs = self.jira_importer.connection_defs
        logger.info('Processed Jira connection definitions: created=%d updated=%d', len(jira_created), len(jira_updated))

        return jira_created, jira_updated

# ################################################################################################################################

    def sync_ldap(self, ldap_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes LDAP connection definitions from a YAML configuration with the database.
        """
        if not ldap_list:
            return [], []

        count = len(ldap_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} LDAP connection {noun}')

        # Examine each LDAP connection item
        for idx, item in enumerate(ldap_list):
            logger.info('LDAP connection item %d: %s', idx, item)

        ldap_created, ldap_updated = self.ldap_importer.sync_definitions(ldap_list, session)

        # Get LDAP definitions from the LDAP importer
        self.ldap_defs = self.ldap_importer.connection_defs
        logger.info('Processed LDAP connection definitions: created=%d updated=%d', len(ldap_created), len(ldap_updated))

        return ldap_created, ldap_updated

# ################################################################################################################################

    def sync_microsoft_365(self, microsoft_365_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes Microsoft 365 connection definitions from a YAML configuration with the database.
        """
        if not microsoft_365_list:
            return [], []

        count = len(microsoft_365_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} Microsoft 365 connection {noun}')

        # Examine each Microsoft 365 connection item
        for idx, item in enumerate(microsoft_365_list):
            logger.info('Microsoft 365 connection item %d: %s', idx, item)

        microsoft_365_created, microsoft_365_updated = self.microsoft_365_importer.sync_definitions(microsoft_365_list, session)

        # Get Microsoft 365 definitions from the Microsoft 365 importer
        self.microsoft_365_defs = self.microsoft_365_importer.connection_defs
        logger.info('Processed Microsoft 365 connection definitions: created=%d updated=%d', len(microsoft_365_created), len(microsoft_365_updated))

        return microsoft_365_created, microsoft_365_updated

# ################################################################################################################################

    def sync_es(self, es_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes ElasticSearch connection definitions from a YAML configuration with the database.
        """
        if not es_list:
            return [], []

        count = len(es_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} ElasticSearch connection {noun}')

        # Examine each ElasticSearch connection item
        for idx, item in enumerate(es_list):
            logger.info('ElasticSearch connection item %d: %s', idx, item)

        es_created, es_updated = self.es_importer.sync_es_definitions(es_list, session)

        # Get ElasticSearch definitions from the ElasticSearch importer
        self.es_defs = self.es_importer.es_defs
        logger.info('Processed ElasticSearch connection definitions: created=%d updated=%d', len(es_created), len(es_updated))

        return es_created, es_updated

# ################################################################################################################################

    def sync_pubsub_topic(self, topic_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub topic definitions from a YAML configuration with the database.
        """
        if not topic_list:
            return [], []

        count = len(topic_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} pubsub topic {noun}')

        # Examine each pubsub topic item
        for idx, item in enumerate(topic_list):
            logger.info('Pubsub topic item %d: %s', idx, item)

        topic_created, topic_updated = self.pubsub_topic_importer.sync_pubsub_topic_definitions(topic_list, session)

        # Get pubsub topic definitions from the pubsub topic importer
        self.pubsub_topic_defs = self.pubsub_topic_importer.pubsub_topic_defs
        logger.info('Processed pubsub topic definitions: created=%d updated=%d', len(topic_created), len(topic_updated))

        return topic_created, topic_updated

# ################################################################################################################################

    def sync_outgoing_rest(self, outgoing_list:'list', session:'SASession') -> 'tuple':
        """Synchronizes outgoing REST connection definitions from a YAML configuration with the database.
        """
        return self.outgoing_rest_importer.sync_outgoing_rest(outgoing_list, session)

# ################################################################################################################################

    def sync_outgoing_soap(self, outgoing_list:'list', session:'SASession') -> 'tuple':
        """Synchronizes outgoing SOAP connection definitions from a YAML configuration with the database.
        """
        return self.outgoing_soap_importer.sync_outgoing_soap(outgoing_list, session)

# ################################################################################################################################

    def sync_pubsub_permission(self, permission_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub permission definitions from a YAML configuration with the database.
        """
        if not permission_list:
            return [], []

        count = len(permission_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} pubsub permission {noun}')

        # Examine each pubsub permission item
        for idx, item in enumerate(permission_list):
            logger.info('Pubsub permission item %d: %s', idx, item)

        permission_created, permission_updated = self.pubsub_permission_importer.sync_pubsub_permission_definitions(permission_list, session)

        # Get pubsub permission definitions from the pubsub permission importer
        self.pubsub_permission_defs = self.pubsub_permission_importer.pubsub_permission_defs
        logger.info('Processed pubsub permission definitions: created=%d updated=%d', len(permission_created), len(permission_updated))

        return permission_created, permission_updated

# ################################################################################################################################

    def sync_pubsub_subscription(self, subscription_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub subscription definitions from a YAML configuration with the database.
        """
        if not subscription_list:
            return [], []

        count = len(subscription_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} pubsub subscription {noun}')

        # Examine each pubsub subscription item
        for idx, item in enumerate(subscription_list):
            logger.info('Pubsub subscription item %d: %s', idx, item)

        subscription_created, subscription_updated = self.pubsub_subscription_importer.sync_pubsub_subscription_definitions(subscription_list, session)

        # Get pubsub subscription definitions from the pubsub subscription importer
        self.pubsub_subscription_defs = self.pubsub_subscription_importer.pubsub_subscription_defs
        logger.info('Processed pubsub subscription definitions: created=%d updated=%d', len(subscription_created), len(subscription_updated))

        return subscription_created, subscription_updated

# ################################################################################################################################

    def sync_from_yaml(
        self,
        yaml_config:'stranydict',
        session:'SASession',
        server_dir:'str | None'=None,
        wait_for_services_timeout:'int | None'=None
    ) -> 'tuple':
        """ Synchronizes all objects from a YAML configuration with the database.
        """
        logger.info('Starting synchronization of YAML configuration')

        # Reset tracking dictionaries
        self.created_objects = {}
        self.updated_objects = {}

        # Wait for all services referenced in the configuration to be available
        if server_dir:
            timeout = wait_for_services_timeout or Default_Service_Wait_Timeout
            services_available = wait_for_services(yaml_config, server_dir, timeout_seconds=timeout)

            if not services_available:
                raise Exception('Expected services not found')

        # Process security definitions first
        sec_created, sec_updated = self.sync_security(yaml_config.get('security', []), session)
        if sec_created:
            self.created_objects['security'] = sec_created
        if sec_updated:
            self.updated_objects['security'] = sec_updated

        # Process security groups (depends on security definitions)
        groups_created, groups_updated = self.sync_groups(yaml_config.get('groups', []), session)
        if groups_created:
            self.created_objects['groups'] = groups_created
        if groups_updated:
            self.updated_objects['groups'] = groups_updated

        # Process REST channels which may depend on security definitions
        channels_created, channels_updated = self.sync_channel_rest(yaml_config.get('channel_rest', []), session)
        if channels_created:
            self.created_objects['channel_rest'] = channels_created
        if channels_updated:
            self.updated_objects['channel_rest'] = channels_updated

        # Process cache definitions
        cache_created, cache_updated = self.sync_cache(yaml_config.get('cache', []), session)
        if cache_created:
            self.created_objects['cache'] = cache_created
        if cache_updated:
            self.updated_objects['cache'] = cache_updated

        # Process Odoo connection definitions
        odoo_created, odoo_updated = self.sync_odoo(yaml_config.get('odoo', []), session)
        if odoo_created:
            self.created_objects['odoo'] = odoo_created
        if odoo_updated:
            self.updated_objects['odoo'] = odoo_updated

        # Process SMTP connection definitions
        smtp_created, smtp_updated = self.sync_smtp(yaml_config.get('email_smtp', []), session)
        if smtp_created:
            self.created_objects['email_smtp'] = smtp_created
        if smtp_updated:
            self.updated_objects['email_smtp'] = smtp_updated

        # Process IMAP connection definitions
        imap_created, imap_updated = self.sync_imap(yaml_config.get('email_imap', []), session)
        if imap_created:
            self.created_objects['email_imap'] = imap_created
        if imap_updated:
            self.updated_objects['email_imap'] = imap_updated

        # Process SQL connection pool definitions
        sql_created, sql_updated = self.sync_sql(yaml_config.get('sql', []), session)
        if sql_created:
            self.created_objects['sql'] = sql_created
        if sql_updated:
            self.updated_objects['sql'] = sql_updated

        # Process scheduler job definitions
        job_created, job_updated = self.sync_scheduler(yaml_config.get('scheduler', []), session)
        if job_created:
            self.created_objects['scheduler'] = job_created
        if job_updated:
            self.updated_objects['scheduler'] = job_updated

        # Process Confluence connection definitions
        confluence_created, confluence_updated = self.sync_confluence(yaml_config.get('confluence', []), session)
        if confluence_created:
            self.created_objects['confluence'] = confluence_created
        if confluence_updated:
            self.updated_objects['confluence'] = confluence_updated

        # Process Jira connection definitions
        jira_created, jira_updated = self.sync_jira(yaml_config.get('jira', []), session)
        if jira_created:
            self.created_objects['jira'] = jira_created
        if jira_updated:
            self.updated_objects['jira'] = jira_updated

        # Process LDAP connection definitions
        ldap_created, ldap_updated = self.sync_ldap(yaml_config.get('ldap', []), session)
        if ldap_created:
            self.created_objects['ldap'] = ldap_created
        if ldap_updated:
            self.updated_objects['ldap'] = ldap_updated

        # Process Microsoft 365 connection definitions
        ms365_created, ms365_updated = self.sync_microsoft_365(yaml_config.get('microsoft_365', []), session)
        if ms365_created:
            self.created_objects['microsoft_365'] = ms365_created
        if ms365_updated:
            self.updated_objects['microsoft_365'] = ms365_updated

        # Process ElasticSearch connection definitions
        es_created, es_updated = self.sync_es(yaml_config.get('elastic_search', []), session)
        if es_created:
            self.created_objects['elastic_search'] = es_created
        if es_updated:
            self.updated_objects['elastic_search'] = es_updated

        # Process outgoing REST connection definitions
        outgoing_rest_created, outgoing_rest_updated = self.sync_outgoing_rest(yaml_config.get('outgoing_rest', []), session)
        if outgoing_rest_created:
            self.created_objects['outgoing_rest'] = outgoing_rest_created
        if outgoing_rest_updated:
            self.updated_objects['outgoing_rest'] = outgoing_rest_updated

        # Process outgoing SOAP connection definitions
        outgoing_soap_created, outgoing_soap_updated = self.sync_outgoing_soap(yaml_config.get('outgoing_soap', []), session)
        if outgoing_soap_created:
            self.created_objects['outgoing_soap'] = outgoing_soap_created
        if outgoing_soap_updated:
            self.updated_objects['outgoing_soap'] = outgoing_soap_updated

        # Process pubsub topic definitions
        pubsub_topic_created, pubsub_topic_updated = self.sync_pubsub_topic(yaml_config.get('pubsub_topic', []), session)
        if pubsub_topic_created:
            self.created_objects['pubsub_topic'] = pubsub_topic_created
        if pubsub_topic_updated:
            self.updated_objects['pubsub_topic'] = pubsub_topic_updated

        # Process pubsub permission definitions
        pubsub_permission_created, pubsub_permission_updated = self.sync_pubsub_permission(yaml_config.get('pubsub_permission', []), session)
        if pubsub_permission_created:
            self.created_objects['pubsub_permission'] = pubsub_permission_created
        if pubsub_permission_updated:
            self.updated_objects['pubsub_permission'] = pubsub_permission_updated

        # Process pubsub subscription definitions
        pubsub_subscription_created, pubsub_subscription_updated = self.sync_pubsub_subscription(yaml_config.get('pubsub_subscription', []), session)
        if pubsub_subscription_created:
            self.created_objects['pubsub_subscription'] = pubsub_subscription_created
        if pubsub_subscription_updated:
            self.updated_objects['pubsub_subscription'] = pubsub_subscription_updated

        logger.info('YAML synchronization completed')

        return self.created_objects, self.updated_objects

# ################################################################################################################################
# ################################################################################################################################
