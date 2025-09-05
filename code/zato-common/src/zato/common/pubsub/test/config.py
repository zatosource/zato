# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger

# PyYAML
from yaml import safe_load as yaml_load

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.test.users_yaml import calculate_expected_messages

# ################################################################################################################################
# ################################################################################################################################

_default_port_publish = PubSub.REST_Server.Default_Port_Publish

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ServerConfig:
    """ Server configuration parameters.
    """
    host: str = '127.0.0.1'
    port: int = _default_port_publish

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class CollectionConfig:
    """ Configuration for message collection.
    """
    users_yaml_path: str = ''
    messages_per_topic_per_user: int = 10
    log_interval: int = 100
    timeout_seconds: int = 300
    expected_message_count: int = 0  # This will be computed dynamically

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ReportConfig:
    """ Configuration for report generation.
    """
    url_path: str = '/report'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AppConfig:
    """ Overall application configuration.
    """
    server: ServerConfig
    collection: CollectionConfig
    report: ReportConfig

    def __post_init__(self) -> 'None':
        """ Initialize default configurations if none provided.
        """
        self.server = ServerConfig()
        self.collection = CollectionConfig()
        self.report = ReportConfig()

# ################################################################################################################################
# ################################################################################################################################

def load_config(config_file:'str') -> 'AppConfig':
    """ Load configuration from YAML file.
    """
    try:
        with open(config_file, 'r') as f:
            config_dict = yaml_load(f) or {}

        # Extract configuration sections
        server_dict = config_dict.get('server', {})
        collection_dict = config_dict.get('collection', {})
        report_dict = config_dict.get('report', {})

        # Create configuration objects
        server_config = ServerConfig(**server_dict)
        collection_config = CollectionConfig(**collection_dict)
        report_config = ReportConfig(**report_dict)

        # Calculate the expected message count dynamically if users_yaml_path is provided
        if collection_config.users_yaml_path:
            collection_config.expected_message_count = calculate_expected_messages(
                collection_config.users_yaml_path,
                collection_config.messages_per_topic_per_user
            )
            logger.info(f'Dynamically calculated expected message count: {collection_config.expected_message_count}')

        # Create and return the application config
        return AppConfig(
            server=server_config,
            collection=collection_config,
            report=report_config
        )

    except Exception as e:
        logger.error(f'Error loading configuration from {config_file}: {e}')
        # Return default configuration
        return AppConfig()

# ################################################################################################################################
# ################################################################################################################################
