# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.common.odb.model import Cluster, HTTPBasicAuth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, anytuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

class EnmasseYAMLImporter:
    """ Imports enmasse YAML configuration files and builds an in-memory representation.
    """
    def __init__(self) -> 'None':

        # This is always the same
        self.cluster_id = ModuleCtx.Cluster_ID

        self.sec_defs = {}
        self.objects = {}

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

    def create_security_definition(self, sec_def:'anydict', session:'SASession', cluster:'Cluster') -> 'any_':
        """ Creates a new security definition instance.
        """
        name = sec_def['name']
        sec_type = sec_def['type']

        if sec_type == 'basic_auth':
            instance = HTTPBasicAuth(
                None,
                name,
                sec_def.get('is_active', True),
                sec_def['username'],
                sec_def['realm'],
                sec_def['password'],
                cluster
            )

        # Add handlers for other security types

        session.add(instance) # type: ignore
        return instance # type: ignore

    def update_security_definition(self, existing:'any_', sec_def:'anydict') -> 'any_':
        """ Updates an existing security definition instance.
        """
        sec_type = sec_def['type']

        if sec_type == 'basic_auth':
            existing.is_active = sec_def.get('is_active', existing.is_active)
            existing.username = sec_def['username']
            existing.realm = sec_def['realm']

            if 'password' in sec_def:
                existing.password = sec_def['password']

        return existing

    def process_security_definitions(self, security_list:'anylist', session:'SASession', cluster:'Cluster') -> 'anytuple':
        """ Processes security definitions - creates new ones or updates existing.
        """
        created = []
        updated = []

        for sec_def in security_list:
            name = sec_def['name']
            sec_type = sec_def['type']

            # Find existing definition
            existing = None
            if sec_type == 'basic_auth':
                existing = session.query(HTTPBasicAuth).filter_by(name=name).first()
            # Add queries for other security types

            if existing:
                instance = self.update_security_definition(existing, sec_def)
                updated.append(instance)
            else:
                instance = self.create_security_definition(sec_def, session, cluster)
                created.append(instance)

        session.commit()
        return created, updated

# ################################################################################################################################
# ################################################################################################################################
