# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel import ChannelImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.cli.enmasse.importers.es import ESImporter
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.cli.enmasse.importers.jira import JiraImporter
from zato.cli.enmasse.importers.ldap import LDAPImporter
from zato.cli.enmasse.importers.microsoft_365 import Microsoft365Importer
from zato.common.odb.model import Cluster

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

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
        self.objects = {}
        self.cluster = None

        # Initialize importers
        self.security_importer = SecurityImporter(self)
        self.channel_importer = ChannelImporter(self)
        self.group_importer = GroupImporter(self)
        self.cache_importer = CacheImporter(self)
        self.odoo_importer = OdooImporter(self)
        self.smtp_importer = SMTPImporter(self)
        self.imap_importer = IMAPImporter(self)
        self.es_importer = ESImporter(self)
        self.sql_importer = SQLImporter(self)
        self.scheduler_importer = SchedulerImporter(self)
        self.confluence_importer = ConfluenceImporter(self)
        self.jira_importer = JiraImporter(self)
        self.ldap_importer = LDAPImporter(self)
        self.microsoft_365_importer = Microsoft365Importer(self)

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

        with open(path, 'r') as f:
            yaml_content = f.read()

        return self.from_string(yaml_content)

# ################################################################################################################################

    def from_string(self, yaml_string:'str') -> 'stranydict':
        """ Imports YAML configuration from a string.
        """
        # Parse YAML into Python data structure
        config = yaml.safe_load(yaml_string)

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

        logger.info('Processing %d security definitions', len(security_list))
        security_created, security_updated = self.security_importer.sync_security_definitions(security_list, session)

        # Get security definitions from the security importer
        self.sec_defs = self.security_importer.sec_defs
        logger.info('Processed security definitions: created=%d updated=%d', len(security_created), len(security_updated))

        return security_created, security_updated

# ################################################################################################################################

    def sync_groups(self, group_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes security groups from a YAML configuration with the database.
        """
        if not group_list:
            return [], []

        logger.info('Processing %d security groups', len(group_list))
        groups_created, groups_updated = self.group_importer.sync_groups(group_list, session)
        logger.info('Processed security groups: created=%d updated=%d', len(groups_created), len(groups_updated))

        return groups_created, groups_updated

# ################################################################################################################################

    def sync_channel_rest(self, channel_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes REST channels from a YAML configuration with the database.
        """
        if not channel_list:
            return [], []

        logger.info('Processing %d REST channels', len(channel_list))
        channels_created, channels_updated = self.channel_importer.sync_channel_rest(channel_list, session)
        logger.info('Processed REST channels: created=%d updated=%d', len(channels_created), len(channels_updated))

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

        logger.info('Processing %d Odoo connection definitions', len(odoo_list))

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

        logger.info('Processing %d SMTP connection definitions', len(smtp_list))

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

        logger.info('Processing %d IMAP connection definitions', len(imap_list))

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

        logger.info('Processing %d SQL connection pool definitions', len(sql_list))

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

        logger.info('Processing %d scheduler job definitions', len(job_list))

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

        logger.info('Processing %d Confluence connection definitions', len(confluence_list))

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

        logger.info('Processing %d Jira connection definitions', len(jira_list))

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

        logger.info('Processing %d LDAP connection definitions', len(ldap_list))

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

        logger.info('Processing %d Microsoft 365 connection definitions', len(microsoft_365_list))

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

        logger.info('Processing %d ElasticSearch connection definitions', len(es_list))

        # Examine each ElasticSearch connection item
        for idx, item in enumerate(es_list):
            logger.info('ElasticSearch connection item %d: %s', idx, item)

        es_created, es_updated = self.es_importer.sync_es_definitions(es_list, session)

        # Get ElasticSearch definitions from the ElasticSearch importer
        self.es_defs = self.es_importer.es_defs
        logger.info('Processed ElasticSearch connection definitions: created=%d updated=%d', len(es_created), len(es_updated))

        return es_created, es_updated

# ################################################################################################################################

    def sync_from_yaml(self, yaml_config:'stranydict', session:'SASession') -> 'None':
        """ Synchronizes all objects from a YAML configuration with the database.
            This is the main entry point for processing a complete YAML file.
        """
        logger.info('Starting synchronization of YAML configuration')

        # Process security definitions first
        self.sync_security(yaml_config.get('security', []), session)

        # Process security groups (depends on security definitions)
        self.sync_groups(yaml_config.get('groups', []), session)

        # Process REST channels which may depend on security definitions
        self.sync_channel_rest(yaml_config.get('channel_rest', []), session)

        # Process cache definitions
        self.sync_cache(yaml_config.get('cache', []), session)

        # Process Odoo connection definitions
        self.sync_odoo(yaml_config.get('odoo', []), session)

        # Process SMTP connection definitions
        self.sync_smtp(yaml_config.get('email_smtp', []), session)

        # Process IMAP connection definitions
        self.sync_imap(yaml_config.get('email_imap', []), session)

        # Process SQL connection pool definitions
        self.sync_sql(yaml_config.get('sql', []), session)

        # Process scheduler job definitions
        self.sync_scheduler(yaml_config.get('scheduler', []), session)

        # Process Confluence connection definitions
        self.sync_confluence(yaml_config.get('confluence', []), session)

        # Process Jira connection definitions
        self.sync_jira(yaml_config.get('jira', []), session)

        # Process LDAP connection definitions
        self.sync_ldap(yaml_config.get('ldap', []), session)

        # Process Microsoft 365 connection definitions
        self.sync_microsoft_365(yaml_config.get('microsoft_365', []), session)

        # Process ElasticSearch connection definitions
        self.sync_es(yaml_config.get('search_es', []), session)

        logger.info('YAML synchronization completed')

# ################################################################################################################################
# ################################################################################################################################
