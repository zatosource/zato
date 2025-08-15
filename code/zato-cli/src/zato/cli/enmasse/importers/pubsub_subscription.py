# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import PubSub
from zato.common.odb.model import PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase, HTTPSOAP
from zato.common.util.api import new_sub_key
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

class PubSubSubscriptionImporter:
    """ Handles importing pubsub subscription definitions from YAML configuration files.
    """

    def __init__(self, importer:'any_') -> 'None':
        self.importer = importer
        self.pubsub_subscription_defs = {}

# ################################################################################################################################

    def _process_pubsub_subscription_defs(self, query_result:'any_', out:'dict') -> 'None':

        search_results = query_result[0]
        items = search_results.result

        logger.info('Processing %d pubsub subscription definitions', len(items))

        for item in items:

            subscription_dict = {
                'id': item.id,
                'sub_key': item.sub_key,
                'sec_base_id': item.sec_base_id,
                'delivery_type': item.delivery_type,
                'push_type': item.push_type,
                'rest_push_endpoint_id': item.rest_push_endpoint_id,
                'push_service_name': item.push_service_name,
                'is_active': item.is_active,
                'cluster_id': 1
            }

            sub_key = subscription_dict['sub_key']
            logger.info('Processing pubsub subscription definition: %s (id=%s)', sub_key, subscription_dict.get('id'))
            out[sub_key] = subscription_dict

# ################################################################################################################################

    def get_pubsub_subscription_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}

        logger.info('Retrieving pubsub subscription definitions from database for cluster_id=%s', cluster_id)

        # Single query to get subscriptions with their topic names
        query = session.query(
            PubSubSubscription,
            PubSubTopic.name
        ).outerjoin(
            PubSubSubscriptionTopic, PubSubSubscription.id == PubSubSubscriptionTopic.subscription_id
        ).outerjoin(
            PubSubTopic, PubSubSubscriptionTopic.topic_id == PubSubTopic.id
        ).filter(PubSubSubscription.cluster_id == cluster_id)

        results = query.all()

        # Group topics by subscription
        subscription_topics = {}
        for subscription, topic_name in results:
            if subscription.sub_key not in subscription_topics:
                subscription_topics[subscription.sub_key] = {
                    'subscription': subscription,
                    'topics': []
                }
            if topic_name:
                subscription_topics[subscription.sub_key]['topics'].append(topic_name)

        # Process subscriptions directly
        for sub_key, data in subscription_topics.items():
            subscription = data['subscription']
            topic_names = sorted(data['topics'])

            subscription_dict = {
                'id': subscription.id,
                'sub_key': subscription.sub_key,
                'sec_base_id': subscription.sec_base_id,
                'delivery_type': subscription.delivery_type,
                'push_type': subscription.push_type,
                'rest_push_endpoint_id': subscription.rest_push_endpoint_id,
                'push_service_name': subscription.push_service_name,
                'is_active': subscription.is_active,
                'cluster_id': subscription.cluster_id,
                'topic_name_list': topic_names
            }
            out[subscription.sub_key] = subscription_dict

        logger.info('Total pubsub subscription definitions from DB: %d', len(out))
        for sub_key in out:
            logger.info('DB pubsub subscription def: sub_key=%s', sub_key)

        return out

# ################################################################################################################################

    def create_pubsub_subscription_definition(self, definition:'stranydict', session:'SASession') -> 'PubSubSubscription':
        """ Creates a new pubsub subscription definition in the database.
        """
        logger.info('Creating pubsub subscription definition: %s', definition)

        instance = PubSubSubscription()
        instance.cluster_id = self.importer.cluster_id
        instance.sub_key = new_sub_key(definition['username'])
        instance.sec_base_id = definition['sec_base_id']
        instance.delivery_type = definition['delivery_type']
        instance.push_type = definition.get('push_type')
        instance.rest_push_endpoint_id = definition.get('rest_push_endpoint_id')
        instance.push_service_name = definition.get('push_service_name')
        instance.is_active = definition.get('is_active', True)

        logger.info('Creating subscription: sub_key=%s, sec_base_id=%s, cluster_id=%s', instance.sub_key, instance.sec_base_id, instance.cluster_id)

        set_instance_opaque_attrs(instance, definition)
        session.add(instance)
        session.commit()
        logger.info('Subscription created with ID %s', instance.id)

        # Create subscription-topic associations
        logger.info('Creating topic associations for subscription ID %s with topics %s', instance.id, definition['topic_id_list'])

        for topic_id in definition['topic_id_list']:
            logger.info('Adding topic association: subscription_id=%s, topic_id=%s, cluster_id=%s', instance.id, topic_id, self.importer.cluster_id)

            # Check if association already exists
            existing = session.query(PubSubSubscriptionTopic).filter(
                PubSubSubscriptionTopic.subscription_id == instance.id,
                PubSubSubscriptionTopic.topic_id == topic_id,
                PubSubSubscriptionTopic.cluster_id == self.importer.cluster_id
            ).first()

            if existing:
                logger.info('Topic association already exists: subscription_id=%s, topic_id=%s, cluster_id=%s', instance.id, topic_id, self.importer.cluster_id)
                continue

            sub_topic = PubSubSubscriptionTopic()
            sub_topic.subscription_id = instance.id
            sub_topic.topic_id = topic_id
            sub_topic.pattern_matched = 'enmasse'
            sub_topic.cluster_id = self.importer.cluster_id
            session.add(sub_topic)

        session.commit()
        logger.info('All topic associations committed for subscription ID %s', instance.id)
        return instance

