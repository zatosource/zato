# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Lock

# Zato
from zato.common.db_env.commit_ticket import CommitTicket
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.db_env.commit_ticket import commit_ticket_list
    from zato.common.typing_ import any_, anylist, callable_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    callable_ = callable_
    commit_ticket_list = commit_ticket_list

# ################################################################################################################################
# ################################################################################################################################

# How many commits are in progress at once unless a queue is told otherwise - a database with a single writer runs one.
Default_Max_In_Flight = 1

# ################################################################################################################################
# ################################################################################################################################

class CommitQueue:
    """ Writes the items of concurrent synchronous callers in shared transactions. A caller that arrives
    while fewer than the maximum number of commits are in progress commits its own item at once. Callers that arrive
    when all of them are in progress wait, and once a commit completes, one of the waiting callers commits
    the items of the next batch. The next batch takes the urgent items first and the other items after them,
    each kind in the order of arrival, for as long as the total weight of the batch is within the maximum per commit.
    The writer of a batch stores in each item what its caller receives, and an exception
    from a commit reaches every caller whose item was part of it.
    """

    def __init__(
        self,
        *,
        write_batch:'callable_',
        max_weight:'int',
        max_in_flight:'int' = Default_Max_In_Flight,
        ) -> 'None':

        self.write_batch = write_batch
        self.max_weight = max_weight
        self.max_in_flight = max_in_flight

        # Guards the waiting tickets and the number of commits in progress
        self._lock = Lock()

        # The tickets of the callers waiting for a commit, oldest first
        self._waiting:'commit_ticket_list' = []

        # How many commits are in progress, or have a caller chosen to run them
        self._in_flight = 0

# ################################################################################################################################

    def write(self, item:'any_', *, weight:'int', is_urgent:'bool') -> 'None':
        """ Writes one item, in a commit of its own or shared with other callers.
        """
        ticket = CommitTicket(item, weight, is_urgent)

        # The caller commits at once if fewer than the maximum number of commits are in progress ..
        with self._lock:
            if self._in_flight >= self.max_in_flight:
                self._waiting.append(ticket)
                is_runner = False
            else:
                self._in_flight += 1
                ticket.batch = [ticket]
                ticket.has_started = True
                is_runner = True

        # .. otherwise, it waits until its item is written or until it is to run the next commit itself ..
        if not is_runner:
            try:
                _ = ticket.ready.wait()
                is_runner = self._start(ticket)
            except BaseException:
                self._abandon(ticket)
                raise

        # .. a caller that runs a commit writes the items of its whole batch ..
        if is_runner:
            self._commit(ticket)

        # .. and the outcome of the commit is the caller's own.
        if ticket.exception is not None:
            raise ticket.exception

# ################################################################################################################################

    def _start(self, ticket:'CommitTicket') -> 'bool':
        """ Returns whether the caller of a ticket that was woken up is to run the next commit,
        rather than having had its item written by another caller.
        """
        with self._lock:
            if ticket.batch is None:
                out = False
            else:
                ticket.has_started = True
                out = True

        return out

# ################################################################################################################################

    def _commit(self, runner:'CommitTicket') -> 'None':
        """ Writes the items of a batch in one transaction, passes the queue on to the next batch
        and releases the callers of this one.
        """
        tickets = cast_('commit_ticket_list', runner.batch)

        batch:'anylist' = []

        for ticket in tickets:
            batch.append(ticket.item)

        # Write all the items of the batch ..
        try:
            _ = self.write_batch(batch)

        # .. if the commit fails, each of its callers receives the exception ..
        except BaseException as e:
            for ticket in tickets:
                ticket.exception = e

        # .. the next batch starts before the callers of this one resume ..
        self._hand_off()

        # .. and the callers of this one are released.
        for ticket in tickets:
            ticket.ready.set()

# ################################################################################################################################

    def _take_batch(self) -> 'commit_ticket_list':
        """ Takes the tickets of the next commit out of the waiting ones, the urgent ones first and the others
        after them, until the next ticket would take the total weight above the maximum. The first ticket
        is always taken, whatever its weight.
        """
        urgent:'commit_ticket_list' = []
        other:'commit_ticket_list' = []

        for ticket in self._waiting:
            if ticket.is_urgent:
                urgent.append(ticket)
            else:
                other.append(ticket)

        out:'commit_ticket_list' = []
        total_weight = 0

        for ticket in urgent + other:

            # A ticket that does not fit waits for the next commit, and so do all the tickets behind it ..
            if out:
                if total_weight + ticket.weight > self.max_weight:
                    break

            out.append(ticket)
            total_weight += ticket.weight

        # .. and the tickets taken are not waiting anymore.
        for ticket in out:
            self._waiting.remove(ticket)

        return out

# ################################################################################################################################

    def _hand_off(self) -> 'None':
        """ Passes the commit that ended on to a waiting caller, which is to run the next batch,
        or ends it if no caller is waiting.
        """
        with self._lock:

            # Nothing is waiting, so the next caller to arrive commits at once ..
            if not self._waiting:
                self._in_flight -= 1
                runner = None

            # .. otherwise, a caller of the next batch is to commit it.
            else:
                batch = self._take_batch()

                runner = batch[0]
                runner.batch = batch

        if runner:
            runner.ready.set()

# ################################################################################################################################

    def _abandon(self, ticket:'CommitTicket') -> 'None':
        """ Takes the ticket of a caller that stopped waiting out of the queue. An item that is still waiting
        is not written, and if the caller had been chosen to run the next commit, its batch goes back
        to the front of the queue for the next caller to commit. An item that is part of a commit
        another caller runs is written regardless.
        """
        needs_hand_off = False

        with self._lock:

            # The item has not been taken by any commit yet ..
            if ticket in self._waiting:
                self._waiting.remove(ticket)

            # .. or its caller was to commit a batch it never began.
            elif ticket.batch is not None and not ticket.has_started:
                others = ticket.batch[1:]
                self._waiting[0:0] = others

                ticket.batch = None
                needs_hand_off = True

        if needs_hand_off:
            self._hand_off()

# ################################################################################################################################
# ################################################################################################################################
