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
from zato.common.odb.model import Cluster, HTTPBasicAuth, APIKeySecurity, NTLM, OAuth, HTTPSOAP, Service, to_json
from zato.common.odb.query import basic_auth_list, apikey_security_list, ntlm_list, oauth_list
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
        self.cluster = None
        
# ################################################################################################################################

    def get_cluster(self, session:'SASession') -> 'any_':
        """ Returns the cluster instance, retrieving it from the database if needed.
        """
        if not self.cluster:
            logger.info('Getting cluster by id=%s', self.cluster_id)
            self.cluster = session.query(Cluster).filter_by(id=self.cluster_id).one()
        return self.cluster

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
        logger.info('Processing %d %s definitions', len(definitions), sec_type)

        # Process each definition
        for item in definitions:

            # Store the type
            item['type'] = sec_type

            # Get the name - it's a required field so should always be present
            name = item['name']
            logger.info('Processing security definition: %s (type=%s, id=%s)', name, sec_type, item.get('id'))

            # Store in the dictionary using name as key
            out[name] = item

# ################################################################################################################################

    def get_security_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        """ Retrieves all security definitions from the database.
        """
        out = {}
        logger.info('Retrieving security definitions from database for cluster_id=%s', cluster_id)

        # Get basic auth definitions
        basic_auth = basic_auth_list(session, cluster_id)
        logger.info('Getting basic_auth definitions')
        self._process_security_defs(basic_auth, 'basic_auth', out)

        # Get API key definitions
        apikey = apikey_security_list(session, cluster_id)
        logger.info('Getting apikey definitions')
        self._process_security_defs(apikey, 'apikey', out)

        # Get NTLM definitions
        ntlm = ntlm_list(session, cluster_id)
        logger.info('Getting ntlm definitions')
        self._process_security_defs(ntlm, 'ntlm', out)

        # Get OAuth definitions
        oauth = oauth_list(session, cluster_id)
        # Convert to JSON to inspect the raw results
        oauth_json = to_json(oauth)
        logger.info('Getting oauth/bearer_token definitions: %s', oauth_json)
        self._process_security_defs(oauth, 'bearer_token', out)

        logger.info('Total security definitions from DB: %d', len(out))
        for name, details in out.items():
            logger.info('DB security def: name=%s type=%s', name, details.get('type'))

        return out

# ################################################################################################################################

    def compare_security_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple[anylist, anylist]':
        """ Compares security definitions from YAML with database records.
        """
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML defs with %d DB defs', len(yaml_defs), len(db_defs))

        # Log all database definitions keys for debugging
        logger.info('DB definition keys: %s', list(db_defs.keys()))

        # Process each definition from YAML
        for item in yaml_defs:
            name = item['name']
            sec_type = item['type']

            logger.info('Checking YAML def: name=%s type=%s', name, sec_type)

            # Skip if no name defined
            if not name:
                logger.warning('Skipping unnamed security definition')
                continue

            # Get definition from the database, if it exists
            db_def = db_defs.get(name)

            if not db_def:
                # Definition doesn't exist in DB, create it
                logger.info('Definition %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Definition %s exists in DB with id=%s type=%s', name, db_def.get('id'), db_def.get('type'))

                # Definition exists, check if update is needed
                needs_update = False

                # Compare all other attributes that are in YAML
                for key, value in item.items():

                    # We never compare these
                    if key in ('type', 'name', 'password'):
                        continue

                    # If the values are different, an update is needed
                    if key in db_def and db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                if needs_update:
                    # Add database ID to YAML definition for update
                    item['id'] = db_def['id']
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))
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

    def _create_bearer_token(self, security_def:'anydict', cluster:'any_') -> 'any_':
        """ Create a Bearer Token (OAuth) security definition.
        """
        # Create new instance (OAuth class is used for bearer_token)
        auth = OAuth(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def.get('password'),
            'not-used',    # proto_version
            'not-used',    # sig_method
            0,             # max_nonce_log
            cluster
        )

        # Set any additional opaque attributes
        set_instance_opaque_attrs(auth, security_def)

        return auth

    def create_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        """ Creates a new security definition instance.
        """
        sec_type = security_def['type']
        def_name = security_def.get('name', 'unnamed')

        logger.info('Creating security definition: name=%s type=%s', def_name, sec_type)
        
        # Get the cluster instance
        self.get_cluster(session)

        # Create instance based on security type
        if sec_type == 'basic_auth':
            auth = self._create_basic_auth(security_def, self.cluster)
        elif sec_type == 'apikey':
            auth = self._create_apikey(security_def, self.cluster)
        elif sec_type == 'ntlm':
            auth = self._create_ntlm(security_def, self.cluster)
        elif sec_type == 'bearer_token':
            auth = self._create_bearer_token(security_def, self.cluster)
        else:
            # Log warning for unsupported types
            logger.warning('Unsupported security type: %s', sec_type)
            return None

        logger.info('Created new security definition: %s (type=%s)', def_name, sec_type)
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

    def get_class_by_type(self, sec_type):
        """ Get the appropriate class for the security type.
        """
        class_map = {
            'basic_auth': HTTPBasicAuth,
            'apikey': APIKeySecurity,
            'ntlm': NTLM,
            'bearer_token': OAuth
        }
        return class_map[sec_type]

    def update_security_definition(self, sec_def:'anydict', session:'SASession', db_defs:'anydict') -> 'any_':
        """ Updates an existing security definition instance.
        """
        # Get basic info from the security definition
        sec_type = sec_def['type']
        def_id = sec_def['id']
        def_name = sec_def['name']

        # Get the security class for this type
        model = self.get_class_by_type(sec_type)

        # Object db_def will definitely exist since we got here from compare_security_defs
        # Use it to fill in any missing values before updating the database object
        db_def = db_defs[def_name]
        for item in db_def:
            if item not in sec_def and item not in ('id', 'type', 'definition'):
                sec_def[item] = db_def[item]

        # Query the database for the definition
        definition = session.query(model).filter_by(id=def_id).one()

        # Update the definition with values from security_def
        self._update_definition(definition, sec_def)

        # Add to session
        session.add(definition)
        return definition

