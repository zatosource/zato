# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import logging
from pathlib import Path

# PyYAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

def main(users: 'int') -> 'None':
    # Get the path to the YAML config file using relative path
    current_dir = Path(__file__).parent
    config_path = current_dir / '..' / '..' / '..' / '..' / '..' / 'src' / 'zato' / 'common' / 'pubsub' / 'server' / 'config.yaml'
    config_path = config_path.resolve()

    # Read and parse the YAML file
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Process the configuration data
    logger.info(f'Loaded configuration from: {config_path}')
    logger.info(f'Users: {users}')
    logger.info(f'Security definitions: {len(config_data.get("security", []))}')
    logger.info(f'Topics: {len(config_data.get("pubsub_topic", []))}')
    logger.info(f'Permissions: {len(config_data.get("pubsub_permission", []))}')
    logger.info(f'Subscriptions: {len(config_data.get("pubsub_subscription", []))}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate enmasse configuration')
    _ = parser.add_argument('--users', type=int, default=1, help='Number of users (default: 1)')
    args = parser.parse_args()
    main(args.users)

# ################################################################################################################################
# ################################################################################################################################
