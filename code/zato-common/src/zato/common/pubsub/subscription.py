# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# gevent
from gevent.lock import RLock

# Zato
from zato.common.pubsub.models import MessageData, Subscription, Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TypeAlias

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.pubsub.rest')

# ################################################################################################################################
# ################################################################################################################################

class SubscriptionManager:
    """ Manages subscriptions to topics with pattern matching capabilities.
    """
    
    def __init__(self) -> 'None':
        self.topics:'Dict[str, Topic]' = {}
        self.lock = RLock()
        
        # Maps endpoint names to their subscriptions for quick lookup
        self.endpoint_to_subs:'Dict[str, List[Subscription]]' = {}
        
        # Pre-compile regex patterns for wildcards
        self.single_wildcard = re.compile(r'\*')
        self.double_wildcard = re.compile(r'\*\*')
        
        logger.info('Subscription manager initialized')

# ################################################################################################################################

    def _match_pattern(self, topic_name:'str', pattern:'str') -> 'bool':
        """ Checks if a topic name matches a subscription pattern.
        """
        # Exact match
        if pattern == topic_name:
            logger.debug(f'Pattern exact match: topic={topic_name}, pattern={pattern}')
            return True
            
        # Convert wildcards to regex patterns
        if '*' in pattern:
            # Replace ** with a special marker
            if '**' in pattern:
                # Double wildcard matches zero or more segments including dots
                regex_pattern = pattern.replace('**', '.*')
                regex_pattern = f'^{regex_pattern}$'
                if re.match(regex_pattern, topic_name):
                    logger.debug(f'Pattern double wildcard match: topic={topic_name}, pattern={pattern}')
                    return True
                    
            # Single wildcard matches exactly one segment (no dots)
            segments = pattern.split('.')
            topic_segments = topic_name.split('.')
            
            if len(segments) != len(topic_segments):
                return False
                
            for i, segment in enumerate(segments):
                if segment == '*':
                    continue
                if segment != topic_segments[i]:
                    return False
                    
            logger.debug(f'Pattern single wildcard match: topic={topic_name}, pattern={pattern}')
            return True
            
        return False

# ################################################################################################################################

    def get_matching_subscriptions(self, topic_name:'str') -> 'List[Subscription]':
        """ Gets all subscriptions that match the given topic name based on pattern matching rules.
        """
        out = []
        
        with self.lock:
            # First check if the topic exists directly
            if topic := self.topics.get(topic_name):
                out.extend(topic.subscriptions.values())
            
            # Then check for pattern-based subscriptions
            for topic_pattern, topic_obj in self.topics.items():
                if '*' in topic_pattern and self._match_pattern(topic_name, topic_pattern):
                    out.extend(topic_obj.subscriptions.values())
        
        logger.debug(f'Found {len(out)} matching subscriptions for topic {topic_name}')
        return out

# ################################################################################################################################

    def create_topic(self, topic_name:'str') -> 'Topic':
        """ Creates a new topic if it doesn't exist already.
        """
        with self.lock:
            if topic_name not in self.topics:
                self.topics[topic_name] = Topic(name=topic_name)
                logger.info(f'Created new topic: {topic_name}')
            return self.topics[topic_name]

# ################################################################################################################################

    def subscribe(self, topic_name:'str', endpoint_name:'str', patterns:'List[str]' = None) -> 'Subscription':
        """ Subscribes an endpoint to a topic.
        """
        patterns = patterns or [topic_name]
        sub_id = f'sub-{uuid.uuid4().hex[:8]}-{endpoint_name}-{topic_name}'
        
        with self.lock:
            # Create the topic if it doesn't exist
            topic = self.create_topic(topic_name)
            
            # Create the subscription
            subscription = Subscription(
                sub_id=sub_id,
                topic_name=topic_name,
                endpoint_name=endpoint_name,
                patterns=patterns
            )
            
            # Add subscription to the topic
            topic.subscriptions[sub_id] = subscription
            
            # Add subscription to the endpoint's map
            if endpoint_name not in self.endpoint_to_subs:
                self.endpoint_to_subs[endpoint_name] = []
            self.endpoint_to_subs[endpoint_name].append(subscription)
            
            logger.info(f'Created subscription: id={sub_id}, endpoint={endpoint_name}, topic={topic_name}, patterns={patterns}')
            return subscription

