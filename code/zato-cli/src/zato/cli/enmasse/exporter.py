# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.exporters.cache import CacheExporter
from zato.cli.enmasse.exporters.email_imap import IMAPExporter
from zato.cli.enmasse.exporters.email_smtp import SMTPExporter
from zato.cli.enmasse.exporters.group import GroupExporter
from zato.cli.enmasse.exporters.odoo import OdooExporter
from zato.cli.enmasse.exporters.scheduler import SchedulerExporter
from zato.cli.enmasse.exporters.security import SecurityExporter
from zato.cli.enmasse.exporters.sql import SQLExporter
from zato.cli.enmasse.exporters.channel_rest import ChannelExporter
from zato.cli.enmasse.exporters.jira import JiraExporter
from zato.cli.enmasse.exporters.ldap import LDAPExporter
from zato.cli.enmasse.exporters.microsoft_365 import Microsoft365Exporter
from zato.cli.enmasse.exporters.confluence import ConfluenceExporter
from zato.cli.enmasse.exporters.es import ElasticSearchExporter
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
    """ Exports Zato objects to a YAML-compatible dictionary structure.
    """
    def __init__(self) -> 'None':

        # This is always the same
        self.cluster_id = ModuleCtx.Cluster_ID
        self.cluster:'any_' = None # To store the cluster object, similar to importer

        # Initialize exporters
        self.cache_exporter = CacheExporter(self)
        self.email_imap_exporter = IMAPExporter(self)
        self.email_smtp_exporter = SMTPExporter(self)
        self.group_exporter = GroupExporter(self)
        self.odoo_exporter = OdooExporter(self)
        self.scheduler_exporter = SchedulerExporter(self)
        self.security_exporter = SecurityExporter(self)
        self.sql_exporter = SQLExporter(self)
        self.channel_exporter = ChannelExporter(self)
        self.jira_exporter = JiraExporter(self)
        self.ldap_exporter = LDAPExporter(self)
        self.microsoft_365_exporter = Microsoft365Exporter(self)
        self.confluence_exporter = ConfluenceExporter(self)
        self.elastic_search_exporter = ElasticSearchExporter(self)
        self.outgoing_rest_exporter = OutgoingRESTExporter(self)
        self.outgoing_soap_exporter = OutgoingSOAPExporter(self)

# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter(Cluster.id == self.cluster_id).one() # type: ignore
        return self.cluster

# ################################################################################################################################

    def export_cache(self, session:'SASession') -> 'list':
        """ Exports cache definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        cache_list = self.cache_exporter.export(session, self.cluster_id)
        return cache_list

# ################################################################################################################################

    def export_odoo(self, session:'SASession') -> 'list':
        """ Exports Odoo connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        odoo_list = self.odoo_exporter.export(session, self.cluster_id)
        return odoo_list

# ################################################################################################################################

    def export_scheduler(self, session:'SASession') -> 'list':
        """ Exports scheduler job definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        scheduler_list = self.scheduler_exporter.export(session, self.cluster_id)
        return scheduler_list

# ################################################################################################################################

    def export_sql(self, session:'SASession') -> 'list':
        """ Exports SQL connection pool definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        sql_list = self.sql_exporter.export(session, self.cluster_id)
        return sql_list

# ################################################################################################################################

    def export_security(self, session:'SASession') -> 'list':
        """ Exports security definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        security_list = self.security_exporter.export(session, self.cluster_id)
        return security_list

# ################################################################################################################################

    def export_email_imap(self, session:'SASession') -> 'list':
        """ Exports email IMAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        imap_list = self.email_imap_exporter.export(session, self.cluster_id)
        return imap_list

# ################################################################################################################################

    def export_email_smtp(self, session:'SASession') -> 'list':
        """ Exports email SMTP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        smtp_list = self.email_smtp_exporter.export(session, self.cluster_id)
        return smtp_list

# ################################################################################################################################

    def export_groups(self, session:'SASession') -> 'list':
        """ Exports security group definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded if needed by exporter
        group_list = self.group_exporter.export(session, self.cluster_id)
        return group_list

# ################################################################################################################################

    def export_channel_rest(self, session:'SASession') -> 'list':
        """ Exports REST Channel definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        channel_list = self.channel_exporter.export(session, self.cluster_id)
        return channel_list

# ################################################################################################################################

    def export_outgoing_rest(self, session:'SASession') -> 'list':
        """ Exports outgoing REST connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        outgoing_rest_list = self.outgoing_rest_exporter.export(session, self.cluster_id)
        return outgoing_rest_list

