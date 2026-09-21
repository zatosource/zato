# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue delivery lines of the Alerts tab - the two an outgoing connection that can use a queue carries in a
# section of their own, messages in the DLQ and a queue backing up. alerts_tab.py appends them to the lines of the
# REST, SOAP, FHIR and MLLP outgoing types that alerts_tab_lines.py builds.

# Zato
from zato.admin.web.alerts_tab_lines import Line_Kind_Popover
from zato.common.alerting.object_config import alert_type_fhir, alert_type_mllp_outgoing, alert_type_rest, alert_type_soap

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

Section_Queue = 'Queue'

# The types whose connections can use a queue
queue_alert_types = (alert_type_rest, alert_type_soap, alert_type_fhir, alert_type_mllp_outgoing)

# What both lines say about where their numbers come from
_reads_the_connection = 'The depth is read off the connection itself, not off the audit log, so this line works ' + \
    'with the audit log off.'

# ################################################################################################################################
# ################################################################################################################################

def dlq_messages_line() -> 'anydict':
    out = {
        'name': 'dlq_messages',
        'section': Section_Queue,
        'kind': Line_Kind_Popover,
        'label': 'Messages in the DLQ',
        'title': 'Messages in the DLQ',
        'fields': ['dlq_messages'],
        'rows': [['dlq_messages']],
        'summary': 'Alert at {dlq_messages|message|messages} in the DLQ',
        'how_it_works': 'How many messages in the connection\'s DLQ raise an alert. A message reaches the DLQ once every ' + \
            'attempt to deliver it from the queue has failed and stays there until somebody retries or discards it, so ' + \
            'the alert stays open for as long as the DLQ holds that many. ' + _reads_the_connection,
    }
    return out

# ################################################################################################################################

def queue_backlog_line() -> 'anydict':
    out = {
        'name': 'queue_backlog',
        'section': Section_Queue,
        'kind': Line_Kind_Popover,
        'label': 'Queue backlog',
        'title': 'Queue backlog',
        'fields': ['queue_depth'],
        'rows': [['queue_depth']],
        'summary': 'Alert at {queue_depth|message|messages} waiting in the queue',
        'how_it_works': 'How many messages waiting in the connection\'s queue raise an alert. Messages wait there while ' + \
            'the receiving system turns them down or is not there, so a deep queue is a system that has been ' + \
            'unavailable for a while. ' + _reads_the_connection,
    }
    return out

# ################################################################################################################################

def queue_lines() -> 'anylist':
    """ The two queue delivery lines, in the order they are read.
    """
    out = [
        dlq_messages_line(),
        queue_backlog_line(),
    ]
    return out

# ################################################################################################################################

def add_queue_lines(type_lines:'anydict') -> 'None':
    """ Appends the queue delivery lines to the lines of every type whose connections can use a queue.
    """
    for alert_type in queue_alert_types:
        type_lines[alert_type] = type_lines[alert_type] + queue_lines()

# ################################################################################################################################
# ################################################################################################################################
