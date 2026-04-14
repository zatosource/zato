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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseYAMLImporter:
    """ Parses enmasse YAML configuration files.
    """
    def __init__(self) -> 'None':
        pass

# ################################################################################################################################

    def from_path(self, path:'str') -> 'stranydict':
        if not os.path.exists(path):
            raise ValueError(f'Path does not exist -> {path}')

        path = os.path.abspath(path)
        base_dir = os.path.dirname(path)

        with open(path, 'r') as f:
            yaml_content = f.read()

        config = yaml.safe_load(yaml_content)

        if 'include' in config:
            config = self._process_includes(config, base_dir)

        return self._process_config(config)

# ################################################################################################################################

    def from_string(self, yaml_string:'str') -> 'stranydict':
        config = yaml.safe_load(yaml_string)
        return self._process_config(config)

# ################################################################################################################################

    def _process_includes(self, config:'stranydict', base_dir:'str', processed_paths:'set | None'=None) -> 'stranydict':

        if processed_paths is None:
            processed_paths = set()

        include_files = config.get('include', [])
        if not include_files:
            return config

        merged_config = {key: value for key, value in config.items() if key != 'include'}

        for include_path in include_files:

            if os.path.isabs(include_path):
                resolved_path = include_path
            else:
                resolved_path = os.path.normpath(os.path.join(base_dir, include_path))

            if not os.path.exists(resolved_path):
                raise ValueError(f'Included file does not exist -> {resolved_path}')

            if resolved_path in processed_paths:
                raise ValueError(f'Circular include detected -> {resolved_path}')

            processed_paths.add(resolved_path)

            with open(resolved_path, 'r') as f:
                include_content = f.read()

            include_config = yaml.safe_load(include_content)

            include_dir = os.path.dirname(resolved_path)

            if 'include' in include_config:
                include_config = self._process_includes(include_config, include_dir, processed_paths)

            self._merge_configs(merged_config, include_config)

        return merged_config

# ################################################################################################################################

    def _merge_configs(self, target:'stranydict', source:'stranydict') -> 'None':

        for key, items in source.items():

            if not items:
                continue

            if key not in target:
                target[key] = []

            target[key].extend(items)

# ################################################################################################################################

    def _process_config(self, config:'stranydict') -> 'stranydict':
        result = {}

        for key, items in config.items():
            if not items:
                continue

            if key not in result:
                result[key] = []

            result[key].extend(items)

        return result

# ################################################################################################################################
# ################################################################################################################################
