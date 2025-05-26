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
from zato.common.odb.model import Cluster, HTTPBasicAuth, to_json
from zato.common.odb.query import basic_auth_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, stranydict

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

    def get_security_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        """ Retrieves all security definitions from the database.
        """
        # Query the database for all existing definitions
        security_defs = {}

        # Get all basic auth definitions
        basic_auth_defs = basic_auth_list(session, cluster_id, None, True)

        # Convert to dictionary keyed by name
        for definition in basic_auth_defs:

            # Get all model attributes
            definition_dict = to_json(definition, return_as_dict=True)['fields']

            print()

            # Add the definition type and reference
            definition_dict['type'] = 'basic_auth'
            definition_dict['definition'] = definition

            # Store in the dictionary using name as key
            security_defs[definition.name] = definition_dict

        # Return the in-memory representation
        return security_defs

# ################################################################################################################################

    def compare_security_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple[anylist, anylist]':
        """ Compares security definitions from YAML with database records.
        """
        to_create = []
        to_update = []

        # Process each definition from YAML
        for yaml_def in yaml_defs:
            name = yaml_def['name']

            # Skip if no name defined
            if not name:
                continue

            # Check if definition already exists in database
            db_def = db_defs.get(name)

            if not db_def:
                # Definition doesn't exist in DB, create it
                to_create.append(yaml_def)
            else:

                # Definition exists, check if update is needed
                needs_update = False

                # Compare all other attributes that are in YAML
                for key, value in yaml_def.items():

                    # We never compare these
                    if key in ('type', 'name', 'password'):
                        continue

                    # Compare with database value if exists
                    if key in db_def and value != db_def[key]:
                        needs_update = True
                        break

                if needs_update:
                    # Add database ID to YAML definition for update
                    yaml_def['id'] = db_def['id']
                    to_update.append(yaml_def)

        return to_create, to_update

# ################################################################################################################################

    def create_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        """ Creates a new security definition instance.
        """
        name = security_def['name']
        sec_type = security_def['type']

        # Get cluster by ID
        cluster = session.query(Cluster).filter_by(id=self.cluster_id).one()

        if sec_type == 'basic_auth':
            # Create new instance
            auth = HTTPBasicAuth(
                None,
                name,
                security_def.get('is_active', True),
                security_def['username'],
                security_def.get('realm'),
                security_def['password'],
                cluster
            )

            # Set any opaque attributes
            set_instance_opaque_attrs(auth, security_def)

            # Add to session
            session.add(auth)
            return auth

        # Add handlers for other security types
        logger.warning(f'Unsupported security type: {sec_type}')
        return None

# ################################################################################################################################

    def update_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        """ Updates an existing security definition instance.
        """
        sec_type = security_def['type']

        if sec_type == 'basic_auth':
            # Find the definition
            definition = session.query(HTTPBasicAuth).filter_by(id=security_def['id']).one()

            # Update fields - iterate through all attributes in the yaml definition
            for key, value in security_def.items():
                # Skip type, name and id attributes
                if key in ('type', 'name', 'id'):
                    continue

                # Set attribute if it exists on the definition
                if hasattr(definition, key):
                    setattr(definition, key, value)

            # Set any opaque attributes
            set_instance_opaque_attrs(definition, security_def)

            # Add to session
            session.add(definition)
            return definition

        # Add handlers for other security types
        logger.warning(f'Unsupported security type: {sec_type}')
        return None

# ################################################################################################################################

    def sync_security_definitions(self, security_list:'anylist', session:'SASession') -> 'tuple[anylist, anylist]':
        """ Synchronizes security definitions between YAML and database.
        """
        # Filter only security definitions
        security_yaml_defs = [item for item in security_list if 'type' in item]

        # Get current definitions from database
        db_defs = self.get_security_defs_from_db(session, self.cluster_id)

        # Compare YAML definitions with database
        to_create, to_update = self.compare_security_defs(security_yaml_defs, db_defs)

        created = []
        updated = []

        try:
            # Create new definitions
            for security_def in to_create:
                instance = self.create_security_definition(security_def, session)
                if instance:
                    created.append(instance)

                    # Update in-memory representation with model data
                    instance_dict = to_json(instance, return_as_dict=True)['fields']
                    instance_dict['type'] = security_def['type']
                    instance_dict['definition'] = instance
                    self.sec_defs[instance.name] = instance_dict

            # Update existing definitions
            for security_def in to_update:
                _ = self.update_security_definition(security_def, session)

            # Commit all changes
            session.commit()

        except Exception as e:
            logger.error(f'Error syncing security definitions: {e}')
            session.rollback()
            raise

        return created, updated

# ################################################################################################################################
# ################################################################################################################################
