# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.db_env.any_of import any_of
from zato.common.db_env.plain_sql import PlainStatement
from zato.common.pubsub.sql.payloads import drop_payloads, get_chunks, get_message_ids
from zato.common.pubsub.sql.schema import delivery_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.pubsub.sql.pending import pending_ack_list
    from zato.common.typing_ import anydict, anylist, intlist, strlist

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    pending_ack_list = pending_ack_list

# ################################################################################################################################
# ################################################################################################################################

# The subscriber column is concatenated with an empty string, which keeps the query planner from looking the rows up
# through an index of subscribers, whose queues may be deep, rather than through the index of messages.
_unindexed_sub_key = delivery_table.c.sub_key.concat('')

_ack_deliveries_query = select(delivery_table.c.id, delivery_table.c.sub_key, delivery_table.c.message_id)
_ack_deliveries_query_plain = PlainStatement(_ack_deliveries_query.where(and_(
    any_of(delivery_table.c.message_id, 'ack_message_ids'),
    any_of(_unindexed_sub_key, 'ack_sub_keys'),
)))

# A concurrent commit may have removed some of the rows first, so the statement returns those it removed.
_delivery_delete = delivery_table.delete().where(any_of(delivery_table.c.id, 'ack_delivery_ids'))
_delivery_delete_plain = PlainStatement(_delivery_delete.returning(delivery_table.c.id))

# ################################################################################################################################
# ################################################################################################################################

class AckDeletes:
    """ The removal of the delivery rows of acknowledgements, and of the payloads that no subscriber needs anymore,
    in the transaction of a group commit.
    """

    def _resolve_ack_message_ids(self, connection:'Connection', acks:'pending_ack_list') -> 'anylist':
        """ Returns the primary keys of the messages of each acknowledgement, in the order of the acknowledgements,
        looking up the keys of those that were given public identifiers alone.
        """
        lookup_msg_ids:'strlist' = []

        for pending in acks:
            if pending.sequence_ids is None:
                lookup_msg_ids.extend(pending.msg_ids)

        if lookup_msg_ids:
            found = get_message_ids(connection, lookup_msg_ids)
        else:
            found = {}

        out:'anylist' = []

        for pending in acks:

            if pending.sequence_ids is None:
                message_ids:'intlist' = []

                for msg_id in pending.msg_ids:
                    if message_id := found.get(msg_id):
                        message_ids.append(message_id)

            else:
                message_ids = pending.sequence_ids

            out.append(message_ids)

        return out

# ################################################################################################################################

    def _delete_acks(self, connection:'Connection', acks:'pending_ack_list', ack_by_message_id:'anydict') -> 'None':
        """ Removes the delivery rows the acknowledgements are about and records each of their messages with the
        acknowledgement that its full delivery counts towards. A row that two acknowledgements of one commit are about
        counts towards the first of them, and a message counts towards the last acknowledgement that removed one
        of its rows, or, with no such acknowledgement, the first one that was about it.
        """
        message_ids_by_ack = self._resolve_ack_message_ids(connection, acks)

        all_message_ids:'anylist' = []
        sub_keys:'strlist' = []
        acked_pairs:'set[tuple[str, int]]' = set()

        for pending, message_ids in zip(acks, message_ids_by_ack):
            all_message_ids.extend(message_ids)

            if pending.sub_key not in sub_keys:
                sub_keys.append(pending.sub_key)

            for message_id in message_ids:
                acked_pairs.add((pending.sub_key, message_id))

        if not all_message_ids:
            return

        # Read the delivery rows of the acknowledged messages that belong to the acknowledging subscribers.
        # The query matches every subscriber of the commit with every message of the commit, so a row
        # of a subscriber that did not acknowledge that particular message is still pending and stays in place ..
        delivery_ids_by_pair:'anydict' = {}

        for chunk in get_chunks(all_message_ids):

            parameters = {
                'ack_message_ids': chunk,
                'ack_sub_keys': sub_keys,
            }

            for row in _ack_deliveries_query_plain.execute(connection, parameters):
                pair = (row.sub_key, row.message_id)

                if pair in acked_pairs:
                    delivery_ids_by_pair[pair] = row.id

        # .. remove them, in the order of their keys, so that concurrent commits lock them in the same order,
        # learning which of them this commit removed ..
        delivery_ids = sorted(delivery_ids_by_pair.values())
        removed_ids:'set[int]' = set()

        for chunk in get_chunks(delivery_ids):
            for row in _delivery_delete_plain.execute(connection, {'ack_delivery_ids': chunk}):
                removed_ids.add(row.id)

        # .. and assign each removed row to the acknowledgement that removed it.
        for pending, message_ids in zip(acks, message_ids_by_ack):
            for message_id in message_ids:

                pair = (pending.sub_key, message_id)
                delivery_id = delivery_ids_by_pair.pop(pair, None)

                if delivery_id in removed_ids:
                    pending.removed_count += 1
                    ack_by_message_id[message_id] = pending

                elif message_id not in ack_by_message_id:
                    ack_by_message_id[message_id] = pending

# ################################################################################################################################

    def _drop_payloads(self, connection:'Connection', ack_by_message_id:'anydict') -> 'None':
        """ Drops the payloads of the acknowledged messages that no subscriber needs anymore, each counting
        as fully delivered towards its acknowledgement.
        """
        message_ids = list(ack_by_message_id)

        for message_id in drop_payloads(connection, message_ids):
            pending = ack_by_message_id[message_id]
            pending.fully_delivered_count += 1

# ################################################################################################################################
# ################################################################################################################################
