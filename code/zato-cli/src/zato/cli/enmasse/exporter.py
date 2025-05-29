# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from pathlib import Path

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.client import get_session_from_server_dir
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.exporters.security import SecurityExporter
from zato.cli.enmasse.exporters.group import GroupExporter
from zato.cli.enmasse.exporters.channel import ChannelExporter
from zato.cli.enmasse.exporters.cache import CacheExporter
from zato.cli.enmasse.exporters.odoo import OdooExporter
from zato.cli.enmasse.exporters.email_smtp import SMTPExporter
from zato.cli.enmasse.exporters.email_imap import IMAPExporter
from zato.cli.enmasse.exporters.es import ElasticSearchExporter
from zato.cli.enmasse.exporters.sql import SQLExporter
from zato.cli.enmasse.exporters.scheduler import SchedulerExporter
from zato.cli.enmasse.exporters.confluence import ConfluenceExporter
from zato.cli.enmasse.exporters.jira import JiraExporter
from zato.cli.enmasse.exporters.ldap import LDAPExporter
from zato.cli.enmasse.exporters.microsoft_365 import Microsoft365Exporter
from zato.cli.enmasse.exporters.outgoing_rest import OutgoingRESTExporter
from zato.cli.enmasse.exporters.outgoing_soap import OutgoingSOAPExporter
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

