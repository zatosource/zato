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
from zato.common.odb.model import Cluster, HTTPBasicAuth, APIKeySecurity, NTLM, to_json
from zato.common.odb.query import basic_auth_list, apikey_security_list, ntlm_list
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

    def _process_security_defs(self, query_result:'any_', sec_type:'str', out:'dict') -> 'None':
        """ Process security definitions from a query result and add them to the output dictionary.
        """
        # Get data from to_json - it will be a list of dictionaries
        definitions = to_json(query_result, return_as_dict=True)
        
        # Process each definition
        for item in definitions:
            
            # Store the type
            item['type'] = sec_type
            
            # Get the name - it's a required field so should always be present
            name = item['name']
            
            # Store in the dictionary using name as key
            out[name] = item
    
    def get_security_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        """ Retrieves all security definitions from the database.
        """
        # Query the database for all existing definitions
        out = {}
        
        # Process basic auth definitions
        basic_auth_defs = basic_auth_list(session, cluster_id, cluster_name=None, needs_columns=True)
        self._process_security_defs(basic_auth_defs, 'basic_auth', out)
        
        # Process API key definitions
        apikey_defs = apikey_security_list(session, cluster_id, True)
        self._process_security_defs(apikey_defs, 'apikey', out)
        
        # Process NTLM definitions
        ntlm_defs = ntlm_list(session, cluster_id, True)
        self._process_security_defs(ntlm_defs, 'ntlm', out)
        
        # Return the in-memory representation
        return out

# ################################################################################################################################

    def compare_security_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple[anylist, anylist]':
        """ Compares security definitions from YAML with database records.
        """
        to_create = []
        to_update = []

        # Process each definition from YAML
        for item in yaml_defs:
            name = item['name']

            # Skip if no name defined
            if not name:
                continue

            # Check if definition already exists in database
            db_def = db_defs.get(name)

            if not db_def:
                # Definition doesn't exist in DB, create it
                to_create.append(item)
            else:

                # Definition exists, check if update is needed
                needs_update = False

                # Compare all other attributes that are in YAML
                for key, value in item.items():

                    # We never compare these
                    if key in ('type', 'name', 'password'):
                        continue

                    # Compare with database value if exists
                    if key in db_def and value != db_def[key]:
                        needs_update = True
                        break

                if needs_update:
                    # Add database ID to YAML definition for update
                    item['id'] = db_def['id']
                    to_update.append(item)

        return to_create, to_update

# ################################################################################################################################

    def _create_basic_auth(self, security_def:'anydict', cluster:'any_') -> 'any_':
        """ Create a basic auth security definition.
        """
        # Create new instance
        auth = HTTPBasicAuth(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def.get('realm'),
            security_def['password'],
            cluster
        )
        
        # Set any opaque attributes
        set_instance_opaque_attrs(auth, security_def)
        
        return auth
    
    def _create_apikey(self, security_def:'anydict', cluster:'any_') -> 'any_':
        """ Create an API key security definition.
        """
        # Create new instance
        auth = APIKeySecurity(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def['password'],
            cluster
        )
        
        # Set header if provided
        if 'header' in security_def:
            auth.header = security_def['header']
            
        # Set any opaque attributes
        set_instance_opaque_attrs(auth, security_def)
        
        return auth
        
    def _create_ntlm(self, security_def:'anydict', cluster:'any_') -> 'any_':
        """ Create an NTLM security definition.
        """
        # Create new instance
        auth = NTLM(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def.get('password'),
            cluster
        )
        
        # Set any opaque attributes
        set_instance_opaque_attrs(auth, security_def)
        
        return auth
    
    def create_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        """ Creates a new security definition instance.
        """
        sec_type = security_def['type']

        # Get cluster by ID
        cluster = session.query(Cluster).filter_by(id=self.cluster_id).one()
        
        # Create instance based on security type
        if sec_type == 'basic_auth':
            auth = self._create_basic_auth(security_def, cluster)
        elif sec_type == 'apikey':
            auth = self._create_apikey(security_def, cluster)
        elif sec_type == 'ntlm':
            auth = self._create_ntlm(security_def, cluster)
        else:
            # Log warning for unsupported types
            logger.warning(f'Unsupported security type: {sec_type}')
            return None
            
        # Add to session
        session.add(auth)
        return auth

# ################################################################################################################################

    def _update_definition(self, definition:'any_', security_def:'anydict') -> 'any_':
        """ Update a security definition with values from YAML.
        """
        # Update fields - iterate through all attributes in the yaml definition
        for key, value in security_def.items():
            # Skip type, name and id attributes
            if key in ('type', 'name', 'id'):
                continue
                
            # Set attribute if it exists on the definition
            if hasattr(definition, key):
                setattr(definition, key, value)
            else:
                # Log a detailed warning about the invalid attribute
                def_type = security_def['type']
                def_name = security_def['name']
                logger.warning(f'Invalid attribute {key!r} for {def_type} security definition {def_name!r}')
        
        # Set any opaque attributes
        set_instance_opaque_attrs(definition, security_def)
        
        return definition
        
    def update_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        """ Updates an existing security definition instance.
        """
        sec_type = security_def['type']
        definition_id = security_def['id']

        # Find and update the definition based on security type
        if sec_type == 'basic_auth':
            definition = session.query(HTTPBasicAuth).filter_by(id=definition_id).one()
            self._update_definition(definition, security_def)
            
        elif sec_type == 'apikey':
            definition = session.query(APIKeySecurity).filter_by(id=definition_id).one()
            self._update_definition(definition, security_def)
            
        elif sec_type == 'ntlm':
            definition = session.query(NTLM).filter_by(id=definition_id).one()
            self._update_definition(definition, security_def)
            
        else:
            # Log warning for unsupported types
            logger.warning(f'Unsupported security type: {sec_type}')
            return None
        
        # Add to session
        session.add(definition)
        return definition

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

        out_created = []
        out_updated = []

        try:
            # Create new definitions
            for item in to_create:
                instance = self.create_security_definition(item, session)
                if instance:
                    out_created.append(instance)

                    # Get model data as a dictionary (will be a single-item list)
                    instance_dict = to_json(instance, return_as_dict=True)[0]

                    # Add the type information
                    instance_dict['type'] = item['type']

                    # Store in memory
                    self.sec_defs[instance.name] = instance_dict

            # Update existing definitions
            for item in to_update:
                instance = self.update_security_definition(item, session)
                if instance:
                    out_updated.append(instance)

            # Commit all changes
            session.commit()

        except Exception as e:
            logger.error(f'Error syncing security definitions: {e}')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
