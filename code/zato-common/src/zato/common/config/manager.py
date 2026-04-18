# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from copy import deepcopy
from threading import RLock

# PyYAML
import yaml

# Zato
from zato.common.config.constants import All_Sections, Key_By_Security

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ConfigManager:
    """ Manages server configuration backed by YAML files on disk.
    Accessible as self.server.config on ParallelServer.
    """

    def __init__(self) -> 'None':

        self.lock = RLock()

        # section_name -> {key -> dict},
        # populated by load_yaml / load_yaml_string.
        self._store:'dict[str, dict[str, anydict]]' = {}
        for section in All_Sections:
            self._store[section] = {}

        # Paths of all YAML files loaded, in order.
        self._yaml_paths:'list[str]' = []

# ################################################################################################################################

    def _key_field(self, section:'str') -> 'str':
        if section in Key_By_Security:
            return 'security'
        return 'name'

# ################################################################################################################################

    def _apply_yaml_data(self, data:'anydict') -> 'None':
        """ Merge parsed YAML data into the store.
        Must be called under self.lock.
        """
        for section, items in data.items():
            if not isinstance(items, list):
                continue

            if section not in All_Sections:
                logger.warning('Ignoring unknown YAML section: %s', section)
                continue

            key_field = self._key_field(section)
            section_store = self._store[section]

            for item in items:
                if not isinstance(item, dict):
                    continue

                key = str(item.get(key_field, ''))
                if not key:
                    logger.warning('Skipping item without %s in section %s', key_field, section)
                    continue

                section_store[key] = item

# ################################################################################################################################

    def load_yaml(self, path:'str') -> 'None':
        """ Load a YAML file from disk and merge into the store.
        """
        with self.lock:
            expanded_path = os.path.expandvars(path)
            contents = open(expanded_path, 'r').read()
            data = yaml.safe_load(contents)
            if data and isinstance(data, dict):
                self._apply_yaml_data(data)
            self._yaml_paths.append(expanded_path)

# ################################################################################################################################

    def load_yaml_string(self, yaml_string:'str') -> 'None':
        """ Parse a YAML string and merge into the store.
        """
        with self.lock:
            expanded = os.path.expandvars(yaml_string)
            data = yaml.safe_load(expanded)
            if data and isinstance(data, dict):
                self._apply_yaml_data(data)

# ################################################################################################################################

    def get(self, section:'str', name:'str') -> 'anydictnone':
        """ Return a copy of a single item, or None if not found.
        """
        with self.lock:
            section_store = self._store[section]
            item = section_store.get(name)
            if item is None:
                return None
            return deepcopy(item)

# ################################################################################################################################

    def get_list(self, section:'str') -> 'anylist':
        """ Return copies of all items in a section.
        """
        with self.lock:
            section_store = self._store[section]
            return [deepcopy(item) for item in section_store.values()]

# ################################################################################################################################

    def set(self, section:'str', name:'str', data:'anydict') -> 'None':
        """ Upsert an item in a section.
        """
        with self.lock:
            section_store = self._store[section]
            section_store[name] = deepcopy(data)

# ################################################################################################################################

    def delete(self, section:'str', name:'str') -> 'bool':
        """ Remove an item from a section. Returns True if it existed.
        """
        with self.lock:
            section_store = self._store[section]
            if name in section_store:
                del section_store[name]
                return True
            return False

# ################################################################################################################################

    def attr_value_exists(self, section:'str', attr_name:'str', value:'str') -> 'bool':
        """ Check if any item in a section has attr_name equal to value.
        """
        with self.lock:
            section_store = self._store[section]
            for item in section_store.values():
                if item.get(attr_name) == value:
                    return True
            return False

# ################################################################################################################################

    def export_to_dict(self) -> 'anydict':
        """ Return all runtime objects as {section: [list of items]}.
        """
        with self.lock:
            out:'anydict' = {}
            for section, section_store in self._store.items():
                if section_store:
                    out[section] = [deepcopy(item) for item in section_store.values()]
            return out

# ################################################################################################################################
# ################################################################################################################################
