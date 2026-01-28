# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class GetRuleList(Service):
    """ Returns all rule containers and rules.
    """
    name = 'zato.rules.get-rule-list'

    def handle(self):

        containers = []
        rules = []

        for container_name, container in self.server.rules._containers.items():
            containers.append({
                'name': container_name
            })

        for rule_name, rule in self.server.rules._all_rules.items():
            rules.append({
                'full_name': rule.full_name,
                'name': rule.name,
                'container_name': rule.container_name,
                'docs': rule.docs or '',
                'when': rule.when or '',
                'defaults': rule.defaults or {},
                'then': rule.then or {}
            })

        self.response.payload = {
            'containers': containers,
            'rules': rules
        }

# ################################################################################################################################
# ################################################################################################################################

class GetRule(Service):
    """ Returns details of a single rule.
    """
    name = 'zato.rules.get-rule'

    def handle(self):

        rule_name = self.request.input.get('name', '')

        if rule_name in self.server.rules._all_rules:
            rule = self.server.rules._all_rules[rule_name]
            self.response.payload = {
                'full_name': rule.full_name,
                'name': rule.name,
                'container_name': rule.container_name,
                'docs': rule.docs or '',
                'when': rule.when or '',
                'defaults': rule.defaults or {},
                'then': rule.then or {}
            }
        else:
            self.response.payload = {
                'error': 'Rule not found: {}'.format(rule_name)
            }

# ################################################################################################################################
# ################################################################################################################################

class ExecuteRule(Service):
    """ Executes a rule against provided data.
    """
    name = 'zato.rules.execute-rule'

    def handle(self):

        rule_name = self.request.input.get('name', '')
        data = self.request.input.get('data', {})

        if rule_name not in self.server.rules._all_rules:
            self.response.payload = {
                'matched': False,
                'error': 'Rule not found: {}'.format(rule_name)
            }
            return

        rule = self.server.rules._all_rules[rule_name]
        result = rule.match(data)

        if result:
            self.response.payload = {
                'matched': True,
                'result': {
                    'full_name': result.full_name,
                    'then': result.then
                }
            }
        else:
            self.response.payload = {
                'matched': False,
                'result': None
            }

# ################################################################################################################################
# ################################################################################################################################

class ReloadRules(Service):
    """ Reloads all rules from disk.
    """
    name = 'zato.rules.reload-rules'

    def handle(self):

        try:
            self.server.rules.load_rules_from_directory(
                self.server.fs_server_config.user_config_location
            )
            self.response.payload = {
                'reloaded': True
            }
        except Exception as e:
            self.response.payload = {
                'reloaded': False,
                'error': str(e)
            }

# ################################################################################################################################
# ################################################################################################################################
