# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The items that the pub/sub writer process runs for the workers. Publications and acknowledgements go through
# the one PubSubWriter of the process, whose commit queue gathers the items of every worker into shared transactions,
# and each lease runs in a transaction of its own, as it does in a worker. The audit events of every worker go through
# a commit queue of their own, into shared transactions of the SQLite audit database. The writer process holds the only
# connection that writes these items to their SQLite files.

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.audit_log.api import AuditLog, get_commit_max_events
from zato.common.audit_log.wire import batch_from_wire
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.writes import new_pending_ack, new_pending_publication, PubSubWriter
from zato.common.pubsub.writer_process.frames import ItemKind
from zato.common.pubsub.writer_process.server import WriterServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.buffer import pending_event_list
    from zato.common.typing_ import anydict, anylist, intlist, strcalldict

    anydict = anydict
    anylist = anylist
    intlist = intlist
    pending_event_list = pending_event_list
    strcalldict = strcalldict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The server name of the audit log of the writer process, which builds no events, since each event that a worker sends
    # carries the name of its server already
    Audit_Server_Name = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AuditItem:
    """ The audit events that one worker sent in one item, which share a transaction with the events of other items.
    """
    events: 'pending_event_list'

# ################################################################################################################################
# ################################################################################################################################

class WriterHandlers:
    """ Runs the publications, acknowledgements, leases and audit events that the workers send to the writer process.
    """

    def __init__(self) -> 'None':
        self.writer = PubSubWriter()

        # The audit events of concurrent items are committed in shared transactions
        self.audit_log = AuditLog(ModuleCtx.Audit_Server_Name)
        self.audit_queue = CommitQueue(write_batch=self._write_audit_batch, max_weight=get_commit_max_events())

# ################################################################################################################################

    def publish(self, body:'anydict') -> 'anydict':
        """ Writes one message with its delivery rows, and returns the subscribers it was published to.
        """
        pending = new_pending_publication(body['message_values'])
        self.writer.publish(pending)

        out = {'subscriber_keys': pending.subscriber_keys}
        return out

# ################################################################################################################################

    def ack(self, body:'anydict') -> 'anydict':
        """ Removes the delivery rows of one subscriber, and returns how many it removed and how many messages
        became fully delivered.
        """
        pending = new_pending_ack(body['sub_key'], body['msg_ids'], body['sequence_ids'])
        self.writer.ack(pending)

        out = {
            'removed_count': pending.removed_count,
            'fully_delivered_count': pending.fully_delivered_count,
        }
        return out

# ################################################################################################################################

    def lease(self, body:'anydict') -> 'anydict':
        """ Leases the deliverable rows of one subscriber, and returns the rows of their messages and the attempt
        number of each message, as pairs, since the identifiers of the messages are integers.
        """
        engine = get_pubsub_engine()

        rows, attempts = call_database(engine, lease_messages, engine, body['sub_key'], body['max_messages'],
            body['max_len'], body['now_ms'], body['leased_until_ms'])

        out_rows:'anylist' = []

        for row in rows:
            row_values = row._asdict()
            out_rows.append(row_values)

        out_attempts:'anylist' = []

        for message_id, attempt in attempts.items():
            out_attempts.append([message_id, attempt])

        out = {
            'rows': out_rows,
            'attempts': out_attempts,
        }
        return out

# ################################################################################################################################

    def audit(self, body:'anydict') -> 'anydict':
        """ Writes the audit events of one item, and returns the ID that the database gave each of them, in their order.
        """
        item = AuditItem()
        item.events = batch_from_wire(body['events'])

        event_count = len(item.events)
        self.audit_queue.write(item, weight=event_count, is_urgent=False)

        event_ids:'intlist' = []

        for pending in item.events:
            event_ids.append(pending.event_id)

        out = {'event_ids': event_ids}
        return out

# ################################################################################################################################

    def _write_audit_batch(self, batch:'anylist') -> 'None':
        """ Commits the audit events of the items of one batch in one transaction, which stores the ID of each event in it.
        """
        events:'pending_event_list' = []

        for item in batch:
            events.extend(item.events)

        _ = self.audit_log.commit_batch(events)

# ################################################################################################################################

    def get_handlers(self) -> 'strcalldict':
        out:'strcalldict' = {
            ItemKind.Publish: self.publish,
            ItemKind.Ack: self.ack,
            ItemKind.Lease: self.lease,
            ItemKind.Audit: self.audit,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

def run_writer(listen_fd:'int') -> 'None':
    """ Serves the workers on the listening socket that the arbiter holds, until the process is terminated.
    Each transaction takes its turn in the queue of its SQLite file, in the place of the writer process that the caller
    bound, because the workers write their subscriptions, their admin operations, the cleanup and the audit events
    of other writers to the same files.
    """
    handlers = WriterHandlers()

    server = WriterServer(listen_fd, handlers.get_handlers())
    server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################