# ################################################################################################################################

    def unsubscribe(self, topic_name:'str', endpoint_name:'str') -> 'bool':
        """ Unsubscribes an endpoint from a topic.
        """
        with self.lock:
            # Check if topic exists
            if topic_name not in self.topics:
                logger.warning(f'Cannot unsubscribe: topic {topic_name} does not exist')
                return False
                
            topic = self.topics[topic_name]
            
            # Find subscriptions for this endpoint in this topic
            to_remove = []
            for sub_id, sub in topic.subscriptions.items():
                if sub.endpoint_name == endpoint_name:
                    to_remove.append(sub_id)
            
            # Remove subscriptions from topic
            for sub_id in to_remove:
                subscription = topic.subscriptions.pop(sub_id, None)
                logger.info(f'Removed subscription: id={sub_id}, endpoint={endpoint_name}, topic={topic_name}')
            
            # Remove subscriptions from endpoint map
            if endpoint_name in self.endpoint_to_subs:
                self.endpoint_to_subs[endpoint_name] = [
                    sub for sub in self.endpoint_to_subs[endpoint_name] 
                    if sub.topic_name != topic_name
                ]
                
                # Clean up empty lists
                if not self.endpoint_to_subs[endpoint_name]:
                    del self.endpoint_to_subs[endpoint_name]
            
            return bool(to_remove)

# ################################################################################################################################

    def get_endpoint_subscriptions(self, endpoint_name:'str') -> 'List[Subscription]':
        """ Gets all subscriptions for an endpoint.
        """
        with self.lock:
            return self.endpoint_to_subs.get(endpoint_name, [])

# ################################################################################################################################

    def get_subscription(self, topic_name:'str', endpoint_name:'str') -> 'Optional[Subscription]':
        """ Gets a specific subscription for an endpoint and topic.
        """
        with self.lock:
            if topic := self.topics.get(topic_name):
                for sub in topic.subscriptions.values():
                    if sub.endpoint_name == endpoint_name:
                        return sub
        return None

# ################################################################################################################################

    def publish_message(self, topic_name:'str', message:'MessageData') -> 'List[str]':
        """ Publishes a message to all matching subscriptions.
        """
        # Get all subscriptions that match this topic
        matching_subs = self.get_matching_subscriptions(topic_name)
        sub_ids = []
        
        with self.lock:
            for sub in matching_subs:
                # Add message to each subscription's queue (LIFO order)
                sub.messages.insert(0, message)
                sub_ids.append(sub.sub_id)
                logger.debug(f'Published message {message.msg_id} to subscription {sub.sub_id}')
        
        logger.info(f'Message {message.msg_id} published to topic {topic_name}, delivered to {len(sub_ids)} subscriptions')
        return sub_ids

# ################################################################################################################################

    def get_messages(self, topic_name:'str', endpoint_name:'str', destructive:'bool'=True) -> 'List[MessageData]':
        """ Retrieves messages from a subscription queue.
        If destructive is True, the messages are removed from the queue.
        """
        subscription = self.get_subscription(topic_name, endpoint_name)
        if not subscription:
            logger.warning(f'No subscription found for endpoint={endpoint_name}, topic={topic_name}')
            return []
        
        with self.lock:
            # Get a copy of the messages
            messages = list(subscription.messages)
            
            # If destructive, clear the subscription queue
            if destructive and messages:
                logger.info(f'Removing {len(messages)} messages from subscription {subscription.sub_id}')
                subscription.messages.clear()
                
        return messages

# ################################################################################################################################
# ################################################################################################################################
