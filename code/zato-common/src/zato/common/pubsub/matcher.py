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
    
    def __init__(self, pattern:'str', compiled_regex:'Pattern[str]', is_pub:'bool', is_sub:'bool') -> 'None':
        self.pattern = pattern
        self.compiled_regex = compiled_regex
        self.is_pub = is_pub
        self.is_sub = is_sub

# ################################################################################################################################

@dataclass(init=False)
class ClientPermissions:
    """ Permissions for a single client.
    """
    client_id: 'str'
    pub_patterns: 'List[PatternInfo]'
    sub_patterns: 'List[PatternInfo]'
    
    def __init__(self, client_id:'str', pub_patterns:'List[PatternInfo]', sub_patterns:'List[PatternInfo]') -> 'None':
        self.client_id = client_id
        self.pub_patterns = pub_patterns
        self.sub_patterns = sub_patterns

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
    
    def __init__(
        self,
        is_ok:'bool',
        client_id:'str',
        topic:'str',
        operation:'str',
        matched_pattern:'Optional[str]' = None,
        reason:'Optional[str]' = None
    ) -> 'None':
        self.is_ok = is_ok
        self.client_id = client_id
        self.topic = topic
        self.operation = operation
        self.matched_pattern = matched_pattern
        self.reason = reason

# ################################################################################################################################

@dataclass(init=False)
class CacheEntry:
    """ Cache entry for compiled patterns.
    """
    compiled_regex: 'Pattern[str]'
    pattern: 'str'
    
    def __init__(self, compiled_regex:'Pattern[str]', pattern:'str') -> 'None':
        self.compiled_regex = compiled_regex
        self.pattern = pattern

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
        self._pattern_cache[pattern] = CacheEntry(
            compiled_regex=compiled_regex,
            pattern=pattern
        )
        
        return compiled_regex
    
    def _parse_permissions(self, permissions:'List[anydict]') -> 'tuple[List[str], List[str]]':
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
        
        return pub_patterns, sub_patterns
    
    def add_client(self, client_id:'str', permissions:'List[anydict]') -> 'None':
        """ Add a new client with permissions.
        """
        with self._lock:
            pub_patterns, sub_patterns = self._parse_permissions(permissions)
            
            pub_pattern_infos = []
            for pattern in pub_patterns:
                compiled_regex = self._compile_pattern(pattern)
                pub_pattern_infos.append(PatternInfo(
                    pattern=pattern,
                    compiled_regex=compiled_regex,
                    is_pub=True,
                    is_sub=False
                ))
            
            sub_pattern_infos = []
            for pattern in sub_patterns:
                compiled_regex = self._compile_pattern(pattern)
                sub_pattern_infos.append(PatternInfo(
                    pattern=pattern,
                    compiled_regex=compiled_regex,
                    is_pub=False,
                    is_sub=True
                ))
            
            self._clients[client_id] = ClientPermissions(
                client_id=client_id,
                pub_patterns=pub_pattern_infos,
                sub_patterns=sub_pattern_infos
            )
    
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
                pub_patterns, sub_patterns = self._parse_permissions(permissions)
                
                pub_pattern_infos = []
                for pattern in pub_patterns:
                    compiled_regex = self._compile_pattern(pattern)
                    pub_pattern_infos.append(PatternInfo(
                        pattern=pattern,
                        compiled_regex=compiled_regex,
                        is_pub=True,
                        is_sub=False
                    ))
                
                sub_pattern_infos = []
                for pattern in sub_patterns:
                    compiled_regex = self._compile_pattern(pattern)
                    sub_pattern_infos.append(PatternInfo(
                        pattern=pattern,
                        compiled_regex=compiled_regex,
                        is_pub=False,
                        is_sub=True
                    ))
                
                self._clients[client_id].pub_patterns = pub_pattern_infos
                self._clients[client_id].sub_patterns = sub_pattern_infos
    
    def _pattern_sort_key(self, pattern_info:'PatternInfo') -> 'tuple[bool, str]':
        """ Sort key function for patterns - wildcards last, then alphabetical.
        """
        return ('*' in pattern_info.pattern), pattern_info.pattern
    
    def evaluate(self, client_id:'str', topic:'str', operation:'str') -> 'EvaluationResult':
        """ Evaluate if a client can perform an operation on a topic.
        """
        # No lock needed for read-only evaluation
        if client_id not in self._clients:
            return EvaluationResult(
                is_ok=False,
                client_id=client_id,
                topic=topic,
                operation=operation,
                reason=f'Client {client_id} not found'
            )
        
        client_perms = self._clients[client_id]
        
        # Select appropriate patterns based on operation
        if operation == 'pub':
            patterns = client_perms.pub_patterns
        elif operation == 'sub':
            patterns = client_perms.sub_patterns
        else:
            return EvaluationResult(
                is_ok=False,
                client_id=client_id,
                topic=topic,
                operation=operation,
                reason=f'Invalid operation: {operation}'
            )
        
        # Sort patterns alphabetically with wildcards last (as per README)
        sorted_patterns = sorted(patterns, key=self._pattern_sort_key)
        
        # Check each pattern - first match wins
        for pattern_info in sorted_patterns:
            if '*' not in pattern_info.pattern:
                # Exact match
                if topic == pattern_info.pattern:
                    return EvaluationResult(
                        is_ok=True,
                        client_id=client_id,
                        topic=topic,
                        operation=operation,
                        matched_pattern=pattern_info.pattern
                    )
            else:
                # Wildcard match using compiled regex
                if pattern_info.compiled_regex.match(topic):
                    return EvaluationResult(
                        is_ok=True,
                        client_id=client_id,
                        topic=topic,
                        operation=operation,
                        matched_pattern=pattern_info.pattern
                    )
        
        # No pattern matched
        return EvaluationResult(
            is_ok=False,
            client_id=client_id,
            topic=topic,
            operation=operation,
            reason='No matching pattern found'
        )
    
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
