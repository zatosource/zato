# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import PubSub
from zato.common.odb.model import PubSubPermission, SecurityBase, to_json
from zato.common.odb.query import pubsub_permission_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from sqlalchemy.orm.session import Session as SASession
    any_ = any_
    anydict = anydict
    stranydict = stranydict
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubPermissionImporter:
    """ Handles importing pub/sub permission definitions from YAML configuration files.
    """

    def __init__(self, importer:'any_') -> 'None':
        self.importer = importer
        self.pubsub_permission_defs = {}

# ################################################################################################################################

    def _process_pubsub_permission_defs(self, query_result:'any_', out:'dict') -> 'None':
        """ Process pub/sub permission definitions from database query result.
        """
        logger.info('Processing pub/sub permission definitions from database')

        items = list(query_result)
        search_result = items[0]
        items = search_result.result

        logger.info('Processing %d pub/sub permission definitions', len(search_result.result))

        for item in items:

            # Each item is a tuple: (PubSubPermission, security_name, subscription_count)
            permission_obj = item[0]  # First element is the PubSubPermission object
            security_name = item[1]   # Second element is the security name
            subscription_count = item[2]  # Third element is the subscription count

            if hasattr(permission_obj, '_asdict'):
                permission_obj = permission_obj._asdict()
                permission_obj = permission_obj['PubSubPermission']

            # Extract fields directly from the permission object
            permission_dict = {
                'id': permission_obj.id,
                'sec_base_id': permission_obj.sec_base_id,
                'pattern': permission_obj.pattern,
                'access_type': permission_obj.access_type,
                'is_active': permission_obj.is_active,
                'cluster_id': permission_obj.cluster_id
            }

            # Add additional fields from the query
            permission_dict['security_name'] = security_name
            permission_dict['subscription_count'] = subscription_count

            # Create a unique key for this permission
            key = f"{permission_dict['sec_base_id']}_{permission_dict['pattern']}_{permission_dict['access_type']}"
            logger.info('Processing pub/sub permission definition: %s (id=%s)', key, permission_dict.get('id'))
            out[key] = permission_dict

# ################################################################################################################################

    def get_pubsub_permission_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving pub/sub permission definitions from database for cluster_id=%s', cluster_id)
        permissions = pubsub_permission_list(session, cluster_id)

        self._process_pubsub_permission_defs(permissions, out)
        logger.info('Total pub/sub permission definitions from DB: %d', len(out))

        for key in out:
            logger.info('DB pub/sub permission def: key=%s', key)

        return out

# ################################################################################################################################

    def create_pubsub_permission_definition(self, definition:'stranydict', session:'SASession') -> 'PubSubPermission':
        """ Creates a new pub/sub permission definition in the database.
        """
        logger.info('Creating pub/sub permission definition: %s', definition)

        instance = PubSubPermission()
        instance.cluster_id = definition.get('cluster_id', 1)
        instance.sec_base_id = definition['sec_base_id']
        instance.pattern = definition['pattern']
        instance.access_type = definition['access_type']
        instance.is_active = definition.get('is_active', True)

        set_instance_opaque_attrs(instance, definition)
        session.add(instance)
        session.commit()

        return instance

# ################################################################################################################################

    def update_pubsub_permission_definition(self, definition:'stranydict', session:'SASession') -> 'PubSubPermission':
        """ Updates an existing pub/sub permission definition in the database.
        """
        logger.info('Updating pub/sub permission definition: %s', definition)

        instance = session.query(PubSubPermission).filter_by(id=definition['id']).one()
        instance.sec_base_id = definition['sec_base_id']
        instance.pattern = definition['pattern']
        instance.access_type = definition['access_type']
        instance.is_active = definition.get('is_active', True)

        set_instance_opaque_attrs(instance, definition)
        session.commit()

        return instance

