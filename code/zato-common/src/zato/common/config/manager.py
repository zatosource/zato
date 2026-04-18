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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# YAML sections whose items are keyed by 'id' rather than 'name'.
_key_by_id = frozenset(['pubsub_permission', 'pubsub_subscription'])

# YAML section aliases - the YAML file uses these names,
# .. but the internal store uses the target names.
_yaml_to_internal = {
    'cache':            'cache_builtin',
    'sql':              'outgoing_sql',
    'odoo':             'outgoing_odoo',
    'outconn_sql':      'outgoing_sql',
    'outconn_soap':     'outgoing_soap',
    'outgoing_ldap':    'generic_connection',
    'ldap':             'generic_connection',
    'confluence':       'generic_connection',
    'jira':             'generic_connection',
    'microsoft_365':    'generic_connection',
    'zato_generic_connection': 'generic_connection',
}

# For generic_connection sub-types, the default 'type_' to set.
_generic_connection_type_defaults = {
    'ldap':             'outconn-ldap',
    'outgoing_ldap':    'outconn-ldap',
    'confluence':       'cloud-confluence',
    'jira':             'cloud-jira',
    'microsoft_365':    'cloud-microsoft-365',
}

# All valid internal section names.
_all_sections = frozenset([
    'security',
    'groups',
    'channel_rest',
    'channel_soap',
    'channel_amqp',
    'channel_openapi',
    'outgoing_rest',
    'outgoing_soap',
    'outgoing_amqp',
    'outgoing_ftp',
    'outgoing_sql',
    'outgoing_odoo',
    'outgoing_sap',
    'cache_builtin',
    'email_smtp',
    'email_imap',
    'scheduler',
    'holiday_calendar',
    'generic_connection',
    'pubsub_topic',
    'pubsub_permission',
    'pubsub_subscription',
    'elastic_search',
    'service',
])

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
        for section in _all_sections:
            self._store[section] = {}

        # Paths of all YAML files loaded, in order.
        self._yaml_paths:'list[str]' = []

# ################################################################################################################################

    def _key_field(self, section:'str') -> 'str':
        if section in _key_by_id:
            return 'id'
        return 'name'

# ################################################################################################################################

    def _resolve_section(self, yaml_key:'str') -> 'str':
        return _yaml_to_internal.get(yaml_key, yaml_key)

# ################################################################################################################################

    def _apply_yaml_data(self, data:'anydict') -> 'None':
        """ Merge parsed YAML data into the in-memory store.
        Must be called under self.lock.
        """
        for yaml_key, items in data.items():
            if not isinstance(items, list):
                continue

            section = self._resolve_section(yaml_key)
            if section not in _all_sections:
                logger.warning('Ignoring unknown YAML section: %s', yaml_key)
                continue

            key_field = self._key_field(section)
            store = self._store[section]
            default_type = _generic_connection_type_defaults.get(yaml_key, '')

            for item in items:
                if not isinstance(item, dict):
                    continue

                if default_type:
                    item.setdefault('type_', default_type)

                key = item.get(key_field, '')
                if not key:
                    logger.warning('Skipping item without %s in section %s', key_field, section)
                    continue

                store[key] = item

# ################################################################################################################################

    def load_yaml(self, path:'str') -> 'None':
        """ Load a YAML file from disk and merge into the in-memory store.
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
        """ Parse a YAML string and merge into the in-memory store.
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
        """ Return a dict copy of all runtime objects.
        """
        with self.lock:
            return deepcopy(self._store)

# ################################################################################################################################
# ################################################################################################################################