# ################################################################################################################################

    def sync_security_definitions(self, security_list:'anylist', session:'SASession') -> 'tuple[anylist, anylist]':
        """ Synchronizes security definitions between YAML and database.
        """

        # Filter only security definitions
        security_yaml_defs = [item for item in security_list if 'type' in item]
        logger.info('Processing %d security definitions from YAML', len(security_yaml_defs))

        # Get current definitions from database
        db_defs = self.get_security_defs_from_db(session, self.cluster_id)

        # Compare YAML definitions with database
        to_create, to_update = self.compare_security_defs(security_yaml_defs, db_defs)

        out_created = []
        out_updated = []

        try:
            # Create new definitions
            logger.info('Creating %d new security definitions', len(to_create))
            for item in to_create:
                logger.info('Creating security definition: name=%s type=%s', item.get('name'), item.get('type'))
                instance = self.create_security_definition(item, session)
                if instance:
                    logger.info('Created security definition: name=%s id=%s', instance.name, getattr(instance, 'id', None))
                    out_created.append(instance)

                    # Get model data as a dictionary (will be a single-item list)
                    instance_dict = to_json(instance, return_as_dict=True)

                    # Add the type information
                    instance_dict['type'] = item['type']

                    # Store in memory
                    self.sec_defs[instance.name] = instance_dict

            # Update existing definitions
            logger.info('Updating %d existing security definitions', len(to_update))
            for item in to_update:
                logger.info('Updating security definition: name=%s id=%s', item.get('name'), item.get('id'))
                instance = self.update_security_definition(item, session, db_defs)
                if instance:
                    logger.info('Updated security definition: name=%s id=%s', instance.name, getattr(instance, 'id', None))
                    out_updated.append(instance)

            # Commit all changes
            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing security definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################

    def get_rest_channels_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        """ Retrieves all REST channels from the database.
        """
        out = {}
        logger.info('Retrieving REST channels from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP).filter(HTTPSOAP.cluster_id==cluster_id).filter(HTTPSOAP.connection=='channel').filter(HTTPSOAP.transport=='plain_http') # type: ignore
        channels = to_json(query, return_as_dict=True)
        logger.info('Processing %d REST channels', len(channels))

        for item in channels:
            item = item['fields']
            name = item['name']
            logger.info('Processing channel: %s (id=%s)', name, item['id'])
            out[name] = item

        return out

# ################################################################################################################################

    def compare_channel_rest(self, yaml_defs:'anylist', db_defs:'anydict') -> 'tuple[anylist, anylist]':
        """ Compares channel_rest definitions from YAML with database records.
        """
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML channels with %d DB channels', len(yaml_defs), len(db_defs))

        for item in yaml_defs:
            name = item['name']
            logger.info('Checking YAML channel: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Channel %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Channel %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                for key, value in item.items():
                    if key in db_def and db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                if needs_update:
                    item['id'] = db_def['id']
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))
        return to_create, to_update

