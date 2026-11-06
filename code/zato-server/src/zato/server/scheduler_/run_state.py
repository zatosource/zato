# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from datetime import datetime
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# Zato
from zato.common.api import SCHEDULER
from zato.common.pubsub.sql.generation import PubSubReplaced

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.common_db.store import SharedObjectStore
    from zato.common.typing_ import anydict, stranydict, strnone, strset

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    SharedObjectStore = SharedObjectStore
    stranydict = stranydict
    strnone = strnone
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Object_Type   = 'scheduler.job'
    Key_Last_Slot = 'last_slot'
    Key_Run_Count = 'run_count'

# The errors after which this server cannot confirm that it is still the active one
_not_active_errors = (PubSubReplaced, SQLAlchemyError, OSError)

# ################################################################################################################################
# ################################################################################################################################

class ClaimResult(NamedTuple):
    """ The decision whether this server runs one firing of a job.
    """
    is_claimed: 'bool'
    outcome: 'str'
    reason: 'str'

# A run that this server claimed has no outcome until the service completes.
_claimed = ClaimResult(True, '', '')

# ################################################################################################################################
# ################################################################################################################################

def _new_data(last_slot:'strnone', run_count:'int') -> 'anydict':
    """ Builds the document of a job's run state.
    """
    out = {
        ModuleCtx.Key_Last_Slot: last_slot,
        ModuleCtx.Key_Run_Count: run_count,
    }

    return out

# ################################################################################################################################

def _is_slot_claimed(data:'anydict', nominal_slot:'datetime') -> 'bool':
    """ Whether a slot is at or before the latest slot that any server claimed.
    """
    last_slot = data[ModuleCtx.Key_Last_Slot]

    if last_slot is None:
        out = False
    else:
        out = datetime.fromisoformat(last_slot) >= nominal_slot

    return out

# ################################################################################################################################
# ################################################################################################################################

class SchedulerRunState:
    """ The run state of each scheduler job in the common database - the latest slot that any server claimed and
    the number of runs claimed so far. A server runs a firing only after it claimed it here, so each slot of
    a schedule runs once across all the servers that schedule the job.
    """

    def __init__(self, shared_objects:'SharedObjectStore') -> 'None':
        self.shared_objects = shared_objects

# ################################################################################################################################

    def _claim_scheduled(self, job_name:'str', nominal_slot:'datetime') -> 'ClaimResult':
        """ Claims one slot of a job's schedule, unless any server claimed that slot or a later one already.
        """
        slot_iso = nominal_slot.isoformat()

        while True:

            current = self.shared_objects.get(ModuleCtx.Object_Type, job_name)

            # A job that never ran has no run state yet ..
            if current is None:
                version = None
                run_count = 0

            # .. a slot that a server claimed already is not run again ..
            elif _is_slot_claimed(current.data, nominal_slot):
                last_slot = current.data[ModuleCtx.Key_Last_Slot]
                reason = f'Slot {slot_iso} is not later than the last claimed slot {last_slot}'
                out = ClaimResult(False, SCHEDULER.OUTCOME.SKIPPED_ALREADY_RUN, reason)
                return out

            # .. otherwise, the claim continues from the state that was read ..
            else:
                version = current.version
                run_count = current.data[ModuleCtx.Key_Run_Count]

            data = _new_data(slot_iso, run_count + 1)

            # .. the claim succeeds only if no other writer changed the state since it was read ..
            if self.shared_objects.compare_and_set(ModuleCtx.Object_Type, job_name, data, version):
                return _claimed

            # .. and after a conflict, the state is read again, which tells whether the slot was claimed in the meantime.
            logger.info('Run state of job `%s` changed during the claim of slot %s, reading it again', job_name, slot_iso)

# ################################################################################################################################

    def _claim_forced(self, job_name:'str') -> 'ClaimResult':
        """ Counts a run that is outside the schedule, which keeps the job's last claimed slot as it is.
        """
        while True:

            current = self.shared_objects.get(ModuleCtx.Object_Type, job_name)

            if current is None:
                version = None
                data = _new_data(None, 1)
            else:
                version = current.version
                last_slot = current.data[ModuleCtx.Key_Last_Slot]
                run_count = current.data[ModuleCtx.Key_Run_Count]
                data = _new_data(last_slot, run_count + 1)

            if self.shared_objects.compare_and_set(ModuleCtx.Object_Type, job_name, data, version):
                return _claimed

            logger.info('Run state of job `%s` changed during the count of a forced run, reading it again', job_name)

# ################################################################################################################################

    def claim(self, job_name:'str', nominal_fire_time_iso:'str') -> 'ClaimResult':
        """ Claims one firing of a job. A firing with a nominal slot belongs to the schedule, and one without it
        is a forced run or a callback job.
        """
        try:
            if nominal_fire_time_iso:
                nominal_slot = datetime.fromisoformat(nominal_fire_time_iso)
                out = self._claim_scheduled(job_name, nominal_slot)
            else:
                out = self._claim_forced(job_name)

        # A server that was replaced, or that cannot reach the common database, does not run the job,
        # because the active server may be running it at the same time.
        except _not_active_errors as e:
            reason = f'Run state could not be claimed: {e}'
            out = ClaimResult(False, SCHEDULER.OUTCOME.SKIPPED_NOT_ACTIVE, reason)

        return out

# ################################################################################################################################

    def get_reload_state(self, job_names:'strset') -> 'stranydict':
        """ Returns the run state of each defined job, by its name, and deletes the run state of jobs
        that are no longer defined.
        """
        out:'stranydict' = {}

        for item in self.shared_objects.list(ModuleCtx.Object_Type):

            if item.name in job_names:
                out[item.name] = item.data
            else:
                _ = self.shared_objects.delete(ModuleCtx.Object_Type, item.name)
                logger.info('Deleted the run state of job `%s`, which is no longer defined', item.name)

        return out

# ################################################################################################################################
# ################################################################################################################################
