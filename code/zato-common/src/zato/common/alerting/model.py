# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alerting engine's data model - findings, rules and alerts. A finding is one thing
# a collector noticed, a rule says which findings matter and what to do about them,
# and an alert is a finding that matched a rule, stored with its dedup count
# and lifecycle. The engine itself carries no domain knowledge - domains contribute
# collector packs producing findings, everything from here on is generic.

from __future__ import annotations

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import dict_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
finding_list = list['Finding']
rule_list    = list['AlertRule']

# ################################################################################################################################
# ################################################################################################################################

# How long repeated findings keep incrementing an existing alert instead of raising a new one
Default_Dedup_Window_Seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

class AlertAction:
    """ What a rule does when it fires - the action menu. Slack and Teams
    are incoming-webhook posts, the rule stores the webhook URL.
    """
    Email_Digest     = 'email-digest'
    Invoke_Service   = 'invoke-service'
    Publish_To_Topic = 'publish-to-topic'
    Slack            = 'slack'
    Teams            = 'teams'

# ################################################################################################################################

class AlertSeverity:
    """ The severity of a finding - critical findings are always dispatched,
    regardless of dedup and digest settings.
    """
    Info     = 'info'
    Warning  = 'warning'
    Critical = 'critical'

# ################################################################################################################################

class AlertState:
    """ The lifecycle states of an alert - raised, acknowledged, resolved.
    """
    Unobserved = 'unobserved'
    Observed   = 'observed'
    Resolved   = 'resolved'

# ################################################################################################################################

class FindingKind:
    """ The kinds of findings the generic collectors produce. Domain-specific
    collector packs define their own kinds in addition to these.
    """
    Missing_Followup = 'missing-followup'
    Outstanding      = 'outstanding-above-threshold'
    Error_Rate       = 'error-rate-above-threshold'
    Feed_Silent      = 'feed-silent'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Finding:
    """ A single observation produced by a collector - the input to rule matching.
    """

    # The kind of finding - the primary field rules match on.
    kind: str = ''

    # The audit source the finding belongs to.
    source: str = ''

    # The object the finding is about - a channel, a connection, a partner pair.
    object_name: str = ''

    # The human-readable description.
    message: str = ''

    # The Dashboard path the description links to.
    link: str = ''

    # The severity - one of AlertSeverity.
    severity: str = AlertSeverity.Warning

# ################################################################################################################################

def new_finding(
    kind:'str',
    source:'str',
    object_name:'str',
    message:'str',
    *,
    link:'str' = '',
    severity:'str' = AlertSeverity.Warning,
    ) -> 'Finding':
    """ Builds one finding.
    """

    # Our response to produce
    out = Finding()

    out.kind = kind
    out.source = source
    out.object_name = object_name
    out.message = message
    out.link = link
    out.severity = severity

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AlertRule:
    """ One alerting rule - which findings it matches and what happens when it fires.
    The match fields are exact values, an empty one matches anything, and the kind
    is the only required one.
    """

    # The rule's own name - alerts are deduplicated and filed under it.
    name: str = ''

    # An inactive rule matches nothing while remaining configured.
    is_active: bool = True

    # What the rule matches - kind is required, source and object narrow it down.
    kind: str = ''
    source: str = ''
    object_name: str = ''

    # What the rule does when it fires - one of AlertAction.
    action: str = AlertAction.Email_Digest

    # The action's own configuration - an address list for email, a service name,
    # a topic name, or a webhook URL for Slack and Teams.
    action_config: 'stranydict' = dict_field()

    # Repeated findings about the same object within this window increment
    # the existing alert's count instead of raising a new one.
    dedup_window_seconds: int = Default_Dedup_Window_Seconds

# ################################################################################################################################

def new_rule(
    name:'str',
    kind:'str',
    *,
    source:'str' = '',
    object_name:'str' = '',
    action:'str' = AlertAction.Email_Digest,
    action_config:'stranydict | None' = None,
    dedup_window_seconds:'int' = Default_Dedup_Window_Seconds,
    is_active:'bool' = True,
    ) -> 'AlertRule':
    """ Builds one alerting rule.
    """
    if action_config is None:
        action_config = {}

    # Our response to produce
    out = AlertRule()

    out.name = name
    out.is_active = is_active
    out.kind = kind
    out.source = source
    out.object_name = object_name
    out.action = action
    out.action_config = action_config
    out.dedup_window_seconds = dedup_window_seconds

    return out

# ################################################################################################################################

def rule_matches(rule:'AlertRule', finding:'Finding') -> 'bool':
    """ Tells whether one rule applies to one finding - the kind must agree
    and the optional narrowing fields only count when the rule sets them.
    """

    # An inactive rule matches nothing
    if not rule.is_active:
        return False

    # The kind is the one required match
    if rule.kind != finding.kind:
        return False

    # The optional criteria narrow the match only when set
    if rule.source:
        if rule.source != finding.source:
            return False

    if rule.object_name:
        if rule.object_name != finding.object_name:
            return False

    return True

# ################################################################################################################################
# ################################################################################################################################
