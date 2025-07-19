# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Dict, List, Optional
import re

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Pattern
    from zato.common.typing_ import anydict, strlist

    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PatternInfo:
    """ Information about a single pattern.
    """
    pattern: 'str'
    compiled_regex: 'Pattern[str]'
    is_pub: 'bool'
    is_sub: 'bool'
    has_wildcards: 'bool'

# ################################################################################################################################

@dataclass(init=False)
class ClientPermissions:
    """ Permissions for a single client.
    """
    client_id: 'str'
    pub_patterns: 'List[PatternInfo]'
    sub_patterns: 'List[PatternInfo]'

# ################################################################################################################################

@dataclass(init=False)
class EvaluationResult:
    """ Result of pattern evaluation.
    """
    is_ok: 'bool'
    client_id: 'str'
    topic: 'str'
    operation: 'str'
    matched_pattern: 'Optional[str]'
    reason: 'Optional[str]'

# ################################################################################################################################

@dataclass(init=False)
class CacheEntry:
    """ Cache entry for compiled patterns.
    """
    compiled_regex: 'Pattern[str]'
    pattern: 'str'

# ################################################################################################################################

@dataclass(init=False)
class ParsedPermissions:
    """ Parsed permissions split into pub and sub patterns.
    """
    pub_patterns: 'List[str]'
    sub_patterns: 'List[str]'

# ################################################################################################################################
# ################################################################################################################################

class PatternMatcher:
    """ Standalone pattern matcher for pub/sub topic permissions.
    """

    def __init__(self) -> 'None':
        self._lock = RLock()
        self._clients: 'Dict[str, ClientPermissions]' = {}
        self._pattern_cache: 'Dict[str, CacheEntry]' = {}

# ################################################################################################################################

    def _compile_pattern(self, pattern:'str') -> 'Pattern[str]':
        """ Compile a topic pattern to regex, with caching.
        """
        if pattern in self._pattern_cache:
            return self._pattern_cache[pattern].compiled_regex

        # Convert pattern to regex based on GetMatches implementation
        regex_pattern = pattern.replace('**', '__DOUBLE_ASTERISK__')
        regex_pattern = regex_pattern.replace('*', '[^.]*')
        regex_pattern = regex_pattern.replace('__DOUBLE_ASTERISK__', '.*')
        regex_pattern = '^' + regex_pattern + '$'

        compiled_regex = re.compile(regex_pattern, re.IGNORECASE)

        # Cache the compiled pattern
        cache_entry = CacheEntry()
        cache_entry.compiled_regex = compiled_regex
        cache_entry.pattern = pattern
        self._pattern_cache[pattern] = cache_entry

        return compiled_regex

# ################################################################################################################################

    def _parse_permissions(self, permissions:'List[anydict]') -> 'ParsedPermissions':
        """ Parse permission dicts into pub and sub patterns.
        """
        publisher_patterns = []
        subscriber_patterns = []

        for permission_dict in permissions:
            access_type = permission_dict.get('access_type', '')
            pattern = permission_dict.get('pattern', '')

            if access_type == PubSub.API_Client.Publisher:
                publisher_patterns.append(pattern)
            elif access_type == PubSub.API_Client.Subscriber:
                subscriber_patterns.append(pattern)
            elif access_type == PubSub.API_Client.Publisher_Subscriber:
                publisher_patterns.append(pattern)
                subscriber_patterns.append(pattern)

        parsed_permissions = ParsedPermissions()
        parsed_permissions.pub_patterns = publisher_patterns
        parsed_permissions.sub_patterns = subscriber_patterns
        return parsed_permissions

# ################################################################################################################################

    def add_client(self, client_id:'str', permissions:'List[anydict]') -> 'None':
        """ Add a new client with permissions.
        """
        with self._lock:
            parsed_permissions = self._parse_permissions(permissions)

            publisher_pattern_list = []
            for pattern in parsed_permissions.pub_patterns:
                pattern_info = self._create_pattern_info(pattern, True, False)
                publisher_pattern_list.append(pattern_info)

            subscriber_pattern_list = []
            for pattern in parsed_permissions.sub_patterns:
                pattern_info = self._create_pattern_info(pattern, False, True)
                subscriber_pattern_list.append(pattern_info)

            # Sort patterns alphabetically with wildcards last
            publisher_pattern_list.sort(key=self._pattern_info_sort_key)
            subscriber_pattern_list.sort(key=self._pattern_info_sort_key)

            client_permissions = ClientPermissions()
            client_permissions.client_id = client_id
            client_permissions.pub_patterns = publisher_pattern_list
            client_permissions.sub_patterns = subscriber_pattern_list
            self._clients[client_id] = client_permissions

# ################################################################################################################################

    def remove_client(self, client_id:'str') -> 'None':
        """ Remove a client and all its permissions.
        """
        with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]