# ################################################################################################################################

    def should_create_pubsub_permission_definition(self, yaml_def:'stranydict', db_defs:'anydict') -> 'bool':
        """ Determines if a pub/sub permission definition should be created.
        """
        key = f"{yaml_def['sec_base_id']}_{yaml_def['pattern']}_{yaml_def['access_type']}"
        return key not in db_defs

# ################################################################################################################################

    def should_update_pubsub_permission_definition(self, yaml_def:'stranydict', db_def:'stranydict') -> 'bool':
        """ Determines if a pub/sub permission definition should be updated by comparing YAML and DB definitions.
        """
        # Compare is_active
        yaml_is_active = yaml_def.get('is_active', True)
        db_is_active = db_def.get('is_active', True)
        if yaml_is_active != db_is_active:
            logger.info('is_active differs: YAML=%s, DB=%s', yaml_is_active, db_is_active)
            return True

        return False

# ################################################################################################################################

    def get_security_base_id_by_name(self, security_name:'str', session:'SASession') -> 'int':
        """ Gets the security base ID by name.
        """
        sec_base = session.query(SecurityBase).filter_by(name=security_name, cluster_id=self.importer.cluster_id).one()
        return sec_base.id

# ################################################################################################################################

    def sync_pubsub_permission_definitions(self, permission_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pub/sub permission definitions from YAML with the database.
        """
        logger.info('Processing %d pub/sub permission definitions from YAML', len(permission_list))

        # Get existing definitions from database
        db_defs = self.get_pubsub_permission_defs_from_db(session, self.importer.cluster_id)

        created = []
        updated = []

        for yaml_def in permission_list:
            security_name = yaml_def['security']
            logger.info('Processing YAML pub/sub permission definition for security: %s', security_name)

            # Get security base ID
            sec_base_id = self.get_security_base_id_by_name(security_name, session)

            # Process pub permissions
            for pattern in yaml_def.get('pub', []):
                permission_def = {
                    'sec_base_id': sec_base_id,
                    'pattern': pattern,
                    'access_type': PubSub.API_Client.Publisher,
                    'is_active': yaml_def.get('is_active', True),
                    'cluster_id': 1
                }

                key = f"{sec_base_id}_{pattern}_{PubSub.API_Client.Publisher}"

                if self.should_create_pubsub_permission_definition(permission_def, db_defs):
                    instance = self.create_pubsub_permission_definition(permission_def, session)
                    created.append(instance)
                    self.pubsub_permission_defs[key] = to_json(instance, return_as_dict=True)['fields']
                else:
                    permission_def['id'] = db_defs[key]['id']
                    if self.should_update_pubsub_permission_definition(permission_def, db_defs[key]):
                        instance = self.update_pubsub_permission_definition(permission_def, session)
                        updated.append(instance)
                        self.pubsub_permission_defs[key] = to_json(instance, return_as_dict=True)['fields']

            # Process sub permissions
            for pattern in yaml_def.get('sub', []):
                permission_def = {
                    'sec_base_id': sec_base_id,
                    'pattern': pattern,
                    'access_type': PubSub.API_Client.Subscriber,
                    'is_active': yaml_def.get('is_active', True),
                    'cluster_id': 1
                }

                key = f"{sec_base_id}_{pattern}_{PubSub.API_Client.Subscriber}"

                if self.should_create_pubsub_permission_definition(permission_def, db_defs):
                    instance = self.create_pubsub_permission_definition(permission_def, session)
                    created.append(instance)
                    self.pubsub_permission_defs[key] = to_json(instance, return_as_dict=True)['fields']
                else:
                    permission_def['id'] = db_defs[key]['id']
                    if self.should_update_pubsub_permission_definition(permission_def, db_defs[key]):
                        instance = self.update_pubsub_permission_definition(permission_def, session)
                        updated.append(instance)
                        self.pubsub_permission_defs[key] = to_json(instance, return_as_dict=True)['fields']

        logger.info('pub/sub permission definitions sync completed: created=%d, updated=%d', len(created), len(updated))
        return created, updated

# ################################################################################################################################
# ################################################################################################################################
