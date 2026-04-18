# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.cli.enmasse.importers.channel_openapi import ChannelOpenAPIImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.jira import JiraImporter
from zato.cli.enmasse.importers.ldap import LDAPImporter
from zato.cli.enmasse.importers.microsoft_365 import Microsoft365Importer
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.sql import SQLImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseImporter:
    """ Imports YAML configuration into the Rust config store,
    preprocessing each section through its type-specific importer first.
    """

    section_map = {
        'security':            SecurityImporter,
        'groups':              GroupImporter,
        'channel_rest':        ChannelImporter,
        'channel_openapi':     ChannelOpenAPIImporter,
        'outgoing_rest':       OutgoingRESTImporter,
        'outgoing_soap':       OutgoingSOAPImporter,
        'scheduler':           SchedulerImporter,
        'sql':                 SQLImporter,
        'cache':               CacheImporter,
        'email_smtp':          SMTPImporter,
        'email_imap':          IMAPImporter,
        'odoo':                OdooImporter,
        'ldap':                LDAPImporter,
        'confluence':          ConfluenceImporter,
        'jira':                JiraImporter,
        'microsoft_365':       Microsoft365Importer,
        'elastic_search':      ElasticSearchImporter,
        'pubsub_topic':        PubSubTopicImporter,
        'pubsub_permission':   PubSubPermissionImporter,
        'pubsub_subscription': PubSubSubscriptionImporter,
    }

    def __init__(self, config_manager:'any_') -> 'None':
        self.config_manager = config_manager

# ################################################################################################################################

    def import_(self, yaml_string:'str') -> 'None':
        """ Parses the YAML string, preprocesses each section through its
        type-specific importer, then passes the preprocessed YAML to the config store.
        """
        import os
        import yaml

        yaml_string = os.path.expandvars(yaml_string)
        data = yaml.safe_load(yaml_string)
        if not data:
            return

        for section_key, importer_class in self.section_map.items():
            items = data.get(section_key)
            if items:
                data[section_key] = importer_class.preprocess(items)
            elif section_key in data:
                del data[section_key]

        if not data:
            return

        preprocessed_yaml = yaml.dump(data, default_flow_style=False, sort_keys=True)
        self.config_manager.load_yaml_string(preprocessed_yaml)

# ################################################################################################################################
# ################################################################################################################################
