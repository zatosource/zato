# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path

# PyYAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

def main():
    # Get the path to the YAML config file using relative path
    current_dir = Path(__file__).parent
    config_path = current_dir / '..' / '..' / '..' / '..' / '..' / 'src' / 'zato' / 'common' / 'pubsub' / 'server' / 'config.yaml'
    config_path = config_path.resolve()

    # Read and parse the YAML file
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Process the configuration data
    print(f'Loaded configuration from: {config_path}')
    print(f'Security definitions: {len(config_data.get("security", []))}')
    print(f'Topics: {len(config_data.get("pubsub_topic", []))}')
    print(f'Permissions: {len(config_data.get("pubsub_permission", []))}')
    print(f'Subscriptions: {len(config_data.get("pubsub_subscription", []))}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
