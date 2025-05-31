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
from zato.cli.enmasse.exporters.channel import ChannelExporter
from zato.common.odb.model import Cluster

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, stranydict

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

# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter(Cluster.id == self.cluster_id).one()
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

        logger.info('Successfully exported objects to dictionary format')
        return output_dict

# ################################################################################################################################
# ################################################################################################################################