# ################################################################################################################################

    def create_channel_rest(self, channel_def:'anydict', session:'SASession') -> 'any_':
        """ Creates a new REST channel.
        """
        name = channel_def['name']
        url_path = channel_def['url_path']
        service_name = channel_def['service']

        logger.info('Creating channel: name=%s url_path=%s service=%s', name, url_path, service_name)

        # Get service by name
        service = session.query(Service).filter_by(name=service_name, cluster_id=self.cluster_id).first()
        if not service:
            msg = f'Service not found {service_name} -> REST channel {name}'
            raise Exception(msg)

        channel = HTTPSOAP()
        channel.name = name
        channel.connection = 'channel'
        channel.transport = 'plain_http'
        channel.url_path = url_path
        channel.service = service
        channel.cluster = self.get_cluster(session)
        channel.is_active = True
        channel.is_internal = False
        channel.soap_action = 'not-used'

        # Set all other attributes directly from YAML definition
        for key, value in channel_def.items():
            if key not in ['service', 'security']:
                setattr(channel, key, value)

        # Set security if provided - direct assignment to security_id
        if 'security' in channel_def:
            security_name = channel_def['security']
            if security_name not in self.sec_defs:
                raise Exception(f'Security definition "{security_name}" not found for REST channel "{name}"')

            sec_def = self.sec_defs[security_name]
            channel.security_id = sec_def['id']

        # Add to session
        session.add(channel)
        return channel

# ################################################################################################################################

    def update_channel_rest(self, channel_def:'anydict', session:'SASession') -> 'any_':
        """ Updates an existing REST channel.
        """
        channel_id = channel_def['id']

        # Query the database for the channel
        channel = session.query(HTTPSOAP).filter_by(id=channel_id).one()

        # Update required attributes
        channel.url_path = channel_def['url_path']

        # Get service by name
        service_name = channel_def['service']
        service = session.query(Service).filter_by(name=service_name, cluster_id=self.cluster_id).first()
        if not service:
            raise Exception(f'Service not found: {service_name}')
        channel.service = service

        # Set all other attributes directly from YAML definition
        for key, value in channel_def.items():
            if key not in ['id', 'service', 'security']:
                setattr(channel, key, value)

        # Update security if provided - direct assignment to security_id
        if 'security' in channel_def:
            security_name = channel_def['security']
            if security_name not in self.sec_defs:
                raise Exception(f'Security definition "{security_name}" not found for REST channel "{channel_def["name"]}"')

            sec_def = self.sec_defs[security_name]
            channel.security_id = sec_def['id']

        # Add to session
        session.add(channel)
        return channel

# ################################################################################################################################

    def sync_channel_rest(self, channel_list:'anylist', session:'SASession') -> 'tuple[anylist, anylist]':
        """ Synchronizes REST channels between YAML and database.
        """
        logger.info('Processing %d REST channels from YAML', len(channel_list))

        db_channels = self.get_rest_channels_from_db(session, self.cluster_id)
        to_create, to_update = self.compare_channel_rest(channel_list, db_channels)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new REST channels', len(to_create))
            for item in to_create:
                logger.info('Creating channel: name=%s', item['name'])
                instance = self.create_channel_rest(item, session)
                logger.info('Created channel: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

            logger.info('Updating %d existing REST channels', len(to_update))
            for item in to_update:
                logger.info('Updating channel: name=%s id=%s', item['name'], item['id'])
                instance = self.update_channel_rest(item, session)
                logger.info('Updated channel: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing REST channels: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################

    def sync_from_yaml(self, yaml_config:'stranydict', session:'SASession') -> 'None':
        """ Synchronizes all objects from a YAML configuration with the database.
            This is the main entry point for processing a complete YAML file.
        """
        logger.info('Starting synchronization of YAML configuration')

        # First process security definitions
        security_list = yaml_config.get('security', [])
        if security_list:
            logger.info('Processing %d security definitions', len(security_list))
            security_created, security_updated = self.sync_security_definitions(security_list, session)
            logger.info('Processed security definitions: created=%d updated=%d', len(security_created), len(security_updated))

        # Then process REST channels which may depend on security definitions
        channel_list = yaml_config.get('channel_rest', [])
        if channel_list:
            logger.info('Processing %d REST channels', len(channel_list))
            channels_created, channels_updated = self.sync_channel_rest(channel_list, session)
            logger.info('Processed REST channels: created=%d updated=%d', len(channels_created), len(channels_updated))

        logger.info('YAML synchronization completed')

# ################################################################################################################################
# ################################################################################################################################
