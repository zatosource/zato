# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import PubSubTopic, to_json
from zato.common.odb.query import pubsub_topic_list
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

class PubSubTopicImporter:
    """ Handles importing pubsub topic definitions from YAML configuration files.
    """

    def __init__(self, importer:'any_') -> 'None':
        self.importer = importer
        self.pubsub_topic_defs = {}

# ################################################################################################################################

    def _process_pubsub_topic_defs(self, query_result:'any_', out:'dict') -> 'None':

        search_results = query_result[0]
        items = search_results.result

        logger.info('Processing %d pubsub topic definitions', len(items))

        for item in items:

            # Each item is a tuple: (PubSubTopic, publisher_count, subscriber_count)
            topic_obj = item[0]  # First element is the PubSubTopic object
            topic_json = to_json(topic_obj, return_as_dict=True)
            topic_dict = topic_json['fields']  # Extract the fields dictionary

            name = topic_dict['name']
            logger.info('Processing pubsub topic definition: %s (id=%s)', name, topic_dict.get('id'))
            out[name] = topic_dict

# ################################################################################################################################

    def get_pubsub_topic_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving pubsub topic definitions from database for cluster_id=%s', cluster_id)
        topics = pubsub_topic_list(session, cluster_id)

        self._process_pubsub_topic_defs(topics, out)
        logger.info('Total pubsub topic definitions from DB: %d', len(out))

        for name in out:
            logger.info('DB pubsub topic def: name=%s', name)

        return out

# ################################################################################################################################

    def create_pubsub_topic_definition(self, definition:'stranydict', session:'SASession') -> 'PubSubTopic':
        """ Creates a new pubsub topic definition in the database.
        """
        logger.info('Creating pubsub topic definition: %s', {k: v for k, v in definition.items() if k != 'password'})

        instance = PubSubTopic()
        instance.cluster_id = self.importer.cluster_id
        instance.name = definition['name']
        instance.description = definition.get('description', '')
        instance.is_active = definition.get('is_active', True)

        set_instance_opaque_attrs(instance, definition)
        session.add(instance)
        session.commit()

        return instance

# ################################################################################################################################

    def update_pubsub_topic_definition(self, definition:'stranydict', session:'SASession') -> 'PubSubTopic':
        """ Updates an existing pubsub topic definition in the database.
        """
        logger.info('Updating pubsub topic definition: name=%s id=%s', definition['name'], definition['id'])

        instance = session.query(PubSubTopic).filter_by(id=definition['id']).one()
        instance.name = definition['name']
        instance.description = definition.get('description', '')
        instance.is_active = definition.get('is_active', True)

        set_instance_opaque_attrs(instance, definition)
        session.commit()

        return instance

# ################################################################################################################################

    def should_create_pubsub_topic_definition(self, yaml_def:'stranydict', db_defs:'anydict') -> 'bool':
        """ Determines if a pubsub topic definition should be created.
        """
        name = yaml_def['name']
        return name not in db_defs

# ################################################################################################################################

    def should_update_pubsub_topic_definition(self, yaml_def:'stranydict', db_def:'stranydict') -> 'bool':
        """ Determines if a pubsub topic definition should be updated by comparing YAML and DB definitions.
        """
        # Compare description
        yaml_description = yaml_def.get('description', '')
        db_description = db_def.get('description', '')
        if yaml_description != db_description:
            logger.info('Description differs: YAML=%s, DB=%s', yaml_description, db_description)
            return True

        # Compare is_active
        yaml_is_active = yaml_def.get('is_active', True)
        db_is_active = db_def.get('is_active', True)
        if yaml_is_active != db_is_active:
            logger.info('is_active differs: YAML=%s, DB=%s', yaml_is_active, db_is_active)
            return True

        return False

# ################################################################################################################################

    def sync_pubsub_topic_definitions(self, topic_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub topic definitions from YAML with the database.
        """
        logger.info('Processing %d pubsub topic definitions from YAML', len(topic_list))

        # Get existing definitions from database
        db_defs = self.get_pubsub_topic_defs_from_db(session, self.importer.cluster_id)

        created = []
        updated = []

        for yaml_def in topic_list:
            name = yaml_def['name']
            logger.info('Processing YAML pubsub topic definition: %s', name)

            if self.should_create_pubsub_topic_definition(yaml_def, db_defs):

                # Create new definition
                instance = self.create_pubsub_topic_definition(yaml_def, session)
                created.append(instance)

                # Add to our tracking dictionary
                self.pubsub_topic_defs[name] = to_json(instance, return_as_dict=True)['fields']
            else:

                # Update existing definition
                yaml_def['id'] = db_defs[name]['id']  # Add the ID for update
                instance = self.update_pubsub_topic_definition(yaml_def, session)
                updated.append(instance)

                # Update our tracking dictionary
                self.pubsub_topic_defs[name] = to_json(instance, return_as_dict=True)['fields']

        logger.info('Pubsub topic definitions sync completed: created=%d, updated=%d', len(created), len(updated))
        return created, updated

# ################################################################################################################################
# ################################################################################################################################
