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

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class EnmasseGenerator:

    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.server_config_dir = self.current_dir / '..' / '..' / '..' / '..' / '..' / 'src' / 'zato' / 'common' / 'pubsub' / 'server'
        self.config_path = (self.server_config_dir / 'config.yaml').resolve()
        self.multi_config_path = (self.server_config_dir / 'config.multi.yaml').resolve()

# ################################################################################################################################

    def load_config(self) -> 'strdict':
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

# ################################################################################################################################

    def create_multi_config(self, config_data:'strdict') -> 'None':
        with open(self.multi_config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, allow_unicode=True)

# ################################################################################################################################

    def log_config_info(self, config_data:'strdict', users:'int') -> 'None':
        logger.info(f'Loaded configuration from: {self.config_path}')
        logger.info(f'Created copy at: {self.multi_config_path}')
        logger.info(f'Users: {users}')
        logger.info(f'Security definitions: {len(config_data.get("security", []))}')
        logger.info(f'Topics: {len(config_data.get("pubsub_topic", []))}')
        logger.info(f'Permissions: {len(config_data.get("pubsub_permission", []))}')
        logger.info(f'Subscriptions: {len(config_data.get("pubsub_subscription", []))}')

# ################################################################################################################################

    def generate(self, users:'int') -> 'None':
        config_data = self.load_config()
        self.create_multi_config(config_data)
        self.log_config_info(config_data, users)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate enmasse configuration')
    _ = parser.add_argument('--users', type=int, default=1, help='Number of users (default: 1)')
    args = parser.parse_args()
    generator = EnmasseGenerator()
    generator.generate(args.users)

# ################################################################################################################################
# ################################################################################################################################
