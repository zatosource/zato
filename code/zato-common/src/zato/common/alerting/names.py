# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The names of the connections alerting delivers through - the Slack, Microsoft Teams
# and SMTP connections share one name and the LLM connection has its own. Each name
# is read from its environment variable, with the constant as the default, so seeding
# and delivery always resolve the same name.

# stdlib
import os

# Zato
from zato.common.api import Incidents

# ################################################################################################################################
# ################################################################################################################################

def get_notification_conn_name() -> 'str':
    """ The name of the Slack, Microsoft Teams and SMTP connections alerts deliver through.
    """
    if name := os.environ.get(Incidents.Env_Notification_Conn_Name):
        out = name
    else:
        out = Incidents.Notification_Conn_Name

    return out

# ################################################################################################################################

def get_llm_conn_name() -> 'str':
    """ The name of the LLM connection diagnoses go through when a rule names none of its own.
    """
    if name := os.environ.get(Incidents.Env_LLM_Connection_Name):
        out = name
    else:
        out = Incidents.LLM_Connection_Name

    return out

# ################################################################################################################################
# ################################################################################################################################
