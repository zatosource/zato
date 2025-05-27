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
        self.objects = {}
        self.cluster = None

        # Initialize importers
        self.security_importer = SecurityImporter(self)
        self.channel_importer = ChannelImporter(self)
        self.group_importer = GroupImporter(self)

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


    def sync_from_yaml(self, yaml_config:'stranydict', session:'SASession') -> 'None':
        """ Synchronizes all objects from a YAML configuration with the database.
            This is the main entry point for processing a complete YAML file.
        """
        logger.info('Starting synchronization of YAML configuration')

        # First process security definitions
        security_list = yaml_config.get('security', [])
        if security_list:
            logger.info('Processing %d security definitions', len(security_list))
            security_created, security_updated = self.security_importer.sync_security_definitions(security_list, session)

            # Get security definitions from the security importer
            self.sec_defs = self.security_importer.sec_defs
            logger.info('Processed security definitions: created=%d updated=%d', len(security_created), len(security_updated))

        # Process security groups (depends on security definitions)
        group_list = yaml_config.get('groups', [])
        if group_list:
            logger.info('Processing %d security groups', len(group_list))
            groups_created, groups_updated = self.group_importer.sync_groups(group_list, session)
            logger.info('Processed security groups: created=%d updated=%d', len(groups_created), len(groups_updated))

        # Then process REST channels which may depend on security definitions
        channel_list = yaml_config.get('channel_rest', [])
        if channel_list:
            logger.info('Processing %d REST channels', len(channel_list))
            channels_created, channels_updated = self.channel_importer.sync_channel_rest(channel_list, session)
            logger.info('Processed REST channels: created=%d updated=%d', len(channels_created), len(channels_updated))

        logger.info('YAML synchronization completed')

# ################################################################################################################################
# ################################################################################################################################
