# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The name of the connections alerting delivers through - the Slack, Microsoft Teams
# and SMTP connections share one name, read from its environment variable with the
# constant as the default, so seeding and delivery always resolve the same name.
# The LLM connection an explanation goes through is picked on the object's Alerts tab
# or on the alerting config, so it has no name of its own here.

# stdlib
import os

# Zato
from zato.common.api import Alerting

# ################################################################################################################################
# ################################################################################################################################

def get_notification_conn_name() -> 'str':
    """ The name of the Slack, Microsoft Teams and SMTP connections alerts deliver through.
    """
    if name := os.environ.get(Alerting.Env_Notification_Conn_Name):
        out = name
    else:
        out = Alerting.Notification_Conn_Name

    return out

# ################################################################################################################################
# ################################################################################################################################
