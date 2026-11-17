# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.apps import AppConfig
from django.db.backends.signals import connection_created

# Zato
from zato.common.db_env.connection import set_django_connection

# ################################################################################################################################
# ################################################################################################################################

class RuleEngineDashboardConfig(AppConfig):
    """ The rule engine dashboard's own Django application, holding its models.
    """
    name = 'zato.rule_engine_dashboard.app'
    label = 'rule_engine_dashboard'

    def ready(self) -> 'None':

        # Each connection of Django to the Zato database has the settings of durability of the engine factory
        connection_created.connect(set_django_connection)

# ################################################################################################################################
# ################################################################################################################################
