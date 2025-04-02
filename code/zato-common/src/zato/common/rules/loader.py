# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from pathlib import Path
from threading import RLock

# Zato
from zato.common.rules.models import Container, Rule
from zato.common.rules.parser import parse_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dict_, str, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RuleLoader:
    """ Handles loading rules from files and directories.
    """
    
    def __init__(self):
        self._lock = RLock()
    
    def load_parsed_rules(self, parsed:'strdict', container_name:'str', 
                          all_rules:'dict_[str, Rule]', containers:'dict_[str, Container]',
                          cached_rules:'dict_[str, any_]') -> 'strlist':
        """ Load rules from parsed data.
        """
        # Our response to produce
        out = []
        
        # First, delete that container completely ..
        _ = containers.pop(container_name, None)
        
        # .. recreate it ..
        container = Container(container_name)
        containers[container.name] = container
        
        # .. go through each rule found ..
        # .. and note that we're iterating the full names alpabetically (because parsed is a SortedDict) ..
        # .. so the container's own dict will also always iterate over them alphabetically ..
        for full_name, rule_data in parsed.items():
            
            # .. build a new rule ..
            rule = Rule()
            rule.full_name = full_name
            rule.name = rule_data['name']
            rule.container_name = rule_data['container_name']
            rule.when = rule_data['when']
            
            try:
                from rule_engine import Rule as RuleImpl
                rule.when_impl = RuleImpl(rule.when)
            except Exception as e:
                logger.warning(f'Rule loading error -> {full_name} -> {rule.when} -> {e}')
                continue
            
            rule.then = rule_data['then']
            rule.defaults = rule_data.get('defaults', {})
            rule.docs = rule_data.get('docs', '')
            rule.invoke = rule_data.get('invoke', '')
            
            # .. make sure to delete it first from the global dict ..
            _ = all_rules.pop(rule.full_name, None)
            
            # .. we can now add it to the global dict ..
            all_rules[rule.full_name] = rule
            
            # .. add it to the container as well ..
            container.add_rule(rule)
            
            # Create a cached version of the rule
            from zato.common.rules.cache import CachedRule
            cached_rules[rule.full_name] = CachedRule(rule)
            
            # .. append it for later use ..
            out.append(rule.full_name)
        
        # .. finally, we can return a list of what we loaded.
        return out
    
    def load_rules_from_file(self, file_path:'str | Path', 
                            all_rules:'dict_[str, Rule]', containers:'dict_[str, Container]',
                            cached_rules:'dict_[str, any_]') -> 'strlist':
        """ Load rules from a file.
        """
        file_name = Path(file_path).name
        file_name = file_name.replace('.zrules', '')
        
        with self._lock:
            # Parse the contents of the file ..
            parsed = parse_file(file_path, file_name)
            
            # .. load it all ..
            result = self.load_parsed_rules(parsed, file_name, all_rules, containers, cached_rules)
            
            # .. log what was loaded ...
            logger.info(f'Loaded rules: {result}')
            
            # .. and tell the caller what we loaded.
            return result
    
    def load_rules_from_directory(self, root_dir:'str | Path', 
                                 all_rules:'dict_[str, Rule]', containers:'dict_[str, Container]',
                                 cached_rules:'dict_[str, any_]') -> 'strlist':
        """ Load rules from a directory.
        """
        # Our response to produce
        out = []
        
        # Go through all the matching files ..
        for elem in Path(root_dir).glob('*.zrules'):
            
            # .. read them all in.
            result = self.load_rules_from_file(elem, all_rules, containers, cached_rules)
            
            # .. append it for later use ..
            out.extend(result)
        
        # .. and return the list of what was loaded to our caller.
        return out

# ################################################################################################################################
# ################################################################################################################################
