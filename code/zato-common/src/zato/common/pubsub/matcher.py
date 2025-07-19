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

        compiled_regex = re.compile(regex_pattern)

        # Cache the compiled pattern
        cache_entry = CacheEntry()
        cache_entry.compiled_regex = compiled_regex
        cache_entry.pattern = pattern
        self._pattern_cache[pattern] = cache_entry

        return compiled_regex

    def _parse_permissions(self, permissions:'List[anydict]') -> 'ParsedPermissions':
        """ Parse permission dicts into pub and sub patterns.
        """
        pub_patterns = []
        sub_patterns = []

        for perm_dict in permissions:
            access_type = perm_dict.get('access_type', '')
            pattern = perm_dict.get('pattern', '')

            if access_type == PubSub.API_Client.Publisher:
                pub_patterns.append(pattern)
            elif access_type == PubSub.API_Client.Subscriber:
                sub_patterns.append(pattern)
            elif access_type == PubSub.API_Client.Publisher_Subscriber:
                pub_patterns.append(pattern)
                sub_patterns.append(pattern)

        parsed_perms = ParsedPermissions()
        parsed_perms.pub_patterns = pub_patterns
        parsed_perms.sub_patterns = sub_patterns
        return parsed_perms

    def add_client(self, client_id:'str', permissions:'List[anydict]') -> 'None':
        """ Add a new client with permissions.
        """
        with self._lock:
            parsed_perms = self._parse_permissions(permissions)

            pub_pattern_infos = []
            for pattern in parsed_perms.pub_patterns:
                compiled_regex = self._compile_pattern(pattern)
                pattern_info = PatternInfo()
                pattern_info.pattern = pattern
                pattern_info.compiled_regex = compiled_regex
                pattern_info.is_pub = True
                pattern_info.is_sub = False
                pub_pattern_infos.append(pattern_info)

            sub_pattern_infos = []
            for pattern in parsed_perms.sub_patterns:
                compiled_regex = self._compile_pattern(pattern)
                pattern_info = PatternInfo()
                pattern_info.pattern = pattern
                pattern_info.compiled_regex = compiled_regex
                pattern_info.is_pub = False
                pattern_info.is_sub = True
                sub_pattern_infos.append(pattern_info)

            # Sort patterns alphabetically with wildcards last
            pub_pattern_infos.sort(key=self._pattern_info_sort_key)
            sub_pattern_infos.sort(key=self._pattern_info_sort_key)
            
            client_perms = ClientPermissions()
            client_perms.client_id = client_id
            client_perms.pub_patterns = pub_pattern_infos
            client_perms.sub_patterns = sub_pattern_infos
            self._clients[client_id] = client_perms

    def remove_client(self, client_id:'str') -> 'None':
        """ Remove a client and all its permissions.
        """
        with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]

    def set_permissions(self, client_id:'str', permissions:'List[anydict]') -> 'None':
        """ Set/update all permissions for a client.
        """
        with self._lock:
            if client_id not in self._clients:
                self.add_client(client_id, permissions)
            else:
                # Update existing client
                parsed_perms = self._parse_permissions(permissions)

                pub_pattern_infos = []
                for pattern in parsed_perms.pub_patterns:
                    compiled_regex = self._compile_pattern(pattern)
                    pattern_info = PatternInfo()
                    pattern_info.pattern = pattern
                    pattern_info.compiled_regex = compiled_regex
                    pattern_info.is_pub = True
                    pattern_info.is_sub = False
                    pub_pattern_infos.append(pattern_info)

                sub_pattern_infos = []
                for pattern in parsed_perms.sub_patterns:
                    compiled_regex = self._compile_pattern(pattern)
                    pattern_info = PatternInfo()
                    pattern_info.pattern = pattern
                    pattern_info.compiled_regex = compiled_regex
                    pattern_info.is_pub = False
                    pattern_info.is_sub = True
                    sub_pattern_infos.append(pattern_info)

                # Sort patterns alphabetically with wildcards last
                pub_pattern_infos.sort(key=self._pattern_info_sort_key)
                sub_pattern_infos.sort(key=self._pattern_info_sort_key)

                self._clients[client_id].pub_patterns = pub_pattern_infos
                self._clients[client_id].sub_patterns = sub_pattern_infos

    def _pattern_sort_key(self, pattern_info:'PatternInfo') -> 'tuple[str, bool]':
        """ Sort key for patterns: alphabetical with wildcards last.
        """
        has_wildcard = '*' in pattern_info.pattern
        return (pattern_info.pattern, has_wildcard)
    
    def _pattern_info_sort_key(self, pattern_info:'PatternInfo') -> 'tuple[str, bool]':
        """ Sort key for PatternInfo objects: alphabetical with wildcards last.
        """
        has_wildcard = '*' in pattern_info.pattern
        return (pattern_info.pattern, has_wildcard)

    def evaluate(self, client_id:'str', topic:'str', operation:'str') -> 'EvaluationResult':
        """ Evaluate if a client can perform an operation on a topic.
        """
        # No lock needed for read-only evaluation
        if client_id not in self._clients:
            result = EvaluationResult()
            result.is_ok = False
            result.client_id = client_id
            result.topic = topic
            result.operation = operation
            result.matched_pattern = None
            result.reason = f'Client {client_id} not found'
            return result

        client_perms = self._clients[client_id]

        # Select appropriate patterns based on operation
        if operation == 'pub':
            patterns = client_perms.pub_patterns
        elif operation == 'sub':
            patterns = client_perms.sub_patterns
        else:
            result = EvaluationResult()
            result.is_ok = False
            result.client_id = client_id
            result.topic = topic
            result.operation = operation
            result.matched_pattern = None
            result.reason = f'Invalid operation: {operation}'
            return result

        # Check patterns in order: exact matches first, then wildcards (pre-sorted)
        for pattern_info in patterns:
            if '*' not in pattern_info.pattern:
                # Exact match
                if topic == pattern_info.pattern:
                    result = EvaluationResult()
                    result.is_ok = True
                    result.client_id = client_id
                    result.topic = topic
                    result.operation = operation
                    result.matched_pattern = pattern_info.pattern
                    result.reason = None
                    return result
            else:
                # Wildcard match using compiled regex
                if pattern_info.compiled_regex.match(topic):
                    result = EvaluationResult()
                    result.is_ok = True
                    result.client_id = client_id
                    result.topic = topic
                    result.operation = operation
                    result.matched_pattern = pattern_info.pattern
                    result.reason = None
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

    def get_client_count(self) -> 'int':
        """ Get the number of registered clients.
        """
        return len(self._clients)

    def get_cache_size(self) -> 'int':
        """ Get the size of the pattern cache.
        """
        return len(self._pattern_cache)

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
