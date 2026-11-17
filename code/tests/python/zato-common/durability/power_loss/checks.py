# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the database of a server holds once the server is back after a loss of power, compared with what the server
# acknowledged to the clients of the workload before the loss.

# stdlib
from collections import Counter

# Zato
from workload import ModuleCtx as WorkloadCtx
from zato.common.audit_log.common import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from workload import Workload
    from zato.common.typing_ import any_, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The events that each acknowledged invocation of the audited channel leaves in the audit log
    Audited_Event_Types = {AuditEvent.Request_Received, AuditEvent.Response_Sent}

    # How many identifiers a message of a failed assertion lists at most
    Max_Listed = 20

# ################################################################################################################################
# ################################################################################################################################

class DatabaseReader:
    """ Reads the database of a server outside of the server, through a connection that the given callable opens.
    """

    def __init__(self, connect:'callable_') -> 'None':
        self.connect = connect

    def read_rows(self, query:'str') -> 'list[any_]':
        connection = self.connect()

        try:
            cursor = connection.cursor()
            _ = cursor.execute(query)
            out = list(cursor.fetchall())
        finally:
            connection.close()

        return out

# ################################################################################################################################
# ################################################################################################################################

def _describe(values:'strlist') -> 'str':
    listed = sorted(values)[:ModuleCtx.Max_Listed]

    out = f'{len(values)} -> {listed}'
    return out

# ################################################################################################################################

def check_traffic(workload:'Workload') -> 'None':
    """ Asserts that the server acknowledged requests of every kind before it lost its power.
    """
    assert workload.published, f'No publication acknowledged, failures -> {workload.failures}'
    assert workload.acked, f'No acknowledgement acknowledged, failures -> {workload.failures}'
    assert workload.audited_cids, f'No audited invocation acknowledged, failures -> {workload.failures}'

# ################################################################################################################################

def check_publications(workload:'Workload', reader:'DatabaseReader') -> 'None':
    """ Asserts that every acknowledged publication is stored, and that no publication is stored twice.
    """
    query = f"select msg_id, correl_id from pubsub_message where topic_name = '{WorkloadCtx.Topic_Name}'"
    rows = reader.read_rows(query)

    stored_msg_ids:'set[str]' = set()
    correl_id_counts:'Counter[str]' = Counter()

    for msg_id, correl_id in rows:
        stored_msg_ids.add(msg_id)
        correl_id_counts[correl_id] += 1

    missing:'strlist' = []

    for correl_id, msg_id in workload.published.items():
        if msg_id not in stored_msg_ids:
            missing.append(correl_id)

    assert not missing, f'Acknowledged publications lost -> {_describe(missing)}'

    repeated:'strlist' = []

    for correl_id, count in correl_id_counts.items():
        if count > 1:
            repeated.append(correl_id)

    assert not repeated, f'Publications stored more than once -> {_describe(repeated)}'

# ################################################################################################################################

def check_acknowledgements(workload:'Workload', reader:'DatabaseReader') -> 'None':
    """ Asserts that no message whose acknowledgement was acknowledged still waits in the queue.
    """
    query = 'select m.msg_id from pubsub_delivery d join pubsub_message m on m.id = d.message_id ' + \
        f"where d.topic_name = '{WorkloadCtx.Topic_Name}'"

    rows = reader.read_rows(query)

    pending:'set[str]' = set()

    for row in rows:
        pending.add(row[0])

    returned = pending & workload.acked
    returned = list(returned)

    assert not returned, f'Acknowledged messages back in the queue -> {_describe(returned)}'

# ################################################################################################################################

def check_audit_events(workload:'Workload', reader:'DatabaseReader') -> 'None':
    """ Asserts that every acknowledged invocation of the audited channel has its events in the audit log.
    """
    query = f"select cid, event_type from event where object_name = '{WorkloadCtx.Audited_Channel_Name}'"
    rows = reader.read_rows(query)

    event_types:'dict[str, set[str]]' = {}

    for cid, event_type in rows:
        if cid not in event_types:
            event_types[cid] = set()
        event_types[cid].add(event_type)

    missing:'strlist' = []

    for cid in workload.audited_cids:
        if cid not in event_types:
            missing.append(cid)
        elif not ModuleCtx.Audited_Event_Types <= event_types[cid]:
            missing.append(cid)

    assert not missing, f'Audit events of acknowledged invocations lost -> {_describe(missing)}'

# ################################################################################################################################

def check_redelivery(workload:'Workload') -> 'None':
    """ Asserts that no message whose acknowledgement was acknowledged was delivered again once the server was back.
    """
    redelivered = set(workload.drained) & workload.acked
    redelivered = list(redelivered)

    assert not redelivered, f'Acknowledged messages delivered again -> {_describe(redelivered)}'

# ################################################################################################################################
# ################################################################################################################################