# ################################################################################################################################

    def update_pubsub_subscription_definition(self, definition:'stranydict', session:'SASession') -> 'PubSubSubscription':
        """ Updates an existing pubsub subscription definition in the database.
        """
        logger.info('Updating pubsub subscription definition: %s', definition)

        instance = session.query(PubSubSubscription).filter_by(id=definition['id']).one()
        instance.sec_base_id = definition['sec_base_id']
        instance.delivery_type = definition['delivery_type']
        instance.push_type = definition.get('push_type')
        instance.rest_push_endpoint_id = definition.get('rest_push_endpoint_id')
        instance.push_service_name = definition.get('push_service_name')
        instance.is_active = definition.get('is_active', True)

        set_instance_opaque_attrs(instance, definition)

        # Update subscription-topic associations
        session.query(PubSubSubscriptionTopic).filter_by(subscription_id=instance.id).delete()
        for topic_id in definition['topic_id_list']:
            sub_topic = PubSubSubscriptionTopic()
            sub_topic.subscription_id = instance.id
            sub_topic.topic_id = topic_id
            sub_topic.pattern_matched = 'enmasse'
            sub_topic.cluster_id = self.importer.cluster_id
            session.add(sub_topic)

        session.commit()
        return instance

# ################################################################################################################################

    def find_existing_subscription_for_security(self, db_defs:'anydict', sec_base_id:'int') -> 'stranydict':
        """ Finds existing subscription for a security definition. Returns None if not found.
        """
        logger.info('Searching for existing subscription with sec_base_id=%s in %d db_defs', sec_base_id, len(db_defs))
        for sub_key, db_def in db_defs.items():
            db_sec_base_id = db_def.get('sec_base_id')
            logger.info('Checking db_def sub_key=%s, sec_base_id=%s', sub_key, db_sec_base_id)
            if db_sec_base_id == sec_base_id:
                logger.info('Found matching subscription: %s', db_def)
                return db_def
        else:
            # If we are here, it means this security definition must have existed
            # but it doesn't have any subscriptions, so we can return an empty dict to indicate that.
            logger.info('No existing subscription found for sec_base_id=%s', sec_base_id)
            return {}

# ################################################################################################################################

    def should_create_pubsub_subscription_definition(self, yaml_def:'stranydict', db_defs:'anydict', sec_base_id:'int') -> 'bool':
        """ Determines if a pubsub subscription definition should be created.
        """
        logger.info('Checking if should create subscription for sec_base_id=%s', sec_base_id)
        # Check if any existing subscription exists for this security definition
        existing_subscription = self.find_existing_subscription_for_security(db_defs, sec_base_id)
        logger.info('Found existing subscription: %s', existing_subscription)
        if existing_subscription:
            logger.info('Should NOT create - existing subscription found')
            return False

        logger.info('Should CREATE - no existing subscription found')
        return True

# ################################################################################################################################

    def should_update_pubsub_subscription_definition(self, yaml_def:'stranydict', db_def:'stranydict') -> 'bool':
        """ Determines if a pubsub subscription definition should be updated by comparing YAML and DB definitions.
        """

        # Compare delivery_type
        yaml_delivery_type = yaml_def.get('delivery_type')
        db_delivery_type = db_def.get('delivery_type')
        if yaml_delivery_type != db_delivery_type:
            logger.info('delivery_type differs: YAML=%s, DB=%s', yaml_delivery_type, db_delivery_type)
            return True

        # Compare push_type
        yaml_push_type = yaml_def.get('push_type', PubSub.Push_Type.Service)
        db_push_type = db_def.get('push_type', PubSub.Push_Type.Service)
        if yaml_push_type != db_push_type:
            logger.info('push_type differs: YAML=%s, DB=%s', yaml_push_type, db_push_type)
            return True

        # Compare is_active
        yaml_is_active = yaml_def.get('is_active', True)
        db_is_active = db_def.get('is_active', True)

        if yaml_is_active is not db_is_active:
            logger.info('is_active differs: YAML=%s, DB=%s', yaml_is_active, db_is_active)
            return True

        # Compare topic lists
        yaml_topic_list = sorted(yaml_def.get('topic_list', []))
        db_topic_list = sorted(db_def.get('topic_name_list', []))
        if yaml_topic_list != db_topic_list:
            logger.info('topic_list differs: YAML=%s, DB=%s', yaml_topic_list, db_topic_list)
            return True

        return False

# ################################################################################################################################

    def get_security_base_id_by_name(self, security_name:'str', session:'SASession') -> 'int':
        """ Gets the security base ID by name.
        """
        security_base = session.query(SecurityBase).filter_by(name=security_name).first()
        if not security_base:
            raise ValueError(f'Security definition not found: {security_name}')
        return security_base.id

