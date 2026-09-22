# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue delivery rules every kind of outgoing connection that can use a queue ships - messages in the DLQ and
# a queue backing up. The two are the same for REST, SOAP, FHIR and MLLP outgoing connections apart from the
# source they match on and what the connection is called, so each ruleset builds its own pair from here.

# ################################################################################################################################
# ################################################################################################################################

# The names of the two rules and of the defaults each compares its depth against
DLQ_Messages_Rule = 'DLQ_Messages'
Queue_Backlog_Rule = 'Queue_Backlog'

DLQ_Threshold_Default = 'dlq_threshold'
Queue_Depth_Threshold_Default = 'queue_depth_threshold'

# One message in the DLQ is one message somebody has to look at, and a thousand waiting in the queue is a
# receiving system that has been unavailable for a while
DLQ_Threshold_Value = 1
Queue_Depth_Threshold_Value = 1000

# ################################################################################################################################
# ################################################################################################################################

_queue_rules_template = """
rule
    {dlq_rule}
docs
    {a_connection} whose DLQ holds a message raises an error email alert.
    A message reaches the DLQ once every attempt to deliver it from the queue has failed, and it stays there until somebody
    retries or discards it, so the alert stays open for as long as the DLQ holds anything. The depth is read off the connection
    itself rather than the audit log.
defaults
    {dlq_default} = {dlq_value}
when
    alert.source is '{source}' and
    alert.dlq_depth is at least default.{dlq_default}
then
    outcome.action = 'email'
    outcome.severity = 'error'

rule
    {backlog_rule}
docs
    {a_connection} whose queue holds a thousand messages waiting to be delivered raises a warning email alert.
    Messages wait in the queue while the receiving system turns them down or is not there, so a queue this deep is a
    system that has been unavailable for a while. The depth is read off the connection itself rather than the audit log.
defaults
    {backlog_default} = {backlog_value}
when
    alert.source is '{source}' and
    alert.queue_depth is at least default.{backlog_default}
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

def build_queue_rules(source:'str', a_connection:'str') -> 'str':
    """ The two queue delivery rules of one kind of outgoing connection - the source is what its facts carry
    and a_connection is how its docs open, e.g. `A REST outgoing connection`.
    """
    out = _queue_rules_template.format(
        dlq_rule=DLQ_Messages_Rule,
        backlog_rule=Queue_Backlog_Rule,
        dlq_default=DLQ_Threshold_Default,
        backlog_default=Queue_Depth_Threshold_Default,
        dlq_value=DLQ_Threshold_Value,
        backlog_value=Queue_Depth_Threshold_Value,
        source=source,
        a_connection=a_connection,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
