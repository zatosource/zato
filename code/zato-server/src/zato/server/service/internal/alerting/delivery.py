# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.alerting.engine import defaults_from_dict, dispatch_action
from zato.common.alerting.model import new_finding, new_rule
from zato.common.alerting.rendering import Template_Dir_Name
from zato.server.alerting_transports import build_alert_transports

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

def _get_template_dir(service:'AdminService') -> 'str':
    """ The server's own template directory - the bundled defaults answer
    until an environment created before the templates existed is recreated.
    """
    out = os.path.join(service.server.repo_location, Template_Dir_Name)

    if not os.path.isdir(out):
        out = ''

    return out

# ################################################################################################################################

def deliver(service:'AdminService', payload:'stranydict', explanation:'stranydict') -> 'None':
    """ Runs the rule's own action through the alerting engine, the way the sweep
    would have - the same transports, the same templates, the same deployment-level
    targets - with the explanation filled in. The explanation being present is what
    keeps the engine from handing the alert back here.
    """
    rule = new_rule(
        payload['rule'],
        payload['kind'],
        action=payload['action'],
        action_config=payload['action_config'],
        dedup_window_seconds=payload['dedup_window_seconds'],
        explain_with_llm=True,
    )

    finding = new_finding(payload['kind'], payload['source'], payload['object_name'], payload['message'],
        link=payload['link'], severity=payload['severity'], fact=payload['fact'], thresholds=payload['thresholds'],
        measures=payload['measures'])

    defaults = defaults_from_dict(payload['defaults'])
    transports = build_alert_transports(service, defaults.email_from)
    template_dir = _get_template_dir(service)

    dispatch_action(rule, finding, payload['alert_id'], payload['count'], transports, defaults, template_dir,
        explanation)

# ################################################################################################################################
# ################################################################################################################################
