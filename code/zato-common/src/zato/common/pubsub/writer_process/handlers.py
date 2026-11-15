# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The items that the pub/sub writer process runs for the workers. Publications and acknowledgements go through
# the one PubSubWriter of the process, whose commit queue gathers the items of every worker into shared transactions,
# and each lease runs in a transaction of its own, as it does in a worker. The writer process holds the only
# connection that writes these items to the SQLite file.

# Zato
from zato.common.db_env.engine import call_database, set_process_queue
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.writes import new_pending_ack, new_pending_publication, PubSubWriter
from zato.common.pubsub.writer_process.frames import ItemKind
from zato.common.pubsub.writer_process.server import WriterServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.db_env.process_queue import ProcessQueue
    from zato.common.typing_ import anydict, anylist, strcalldict

    ProcessQueue = ProcessQueue
    anydict = anydict
    anylist = anylist
    strcalldict = strcalldict

# ################################################################################################################################
# ################################################################################################################################

class WriterHandlers:
    """ Runs the publications, acknowledgements and leases that the workers send to the writer process.
    """

    def __init__(self) -> 'None':
        self.writer = PubSubWriter()

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

    def get_handlers(self) -> 'strcalldict':
        out:'strcalldict' = {
            ItemKind.Publish: self.publish,
            ItemKind.Ack: self.ack,
            ItemKind.Lease: self.lease,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

def run_writer(listen_fd:'int', process_queue:'ProcessQueue') -> 'None':
    """ Serves the workers on the listening socket that the arbiter holds, until the process is terminated.
    Each transaction takes its turn in the queue of the pub/sub file, in the place of the writer process,
    because the workers write their subscriptions, their admin operations and the cleanup to the same file.
    """
    engine = get_pubsub_engine()
    set_process_queue(engine, process_queue)

    handlers = WriterHandlers()

    server = WriterServer(listen_fd, handlers.get_handlers())
    server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################
