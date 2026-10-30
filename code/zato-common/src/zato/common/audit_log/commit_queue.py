# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from threading import Lock

# Zato
from zato.common.audit_log.commit_ticket import CommitTicket
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.buffer import pending_event_list, PendingEvent
    from zato.common.audit_log.commit_ticket import commit_ticket_list
    from zato.common.typing_ import callable_, intnone

    # Dummy assignments to satisfy type checkers
    callable_ = callable_
    commit_ticket_list = commit_ticket_list
    intnone = intnone
    pending_event_list = pending_event_list
    PendingEvent = PendingEvent

# ################################################################################################################################
# ################################################################################################################################

# The environment variable overriding how many events one group commit writes at most
Env_Commit_Max_Events = 'Zato_Audit_Log_Commit_Max_Events'

# How many events one group commit writes at most when the environment does not say otherwise
_default_commit_max_events = 500

# ################################################################################################################################
# ################################################################################################################################

def get_commit_max_events() -> 'int':
    """ Returns how many events one group commit writes at most.
    """
    if value := os.environ.get(Env_Commit_Max_Events, ''):
        out = int(value)
    else:
        out = _default_commit_max_events

    return out

# ################################################################################################################################
# ################################################################################################################################

class CommitQueue:
    """ Writes the events of concurrent synchronous callers in shared transactions. A caller that arrives
    while no commit is in progress commits its own event at once. Callers that arrive during a commit wait,
    and once the commit completes, the caller that has waited longest commits the events of all the waiting
    callers, up to the maximum per commit. Each caller receives the id of its own event, and an exception
    from a commit reaches every caller whose event was part of it.
    """

    def __init__(self, *, write_batch:'callable_', max_events:'int') -> 'None':
        self.write_batch = write_batch
        self.max_events = max_events

        # Guards the waiting tickets and the commit flag
        self._lock = Lock()

        # The tickets of the callers waiting for a commit, oldest first
        self._waiting:'commit_ticket_list' = []

        # Whether a commit is in progress or a caller has been chosen to run the next one
        self._is_committing = False

# ################################################################################################################################

    def write(self, pending:'PendingEvent') -> 'intnone':
        """ Writes one event, in a commit of its own or shared with other callers, and returns its id.
        """
        ticket = CommitTicket(pending)

        # The caller commits at once if no commit is in progress ..
        with self._lock:
            if self._is_committing:
                self._waiting.append(ticket)
                is_runner = False
            else:
                self._is_committing = True
                ticket.batch = [ticket]
                ticket.has_started = True
                is_runner = True

        # .. otherwise, it waits until its event is written or until it is to run the next commit itself ..
        if not is_runner:
            try:
                _ = ticket.ready.wait()
                is_runner = self._start(ticket)
            except BaseException:
                self._abandon(ticket)
                raise

        # .. a caller that runs a commit writes the events of its whole batch ..
        if is_runner:
            self._commit(ticket)

        # .. and the outcome of the commit is the caller's own.
        if ticket.exception is not None:
            raise ticket.exception

        out = ticket.event_id
        return out

# ################################################################################################################################

    def _start(self, ticket:'CommitTicket') -> 'bool':
        """ Returns whether the caller of a ticket that was woken up is to run the next commit,
        rather than having had its event written by another caller.
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
        """ Writes the events of a batch in one transaction, passes the queue on to the next batch
        and releases the callers of this one.
        """
        tickets = cast_('commit_ticket_list', runner.batch)

        batch:'pending_event_list' = []

        for ticket in tickets:
            batch.append(ticket.pending)

        # Write all the events of the batch ..
        try:
            _ = self.write_batch(batch)

        # .. if the commit fails, each of its callers receives the exception ..
        except BaseException as e:
            for ticket in tickets:
                ticket.exception = e

        # .. otherwise, each of them receives the id of its own event ..
        else:
            for ticket in tickets:
                ticket.event_id = ticket.pending.event_id

        # .. the next batch starts before the callers of this one resume ..
        self._hand_off()

        # .. and the callers of this one are released.
        for ticket in tickets:
            ticket.ready.set()

# ################################################################################################################################

    def _hand_off(self) -> 'None':
        """ Chooses the caller that has waited longest to run the next commit, or ends the commit
        in progress if no caller is waiting.
        """
        with self._lock:

            # Nothing is waiting, so the next caller to arrive commits at once ..
            if not self._waiting:
                self._is_committing = False
                runner = None

            # .. otherwise, the oldest waiting caller is to commit everything waiting, up to the maximum.
            else:
                batch = self._waiting[:self.max_events]
                del self._waiting[:self.max_events]

                runner = batch[0]
                runner.batch = batch

        if runner:
            runner.ready.set()

# ################################################################################################################################

    def _abandon(self, ticket:'CommitTicket') -> 'None':
        """ Takes the ticket of a caller that stopped waiting out of the queue. An event that is still waiting
        is not written, and if the caller had been chosen to run the next commit, its batch goes back
        to the front of the queue for the next caller to commit. An event that is part of a commit
        another caller runs is written regardless.
        """
        needs_hand_off = False

        with self._lock:

            # The event has not been taken by any commit yet ..
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
