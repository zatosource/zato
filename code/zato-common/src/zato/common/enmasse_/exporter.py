# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.exporters.cache import CacheExporter
from zato.cli.enmasse.exporters.channel_openapi import ChannelOpenAPIExporter
from zato.cli.enmasse.exporters.channel_rest import ChannelExporter
from zato.cli.enmasse.exporters.confluence import ConfluenceExporter
from zato.cli.enmasse.exporters.email_imap import IMAPExporter
from zato.cli.enmasse.exporters.email_smtp import SMTPExporter
from zato.cli.enmasse.exporters.es import ElasticSearchExporter
from zato.cli.enmasse.exporters.group import GroupExporter
from zato.cli.enmasse.exporters.jira import JiraExporter
from zato.cli.enmasse.exporters.ldap import LDAPExporter
from zato.cli.enmasse.exporters.microsoft_365 import Microsoft365Exporter
from zato.cli.enmasse.exporters.odoo import OdooExporter
from zato.cli.enmasse.exporters.outgoing_rest import OutgoingRESTExporter
from zato.cli.enmasse.exporters.outgoing_soap import OutgoingSOAPExporter
from zato.cli.enmasse.exporters.pubsub_permission import PubSubPermissionExporter
from zato.cli.enmasse.exporters.pubsub_subscription import PubSubSubscriptionExporter
from zato.cli.enmasse.exporters.pubsub_topic import PubSubTopicExporter
from zato.cli.enmasse.exporters.scheduler import SchedulerExporter
from zato.cli.enmasse.exporters.security import SecurityExporter
from zato.cli.enmasse.exporters.sql import SQLExporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseExporter:
    """ Exports Zato objects from the config store to YAML.
    """
    def __init__(self, config_store:'any_') -> 'None':

        self.config_store = config_store

        self.cache_exporter = CacheExporter(self)
        self.channel_exporter = ChannelExporter(self)
        self.channel_openapi_exporter = ChannelOpenAPIExporter(self)
        self.confluence_exporter = ConfluenceExporter(self)
        self.elastic_search_exporter = ElasticSearchExporter(self)
        self.email_imap_exporter = IMAPExporter(self)
        self.email_smtp_exporter = SMTPExporter(self)
        self.group_exporter = GroupExporter(self)
        self.jira_exporter = JiraExporter(self)
        self.ldap_exporter = LDAPExporter(self)
        self.microsoft_365_exporter = Microsoft365Exporter(self)
        self.odoo_exporter = OdooExporter(self)
        self.outgoing_rest_exporter = OutgoingRESTExporter(self)
        self.outgoing_soap_exporter = OutgoingSOAPExporter(self)
        self.pubsub_permission_exporter = PubSubPermissionExporter(self)
        self.pubsub_subscription_exporter = PubSubSubscriptionExporter(self)
        self.pubsub_topic_exporter = PubSubTopicExporter(self)
        self.scheduler_exporter = SchedulerExporter(self)
        self.security_exporter = SecurityExporter(self)
        self.sql_exporter = SQLExporter(self)

# ################################################################################################################################

    def export(self) -> 'str':
        """ Exports all configured Zato objects to a YAML string.
        """
        import yaml
        data = self.export_to_dict()
        if not data:
            return ''
        return yaml.dump(data, default_flow_style=False, sort_keys=True)

# ################################################################################################################################

    def export_to_dict(self) -> 'stranydict':
        """ Exports all configured Zato objects to a filtered dictionary.
        """
        logger.info('Starting export of Zato objects')

        raw = self.config_store.export_to_dict()
        output_dict:'stranydict' = {}

        section_map = {
            'security':            ('security',            self.security_exporter),
            'groups':              ('groups',              self.group_exporter),
            'channel_rest':        ('channel_rest',        self.channel_exporter),
            'channel_openapi':     ('channel_openapi',     self.channel_openapi_exporter),
            'outgoing_rest':       ('outgoing_rest',       self.outgoing_rest_exporter),
            'outgoing_soap':       ('outgoing_soap',       self.outgoing_soap_exporter),
            'scheduler':           ('scheduler',           self.scheduler_exporter),
            'sql':                 ('sql',                 self.sql_exporter),
            'cache':               ('cache',               self.cache_exporter),
            'email_smtp':          ('email_smtp',          self.email_smtp_exporter),
            'email_imap':          ('email_imap',          self.email_imap_exporter),
            'odoo':                ('odoo',                self.odoo_exporter),
            'ldap':                ('ldap',                self.ldap_exporter),
            'confluence':          ('confluence',          self.confluence_exporter),
            'jira':                ('jira',                self.jira_exporter),
            'microsoft_365':       ('microsoft_365',       self.microsoft_365_exporter),
            'elastic_search':      ('elastic_search',      self.elastic_search_exporter),
            'pubsub_topic':        ('pubsub_topic',        self.pubsub_topic_exporter),
            'pubsub_permission':   ('pubsub_permission',   self.pubsub_permission_exporter),
            'pubsub_subscription': ('pubsub_subscription', self.pubsub_subscription_exporter),
        }

        for raw_key, (output_key, exporter) in section_map.items():
            raw_items = raw.get(raw_key, [])
            if raw_items:
                filtered = exporter.export(raw_items)
                if filtered:
                    output_dict[output_key] = filtered

        logger.info('Successfully exported objects to dictionary format')
        return output_dict

# ################################################################################################################################
# ################################################################################################################################
