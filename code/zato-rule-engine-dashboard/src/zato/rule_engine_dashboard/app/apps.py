# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.apps import AppConfig

# ################################################################################################################################
# ################################################################################################################################

class RuleEngineDashboardConfig(AppConfig):
    """ The rule engine dashboard's own Django application, holding its models.
    """
    name = 'zato.rule_engine_dashboard.app'
    label = 'rule_engine_dashboard'

# ################################################################################################################################
# ################################################################################################################################