# ################################################################################################################################

    def export_outgoing_soap(self, session:'SASession') -> 'list':
        """ Exports outgoing SOAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        outgoing_soap_list = self.outgoing_soap_exporter.export(session, self.cluster_id)
        return outgoing_soap_list

# ################################################################################################################################

    def export_jira(self, session:'SASession') -> 'list':
        """ Exports JIRA connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        jira_list = self.jira_exporter.export(session, self.cluster_id)
        return jira_list

# ################################################################################################################################

    def export_ldap(self, session:'SASession') -> 'list':
        """ Exports LDAP connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        ldap_list = self.ldap_exporter.export(session, self.cluster_id)
        return ldap_list

# ################################################################################################################################

    def export_microsoft_365(self, session:'SASession') -> 'list':
        """ Exports Microsoft 365 connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        microsoft_365_list = self.microsoft_365_exporter.export(session, self.cluster_id)
        return microsoft_365_list

# ################################################################################################################################

    def export_confluence(self, session:'SASession') -> 'list':
        """ Exports Confluence connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        confluence_list = self.confluence_exporter.export(session, self.cluster_id)
        return confluence_list

# ################################################################################################################################

    def export_elastic_search(self, session:'SASession') -> 'list':
        """ Exports ElasticSearch connection definitions.
        """
        _ = self.get_cluster(session) # Ensure cluster info is loaded
        elastic_search_list = self.elastic_search_exporter.export_es(session)
        return elastic_search_list

# ################################################################################################################################

    def export_to_dict(self, session:'SASession') -> 'stranydict':
        """ Exports all configured Zato objects to a dictionary.
            This dictionary can then be serialized to YAML.
        """
        logger.info('Starting export of Zato objects to dictionary format')

        output_dict: 'stranydict' = {}

        # Export cache definitions
        cache_defs = self.export_cache(session)
        if cache_defs:
            output_dict['cache'] = cache_defs

        # Export Odoo connection definitions
        odoo_defs = self.export_odoo(session)
        if odoo_defs:
            output_dict['odoo'] = odoo_defs

        # Export SQL connection pool definitions
        sql_defs = self.export_sql(session)
        if sql_defs:
            output_dict['sql'] = sql_defs

        # Export scheduler job definitions
        scheduler_defs = self.export_scheduler(session)
        if scheduler_defs:
            output_dict['scheduler'] = scheduler_defs

        # Export security definitions
        security_defs = self.export_security(session)
        if security_defs:
            output_dict['security'] = security_defs

        # Export email IMAP connection definitions
        email_imap_defs = self.export_email_imap(session)
        if email_imap_defs:
            output_dict['email_imap'] = email_imap_defs

        # Export email SMTP connection definitions
        email_smtp_defs = self.export_email_smtp(session)
        if email_smtp_defs:
            output_dict['email_smtp'] = email_smtp_defs

        # Export security group definitions
        group_defs = self.export_groups(session)
        if group_defs:
            output_dict['groups'] = group_defs

        # Export REST Channel definitions
        channel_rest_defs = self.export_channel_rest(session)
        if channel_rest_defs:
            output_dict['channel_rest'] = channel_rest_defs

        # Export outgoing REST connection definitions
        outgoing_rest_defs = self.export_outgoing_rest(session)
        if outgoing_rest_defs:
            output_dict['outgoing_rest'] = outgoing_rest_defs

        # Export outgoing SOAP connection definitions
        outgoing_soap_defs = self.export_outgoing_soap(session)
        if outgoing_soap_defs:
            output_dict['outgoing_soap'] = outgoing_soap_defs

        # Export JIRA connection definitions
        jira_defs = self.export_jira(session)
        if jira_defs:
            output_dict['jira'] = jira_defs

        # Export LDAP connection definitions
        ldap_defs = self.export_ldap(session)
        if ldap_defs:
            output_dict['ldap'] = ldap_defs

        # Export Microsoft 365 connection definitions
        microsoft_365_defs = self.export_microsoft_365(session)
        if microsoft_365_defs:
            output_dict['microsoft_365'] = microsoft_365_defs

        # Export Confluence connection definitions
        confluence_defs = self.export_confluence(session)
        if confluence_defs:
            output_dict['confluence'] = confluence_defs

        # Export ElasticSearch connection definitions
        elastic_search_defs = self.export_elastic_search(session)
        if elastic_search_defs:
            output_dict['elastic_search'] = elastic_search_defs

        logger.info('Successfully exported objects to dictionary format')
        return output_dict

# ################################################################################################################################
# ################################################################################################################################