class EnmasseYAMLExporter:
    """ Exports objects from database to YAML configuration files.
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
        self.outgoing_rest_defs = {}
        self.outgoing_soap_defs = {}
        self.objects = {}
        self.cluster = None

        # Initialize exporters
        self.security_exporter = SecurityExporter(self)
        self.channel_exporter = ChannelExporter(self)
        self.group_exporter = GroupExporter(self)
        self.cache_exporter = CacheExporter(self)
        self.odoo_exporter = OdooExporter(self)
        self.smtp_exporter = SMTPExporter(self)
        self.imap_exporter = IMAPExporter(self)
        self.es_exporter = ElasticSearchExporter(self)
        self.sql_exporter = SQLExporter(self)
        self.scheduler_exporter = SchedulerExporter(self)
        self.confluence_exporter = ConfluenceExporter(self)
        self.jira_exporter = JiraExporter(self)
        self.ldap_exporter = LDAPExporter(self)
        self.microsoft_365_exporter = Microsoft365Exporter(self)
        self.outgoing_rest_exporter = OutgoingRESTExporter(self)
        self.outgoing_soap_exporter = OutgoingSOAPExporter(self)

# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter_by(id=self.cluster_id).first()
            logger.info('Found cluster: %s', self.cluster.name if self.cluster else None)
        return self.cluster

# ################################################################################################################################

    def to_yaml(self, config:'stranydict') -> 'str':
        """ Converts a configuration dictionary to YAML format.
        """
        # Use the correct YAML dumper to ensure proper formatting
        return yaml.dump(config, default_flow_style=False, sort_keys=False)

# ################################################################################################################################

    def to_file(self, yaml_string:'str', output_path:'str') -> 'None':
        """ Writes YAML string to a file.
        """
        logger.info('Writing YAML configuration to %s', output_path)
        output_dir = os.path.dirname(output_path)

        # Create directory if it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, 'w') as f:
            f.write(yaml_string)

        logger.info('Successfully wrote YAML configuration to file')

# ################################################################################################################################

    def export_security(self, session:'SASession') -> 'list':
        """ Exports security definitions from the database.
        """
        logger.info('Exporting security definitions')
        security_list = self.security_exporter.export_security_definitions(session)
        logger.info('Exported %d security definitions', len(security_list))
        return security_list

# ################################################################################################################################

    def export_groups(self, session:'SASession') -> 'list':
        """ Exports security groups from the database.
        """
        logger.info('Exporting security groups')
        group_list = self.group_exporter.export_group_definitions(session)
        logger.info('Exported %d security groups', len(group_list))
        return group_list

# ################################################################################################################################

    def export_channel_rest(self, session:'SASession') -> 'list':
        """ Exports REST channels from the database.
        """
        logger.info('Exporting REST channels')
        channel_list = self.channel_exporter.export_channel_definitions(session)
        logger.info('Exported %d REST channels', len(channel_list))
        return channel_list

# ################################################################################################################################

    def export_cache(self, session:'SASession') -> 'list':
        """ Exports cache definitions from the database.
        """
        logger.info('Exporting cache definitions')
        cache_list = self.cache_exporter.export_cache_definitions(session)
        logger.info('Exported %d cache definitions', len(cache_list))
        return cache_list

# ################################################################################################################################

    def export_odoo(self, session:'SASession') -> 'list':
        """ Exports Odoo connections from the database.
        """
        logger.info('Exporting Odoo connections')
        odoo_list = self.odoo_exporter.export_odoo_definitions(session)
        logger.info('Exported %d Odoo connections', len(odoo_list))
        return odoo_list

# ################################################################################################################################

    def export_smtp(self, session:'SASession') -> 'list':
        """ Exports SMTP connections from the database.
        """
        logger.info('Exporting SMTP connections')
        smtp_list = self.smtp_exporter.export_smtp_definitions(session)
        logger.info('Exported %d SMTP connections', len(smtp_list))
        return smtp_list

# ################################################################################################################################

    def export_imap(self, session:'SASession') -> 'list':
        """ Exports IMAP connections from the database.
        """
        logger.info('Exporting IMAP connections')
        imap_list = self.imap_exporter.export_imap_definitions(session)
        logger.info('Exported %d IMAP connections', len(imap_list))
        return imap_list

# ################################################################################################################################

    def export_sql(self, session:'SASession') -> 'list':
        """ Exports SQL connections from the database.
        """
        logger.info('Exporting SQL connections')
        sql_list = self.sql_exporter.export_sql_definitions(session)
        logger.info('Exported %d SQL connections', len(sql_list))
        return sql_list

# ################################################################################################################################

    def export_scheduler(self, session:'SASession') -> 'list':
        """ Exports scheduler jobs from the database.
        """
        logger.info('Exporting scheduler jobs')
        job_list = self.scheduler_exporter.export_scheduler_definitions(session)
        logger.info('Exported %d scheduler jobs', len(job_list))
        return job_list

# ################################################################################################################################

    def export_confluence(self, session:'SASession') -> 'list':
        """ Exports Confluence connections from the database.
        """
        logger.info('Exporting Confluence connections')
        confluence_list = self.confluence_exporter.export_confluence_definitions(session)
        logger.info('Exported %d Confluence connections', len(confluence_list))
        return confluence_list

# ################################################################################################################################

    def export_jira(self, session:'SASession') -> 'list':
        """ Exports Jira connections from the database.
        """
        logger.info('Exporting Jira connections')
        jira_list = self.jira_exporter.export_jira_definitions(session)
        logger.info('Exported %d Jira connections', len(jira_list))
        return jira_list

# ################################################################################################################################

    def export_ldap(self, session:'SASession') -> 'list':
        """ Exports LDAP connections from the database.
        """
        logger.info('Exporting LDAP connections')
        ldap_list = self.ldap_exporter.export_ldap_definitions(session)
        logger.info('Exported %d LDAP connections', len(ldap_list))
        return ldap_list

# ################################################################################################################################

    def export_microsoft_365(self, session:'SASession') -> 'list':
        """ Exports Microsoft 365 connections from the database.
        """
        logger.info('Exporting Microsoft 365 connections')
        microsoft_365_list = self.microsoft_365_exporter.export_microsoft_365_definitions(session)
        logger.info('Exported %d Microsoft 365 connections', len(microsoft_365_list))
        return microsoft_365_list

# ################################################################################################################################

    def export_outgoing_rest(self, session:'SASession') -> 'list':
        """ Exports Outgoing REST connections from the database.
        """
        logger.info('Exporting Outgoing REST connections')
        outgoing_rest_list = self.outgoing_rest_exporter.export_outgoing_rest_definitions(session)
        logger.info('Exported %d Outgoing REST connections', len(outgoing_rest_list))
        return outgoing_rest_list

# ################################################################################################################################

    def export_outgoing_soap(self, session:'SASession') -> 'list':
        """ Exports Outgoing SOAP connections from the database.
        """
        logger.info('Exporting Outgoing SOAP connections')
        outgoing_soap_list = self.outgoing_soap_exporter.export_outgoing_soap_definitions(session)
        logger.info('Exported %d Outgoing SOAP connections', len(outgoing_soap_list))
        return outgoing_soap_list

# ################################################################################################################################

    def export_es(self, session:'SASession') -> 'list':
        """ Exports ElasticSearch connections from the database.
        """
        logger.info('Exporting ElasticSearch connections')
        es_list = self.es_exporter.export_es_definitions(session)
        logger.info('Exported %d ElasticSearch connections', len(es_list))
        return es_list

# ################################################################################################################################

    def export_to_yaml(self, session:'SASession') -> 'stranydict':
        """ Exports all objects from the database to a YAML configuration dictionary.
            This is the main entry point for creating a complete YAML export.
        """
        logger.info('Starting export of database objects to YAML configuration')

        config = {}

        # Export security definitions first
        security_list = self.export_security(session)
        if security_list:
            config['security'] = security_list

        # Export security groups
        group_list = self.export_groups(session)
        if group_list:
            config['groups'] = group_list

        # Export REST channels
        channel_list = self.export_channel_rest(session)
        if channel_list:
            config['channel_rest'] = channel_list

        # Export outgoing REST
        outgoing_rest_list = self.export_outgoing_rest(session)
        if outgoing_rest_list:
            config['outgoing_rest'] = outgoing_rest_list

        # Export scheduler jobs
        job_list = self.export_scheduler(session)
        if job_list:
            config['scheduler'] = job_list

        # Export LDAP connections
        ldap_list = self.export_ldap(session)
        if ldap_list:
            config['ldap'] = ldap_list

        # Export SQL connections
        sql_list = self.export_sql(session)
        if sql_list:
            config['sql'] = sql_list

        # Export outgoing SOAP connections
        outgoing_soap_list = self.export_outgoing_soap(session)
        if outgoing_soap_list:
            config['outgoing_soap'] = outgoing_soap_list

        # Export Microsoft 365 connections
        microsoft_365_list = self.export_microsoft_365(session)
        if microsoft_365_list:
            config['microsoft_365'] = microsoft_365_list

        # Export cache definitions
        cache_list = self.export_cache(session)
        if cache_list:
            config['cache'] = cache_list

        # Export Confluence connections
        confluence_list = self.export_confluence(session)
        if confluence_list:
            config['confluence'] = confluence_list

        # Export IMAP connections
        imap_list = self.export_imap(session)
        if imap_list:
            config['email_imap'] = imap_list

        # Export SMTP connections
        smtp_list = self.export_smtp(session)
        if smtp_list:
            config['email_smtp'] = smtp_list

        # Export Jira connections
        jira_list = self.export_jira(session)
        if jira_list:
            config['jira'] = jira_list

        # Export Odoo connections
        odoo_list = self.export_odoo(session)
        if odoo_list:
            config['odoo'] = odoo_list

        # Export ElasticSearch connections
        es_list = self.export_es(session)
        if es_list:
            config['elastic_search'] = es_list

        logger.info('YAML export completed with %d object types', len(config))
        return config

# ################################################################################################################################

    def export_from_server(self, server_dir:'str', output_path:'str'=None, stdin_data:'str'=None) -> 'str':
        """ Exports all objects from a server's database to a YAML configuration file or string.
        """
        logger.info('Exporting enmasse configuration from server directory: %s', server_dir)

        # Get a session from the server directory
        session = get_session_from_server_dir(server_dir, stdin_data)

        try:
            # Get the cluster
            self.get_cluster(session)

            # Export all objects to a YAML configuration
            config = self.export_to_yaml(session)

            # Convert to YAML string
            yaml_string = self.to_yaml(config)

            # If output path is provided, write to file
            if output_path:
                self.to_file(yaml_string, output_path)

            return yaml_string

        finally:
            # Always close the session
            session.close()

# ################################################################################################################################
# ################################################################################################################################

def export_enmasse(server_dir:'str'=None, output_path:'str'=None, stdin_data:'str'=None) -> 'str':
    """ Convenience function to export enmasse configuration from a server.
    """
    if server_dir is None:
        server_dir = os.path.expanduser('~/env/qs-1/server1')

    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'enmasse-export.yaml')

    exporter = EnmasseYAMLExporter()
    yaml_string = exporter.export_from_server(server_dir, output_path, stdin_data)

    logger.info('Enmasse export completed to %s', output_path)
    return yaml_string

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Export configuration from the default server path
    server_path = os.path.expanduser('~/env/qs-1/server1')
    output_path = os.path.join(os.getcwd(), 'enmasse-export.yaml')

    # Export
    export_enmasse(server_path, output_path)

    # Print confirmation
    print(f'Exported enmasse configuration to {output_path}')

# ################################################################################################################################
# ################################################################################################################################
