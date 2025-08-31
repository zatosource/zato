# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import copy
import logging
import os

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

        self.current_dir = os.path.dirname(__file__)

        self.server_config_dir = os.path.join(self.current_dir, '..', '..', '..', '..', '..', 'src', 'zato', 'common', 'pubsub', 'server')

        self.config_path = os.path.join(self.server_config_dir, 'config.yaml')
        self.config_path = os.path.abspath(self.config_path)

        self.multi_config_path = os.path.join(self.server_config_dir, 'config.multi.yaml')
        self.multi_config_path = os.path.abspath(self.multi_config_path)

# ################################################################################################################################

    def _add_users_topics_and_subscriptions(self, config_data:'strdict', users:'int', topics_multiplier:'float') -> 'strdict':

        new_config = copy.deepcopy(config_data)

        # Get existing security definitions to determine how many users we already have
        existing_security = new_config.get('security', [])
        existing_users_count = len(existing_security)
        users_to_add = users - existing_users_count

        # Add topics based on multiplier
        total_topics_needed = round(users * topics_multiplier)
        existing_topics = new_config.get('pubsub_topic', [])
        existing_topic_count = len(existing_topics)
        topics_to_add = total_topics_needed - existing_topic_count

        if topics_to_add > 0:
            for topic_idx in range(topics_to_add):
                topic_num = existing_topic_count + topic_idx + 1
                topic_name = f'demo.{topic_num}'
                topic_def = {
                    'name': topic_name,
                    'description': f'Generated topic {topic_num}'
                }
                new_config.setdefault('pubsub_topic', []).append(topic_def)

        # Extract all topic names for subscriptions
        topics = []
        all_topics = new_config.get('pubsub_topic', [])
        for topic in all_topics:
            topics.append(topic['name'])

        if users_to_add > 0:

            # Create new users, permissions, and subscriptions
            for idx in range(users_to_add):

                # Calculate user number (1-based indexing)
                user_num = existing_users_count + idx
                user_num += 1

                # Generate names for this user
                sec_name = f'demo_sec_def.{user_num}'
                username = f'user.{user_num}'
                password = f'password.{user_num}'

                # Add security definition
                security_def = {
                    'name': sec_name,
                    'type': 'basic_auth',
                    'username': username,
                    'password': password
                }
                new_config.setdefault('security', []).append(security_def)

                # Add permissions for this user
                permission = {
                    'security': sec_name,
                    'pub': ['demo.*', 'orders.*'],
                    'sub': ['demo.*', 'orders.*']
                }
                new_config.setdefault('pubsub_permission', []).append(permission)

                # Add subscription for this user to all existing topics
                subscription = {
                    'security': sec_name,
                    'delivery_type': 'pull',
                    'topic_list': topics
                }
                new_config.setdefault('pubsub_subscription', []).append(subscription)

        return new_config

# ################################################################################################################################

    def load_config(self) -> 'strdict':
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

# ################################################################################################################################

    def create_multi_config(self, modified_config:'strdict') -> 'None':
        with open(self.multi_config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(modified_config, f, default_flow_style=False, allow_unicode=True)

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

    def generate(self, users:'int', topics_multiplier:'float') -> 'None':
        config_data = self.load_config()
        modified_config = self._add_users_topics_and_subscriptions(config_data, users, topics_multiplier)
        self.create_multi_config(modified_config)
        self.log_config_info(modified_config, users)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate enmasse configuration')
    _ = parser.add_argument('--users', type=int, default=1, help='Number of users (default: 1)')
    _ = parser.add_argument('--topics-multiplier', type=float, default=10.0, help='Topics multiplier (default: 10.0)')
    args = parser.parse_args()
    generator = EnmasseGenerator()
    generator.generate(args.users, args.topics_multiplier)

# ################################################################################################################################
# ################################################################################################################################
