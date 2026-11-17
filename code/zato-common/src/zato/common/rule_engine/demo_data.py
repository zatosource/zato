# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# What the demo ruleset is called, which is also the name of its file on disk.
Demo_Ruleset_Name = 'incident_escalation'

# ################################################################################################################################
# ################################################################################################################################

# One incident, five facts about it and five rules over them - every industry has incidents,
# severities, owners and a clock, so the demo reads the same to everyone who opens it.
demo_zrules_contents = """
# ################################################################################################################################

rule
    Critical_Unacknowledged
docs
    A severity 1 incident nobody has acknowledged pages the on-call engineer and tells the manager.
when
    incident.severity is 1 and
    incident.acknowledged is false
then
    outcome.queue = 'on_call'
    outcome.notify = 'manager'
    outcome.page_on_call = true

# ################################################################################################################################

rule
    After_Hours_Routing
docs
    Outside business hours a serious incident goes to the on-call engineer, everything else to the normal queue.
when
    incident.business_hours is false and
    incident.severity is at most 2
then
    outcome.queue = 'on_call'
    outcome.notify = 'on_call_engineer'
else
    outcome.queue = 'normal'
    outcome.notify = 'service_desk'

# ################################################################################################################################

rule
    Impact_Escalation
docs
    An incident customers can feel, open for more than an hour, is escalated whatever the time of day.
when
    incident.severity is at most 2 and
    incident.customer_impact is true and
    incident.hours_open is more than 1
then
    outcome.queue = 'escalation'
    outcome.notify = 'incident_manager'
    outcome.escalate = true

# ################################################################################################################################

rule
    Stale_Low_Priority
docs
    A low-priority incident still open after a day is downgraded and its reporter is asked to confirm it.
defaults
    stale_hours = 24
when
    incident.severity is at least 3 and
    incident.hours_open is more than default.stale_hours
then
    outcome.downgrade = true
    outcome.notify = 'reporter'

# ################################################################################################################################

rule
    Auto_Close_No_Response
docs
    The lowest severity, never acknowledged and three days old - the incident closes itself.
when
    incident.severity is 4 and
    incident.acknowledged is false and
    incident.hours_open is more than 72
then
    outcome.queue = 'closed'
    outcome.close_reason = 'no response from the reporter'

# ################################################################################################################################
""".strip()

# ################################################################################################################################
# ################################################################################################################################