# ################################################################################################################################

    def set_permissions(self, client_id:'str', permissions:'List[anydict]') -> 'None':
        """ Set/update all permissions for a client.
        """
        with self._lock:

            if client_id not in self._clients:
                self.add_client(client_id, permissions)
            if client_id in self._clients:
                parsed_permissions = self._parse_permissions(permissions)

                publisher_pattern_list = []
                for pattern in parsed_permissions.pub_patterns:
                    pattern_info = self._create_pattern_info(pattern, True, False)
                    publisher_pattern_list.append(pattern_info)

                subscriber_pattern_list = []
                for pattern in parsed_permissions.sub_patterns:
                    pattern_info = self._create_pattern_info(pattern, False, True)
                    subscriber_pattern_list.append(pattern_info)

                # Sort patterns alphabetically with wildcards last
                publisher_pattern_list.sort(key=self._pattern_info_sort_key)
                subscriber_pattern_list.sort(key=self._pattern_info_sort_key)

                self._clients[client_id].pub_patterns = publisher_pattern_list
                self._clients[client_id].sub_patterns = subscriber_pattern_list

# ################################################################################################################################

    def _pattern_sort_key(self, pattern_info:'PatternInfo') -> 'tuple[str, bool]':
        """ Sort key for patterns: alphabetical with wildcards last.
        """
        has_wildcard = '*' in pattern_info.pattern
        return (pattern_info.pattern, has_wildcard)

# ################################################################################################################################

    def _pattern_info_sort_key(self, pattern_info:'PatternInfo') -> 'tuple':
        """ Sort key for PatternInfo objects: alphabetical with wildcards last.
        """
        return (pattern_info.has_wildcards, pattern_info.pattern)

    def _create_success_result(self, client_id:'str', topic:'str', operation:'str', matched_pattern:'str') -> 'EvaluationResult':
        """ Create a successful evaluation result.
        """
        result = EvaluationResult()
        result.is_ok = True
        result.client_id = client_id
        result.topic = topic
        result.operation = operation
        result.matched_pattern = matched_pattern
        result.reason = None
        return result

    def _create_pattern_info(self, pattern:'str', is_pub:'bool', is_sub:'bool') -> 'PatternInfo':
        """ Create a PatternInfo object.
        """
        compiled_regex = self._compile_pattern(pattern)
        pattern_info = PatternInfo()
        pattern_info.pattern = pattern.lower()
        pattern_info.compiled_regex = compiled_regex
        pattern_info.is_pub = is_pub
        pattern_info.is_sub = is_sub
        pattern_info.has_wildcards = '*' in pattern
        return pattern_info

# ################################################################################################################################

    def evaluate(self, client_id:'str', topic:'str', operation:'str') -> 'EvaluationResult':
        """ Evaluate if a client can perform an operation on a topic.
        """
        client_permissions = self._clients.get(client_id)
        if not client_permissions:
            result = EvaluationResult()
            result.is_ok = False
            result.client_id = client_id
            result.topic = topic
            result.operation = operation
            result.reason = 'Client not found'
            return result

        # Get patterns based on operation
        if operation == 'publish':
            pattern_list = client_permissions.pub_patterns
        elif operation == 'subscribe':
            pattern_list = client_permissions.sub_patterns
        else:
            result = EvaluationResult()
            result.is_ok = False
            result.client_id = client_id
            result.topic = topic
            result.operation = operation
            result.reason = f'Invalid operation: {operation}'
            return result

        # Check patterns in order: exact matches first, then wildcards (pre-sorted)
        for pattern_info in pattern_list:
            if not pattern_info.has_wildcards:
                # Exact match
                if topic.lower() == pattern_info.pattern:
                    result = self._create_success_result(client_id, topic, operation, pattern_info.pattern)
                    return result
            else:
                # Wildcard match using compiled regex
                if pattern_info.compiled_regex.match(topic):
                    result = self._create_success_result(client_id, topic, operation, pattern_info.pattern)
                    return result

        # No pattern matched
        result = EvaluationResult()
        result.is_ok = False
        result.client_id = client_id
        result.topic = topic
        result.operation = operation
        result.matched_pattern = None
        result.reason = 'No matching pattern found'
        return result

# ################################################################################################################################

    def get_client_count(self) -> 'int':
        """ Get the number of registered clients.
        """
        return len(self._clients)

# ################################################################################################################################

    def get_cache_size(self) -> 'int':
        """ Get the size of the pattern cache.
        """
        return len(self._pattern_cache)

# ################################################################################################################################

    def clear_cache(self) -> 'None':
        """ Clear the pattern cache.
        """
        with self._lock:
            self._pattern_cache.clear()

            # Recompile all patterns for existing clients
            for client_perms in self._clients.values():
                for pattern_info in client_perms.pub_patterns:
                    pattern_info.compiled_regex = self._compile_pattern(pattern_info.pattern)
                for pattern_info in client_perms.sub_patterns:
                    pattern_info.compiled_regex = self._compile_pattern(pattern_info.pattern)

# ################################################################################################################################
# ################################################################################################################################