# ################################################################################################################################

    def get_topic_id_by_name(self, topic_name:'str', session:'SASession') -> 'int':
        """ Gets the topic ID by name.
        """
        topic = session.query(PubSubTopic).filter_by(name=topic_name).first()
        if not topic:
            raise ValueError(f'Topic not found: {topic_name}')
        return topic.id

# ################################################################################################################################

    def get_rest_endpoint_id_by_name(self, endpoint_name:'str', session:'SASession') -> 'int':
        """ Gets the REST endpoint ID by name.
        """
        endpoint = session.query(HTTPSOAP).filter_by(name=endpoint_name).first()
        if not endpoint:
            raise ValueError(f'REST endpoint not found: {endpoint_name}')
        return endpoint.id

# ################################################################################################################################

    def sync_pubsub_subscription_definitions(self, subscription_list:'list', session:'SASession') -> 'tuple':
        """ Synchronizes pubsub subscription definitions from YAML with the database.
        """
        logger.info('Processing %d pubsub subscription definitions from YAML', len(subscription_list))

        # Get existing definitions from database
        db_defs = self.get_pubsub_subscription_defs_from_db(session, self.importer.cluster_id)

        created = []
        updated = []

        for yaml_def in subscription_list:
            security_name = yaml_def['security']
            topic_list = yaml_def.get('topic_list') or []
            delivery_type = yaml_def['delivery_type']

            logger.info('Processing YAML pubsub subscription definition: security=%s, topics=%s, delivery_type=%s',
                       security_name, topic_list, delivery_type)

            # Get security base ID
            sec_base_id = self.get_security_base_id_by_name(security_name, session)

            # Get topic IDs
            topic_id_list = []
            for topic_name in topic_list:
                topic_id = self.get_topic_id_by_name(topic_name, session)
                topic_id_list.append(topic_id)

            # Prepare subscription definition
            subscription_def = {
                'sec_base_id': sec_base_id,
                'delivery_type': delivery_type,
                'topic_id_list': topic_id_list,
                'is_active': yaml_def.get('is_active', True),
                'username': security_name
            }

            # Handle push-specific fields
            if delivery_type == PubSub.Delivery_Type.Push:
                if 'push_rest_endpoint' in yaml_def:
                    rest_endpoint_id = self.get_rest_endpoint_id_by_name(yaml_def['push_rest_endpoint'], session)
                    subscription_def['rest_push_endpoint_id'] = rest_endpoint_id
                    subscription_def['push_type'] = PubSub.Push_Type.REST
                elif 'push_service' in yaml_def:
                    subscription_def['push_service_name'] = yaml_def['push_service']
                    subscription_def['push_type'] = PubSub.Push_Type.Service

            # Add other opaque attributes
            for key, value in yaml_def.items():
                if key not in ['security', 'topic_list', 'delivery_type', 'push_rest_endpoint', 'push_service', 'is_active']:
                    subscription_def[key] = value

            # Create a key for tracking
            key = f'{security_name}_{sorted(topic_list)}_{delivery_type}'

            should_create = self.should_create_pubsub_subscription_definition(yaml_def, db_defs, sec_base_id)
            logger.info('Decision for security %s: should_create=%s', security_name, should_create)

            if should_create:

                # Create a new definition
                instance = self.create_pubsub_subscription_definition(subscription_def, session)
                created.append(instance)

                # Add to our tracking dictionary
                self.pubsub_subscription_defs[instance.sub_key] = {
                    'id': instance.id,
                    'sub_key': instance.sub_key,
                    'sec_base_id': instance.sec_base_id,
                    'delivery_type': instance.delivery_type,
                    'push_type': instance.push_type,
                    'rest_push_endpoint_id': instance.rest_push_endpoint_id,
                    'push_service_name': instance.push_service_name,
                    'is_active': instance.is_active,
                    'cluster_id': instance.cluster_id
                }

            else:

                existing_sub = self.find_existing_subscription_for_security(db_defs, sec_base_id)

                # Update existing subscription
                if self.should_update_pubsub_subscription_definition(yaml_def, existing_sub):
                    subscription_def['id'] = existing_sub['id']
                    instance = self.update_pubsub_subscription_definition(subscription_def, session)
                    updated.append(instance)

                    # Update our tracking dictionary
                    self.pubsub_subscription_defs[instance.sub_key] = {
                        'id': instance.id,
                        'sub_key': instance.sub_key,
                        'sec_base_id': instance.sec_base_id,
                        'delivery_type': instance.delivery_type,
                        'push_type': instance.push_type,
                        'rest_push_endpoint_id': instance.rest_push_endpoint_id,
                        'push_service_name': instance.push_service_name,
                        'is_active': instance.is_active,
                        'cluster_id': instance.cluster_id
                    }

        logger.info('Pubsub subscription definitions sync completed: created=%d, updated=%d', len(created), len(updated))
        return created, updated

# ################################################################################################################################
# ################################################################################################################################
