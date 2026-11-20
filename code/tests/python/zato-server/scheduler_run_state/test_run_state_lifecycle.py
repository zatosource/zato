# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from contextlib import closing
from datetime import datetime

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.db_env.engine import new_zato_engine
from zato.common.api import SCHEDULER
from zato.common.common_db.schema import metadata
from zato.common.common_db.store import SharedObjectStore
from zato.common.ext.bunch import Bunch
from zato.common.odb.model import Base, Job, Service as ServiceModel
from zato.common.typing_ import cast_
from zato.server.scheduler_.client import ModuleCtx as ClientCtx, SchedulerClient
from zato.server.scheduler_.run_state import ModuleCtx as RunStateCtx, SchedulerRunState
from zato.server.service.internal.scheduler import _create_edit, _SchedulerAdmin, Delete
from zato.common.test.direct_sql.seed import seed_config_objects

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from redis import Redis
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, anylist, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    Engine = Engine
    Path = Path
    Redis = Redis
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Job_Name = 'test.run_state.lifecycle.job'
    Other_Job_Name = 'test.run_state.lifecycle.other'
    Renamed_Job_Name = 'test.run_state.lifecycle.renamed'

    Service_Name = 'test.run_state.lifecycle.service'
    Service_Impl_Name = 'test.run_state.lifecycle.Service'

    First_Slot = '2026-11-14T10:00:00+00:00'
    First_Entry = '1763114400000-0'

    Start_Date = '2026-11-14T10:00:00'
    Interval_Minutes = 1

    Cid = 'test-run-state-lifecycle'

    Event_Run_State_Deleted = 'run_state_deleted'
    Event_Command = 'command'

# ################################################################################################################################
# ################################################################################################################################

class _RecordingStore(SharedObjectStore):
    """ A store that records each deletion of a run state, along with whether the ODB held the job at that time.
    """
    def __init__(self, engine:'Engine', odb_session:'sessionmaker', events:'anylist') -> 'None':
        super().__init__()
        self._engine = engine
        self._odb_session = odb_session
        self._events = events

    def delete(self, object_type:'str', name:'str') -> 'bool':

        with closing(self._odb_session()) as session:
            job_count = session.query(Job).filter_by(name=name).count()

        self._events.append((ModuleCtx.Event_Run_State_Deleted, name, job_count))

        out = super().delete(object_type, name)
        return out

# ################################################################################################################################

class _RecordingScheduler:
    """ A scheduler client that records each command it would send.
    """
    def __init__(self, events:'anylist') -> 'None':
        self._events = events

    def create_job(self, job_id:'int', job_data:'anydict') -> 'None':
        self._events.append((ModuleCtx.Event_Command, 'create_job', job_id))

    def edit_job(self, job_id:'int', job_data:'anydict') -> 'None':
        self._events.append((ModuleCtx.Event_Command, 'edit_job', job_id))

    def delete_job(self, job_id:'int') -> 'None':
        self._events.append((ModuleCtx.Event_Command, 'delete_job', job_id))

# ################################################################################################################################

class _Server:
    """ The attributes of a server that the scheduler services use.
    """
    def __init__(self, run_state:'SchedulerRunState', scheduler:'_RecordingScheduler') -> 'None':
        self._scheduler_run_state = run_state
        self._scheduler = scheduler
        self.service_store = Bunch(name_to_impl_name={ModuleCtx.Service_Name: ModuleCtx.Service_Impl_Name})

# ################################################################################################################################

class _ServiceCall:
    """ The attributes of a scheduler service instance that its handler uses.
    """
    _service_by_name = _SchedulerAdmin._service_by_name

    def __init__(self, server:'_Server', odb_session:'sessionmaker', input:'Bunch') -> 'None':
        self.server = server
        self.odb = Bunch(session=odb_session)
        self.request = Bunch(input=input, payload=dict(input))
        self.response = Bunch(payload=Bunch())
        self.logger = logger
        self.cid = ModuleCtx.Cid

# ################################################################################################################################

class _Environment:
    """ The ODB, the Zato database and the recorders of one test.
    """
    def __init__(self, tmp_path:'Path') -> 'None':

        odb_engine = new_zato_engine(f'sqlite:///{os.path.join(tmp_path, "config.db")}')
        Base.metadata.create_all(odb_engine)
        self.odb_session = sessionmaker(bind=odb_engine)

        database_engine = new_zato_engine(f'sqlite:///{os.path.join(tmp_path, "zato.db")}')
        metadata.create_all(database_engine)

        self.events:'anylist' = []
        self.store = _RecordingStore(database_engine, self.odb_session, self.events)
        self.run_state = SchedulerRunState(self.store)
        self.server = _Server(self.run_state, _RecordingScheduler(self.events))

        with closing(self.odb_session()) as session:
            service = ServiceModel()
            service.name = ModuleCtx.Service_Name
            service.is_active = True
            service.impl_name = ModuleCtx.Service_Impl_Name
            service.is_internal = False
            seed_config_objects(session, [service])
            session.commit()

    def add_job(self, name:'str') -> 'int':
        """ Commits a job to the ODB and returns its ID.
        """
        with closing(self.odb_session()) as session:
            service = session.query(ServiceModel).filter_by(name=ModuleCtx.Service_Name).one()

            job = Job()
            job.name = name
            job.is_active = True
            job.job_type = SCHEDULER.JOB_TYPE.INTERVAL_BASED
            job.start_date = datetime.fromisoformat(ModuleCtx.Start_Date)
            job.service = service
            seed_config_objects(session, [job])
            session.commit()

            out = cast_('int', job.id)

        return out

    def call(self, input:'anydict') -> '_ServiceCall':
        """ Returns the attributes of a service instance invoked with the given input.
        """
        out = _ServiceCall(self.server, self.odb_session, Bunch(input))
        return out

    def get_run_state_names(self) -> 'strlist':
        """ Returns the names of all the jobs that the Zato database holds a run state for.
        """
        out = sorted(item.name for item in self.store.list(RunStateCtx.Object_Type))
        return out

# ################################################################################################################################

class _RecordingClient(SchedulerClient):
    """ A scheduler client that records the payload of each command in place of sending it.
    """
    def __init__(self, redis_conn:'Redis') -> 'None':
        super().__init__(redis_conn)
        self.payloads:'anylist' = []

    def invoke(self, command:'str', payload:'any_'=None, needs_reply:'bool'=False) -> 'anydict | None':
        self.payloads.append((command, payload))
        return None

# ################################################################################################################################

class _ODBAdapter:
    """ An ODB adapter that runs one action of another server during its read of the jobs.
    """
    def __init__(self, jobs:'anydict', during_read:'any_') -> 'None':
        self._jobs = jobs
        self._during_read = during_read

    def get_scheduler_jobs(self) -> 'anydict':
        self._during_read()
        return self._jobs

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def env(tmp_path:'Path') -> '_Environment':
    out = _Environment(tmp_path)
    return out

# ################################################################################################################################

def _edit_input(job_id:'int', name:'str') -> 'anydict':
    out = {
        'id': job_id,
        'name': name,
        'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
        'service': ModuleCtx.Service_Name,
        'is_active': True,
        'start_date': ModuleCtx.Start_Date,
        'extra': '',
        'minutes': ModuleCtx.Interval_Minutes,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_reload_keeps_the_run_state_of_a_job_its_read_did_not_return(env:'_Environment') -> 'None':

    # Two jobs run, and the ODB read of a reload returns only one of them, because the other was created after the read ..
    _ = env.run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    _ = env.run_state.claim(ModuleCtx.Other_Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    reload_state = env.run_state.get_reload_state({ModuleCtx.Job_Name})

    # .. so the reload sends the run state of the job it read and deletes nothing.
    assert sorted(reload_state) == [ModuleCtx.Job_Name]
    assert env.get_run_state_names() == sorted([ModuleCtx.Job_Name, ModuleCtx.Other_Job_Name])

# ################################################################################################################################

def test_the_deletion_of_a_job_removes_its_run_state_after_the_commit(env:'_Environment') -> 'None':

    job_id = env.add_job(ModuleCtx.Job_Name)
    _ = env.run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)
    _ = env.run_state.claim(ModuleCtx.Other_Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    Delete.handle(env.call({'id': job_id})) # type: ignore[arg-type]

    # The run state goes once the ODB no longer holds the job, and before the scheduler receives the deletion ..
    assert env.events == [
        (ModuleCtx.Event_Run_State_Deleted, ModuleCtx.Job_Name, 0),
        (ModuleCtx.Event_Command, 'delete_job', job_id),
    ]

    # .. and the run state of any other job stays.
    assert env.get_run_state_names() == [ModuleCtx.Other_Job_Name]

# ################################################################################################################################

def test_the_rename_of_a_job_removes_the_run_state_of_its_previous_name(env:'_Environment') -> 'None':

    job_id = env.add_job(ModuleCtx.Job_Name)
    _ = env.run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    _create_edit(env.call(_edit_input(job_id, ModuleCtx.Renamed_Job_Name)), 'edit')

    # No job created later under the previous name continues its runs, and the deletion follows the commit of the rename.
    assert env.events == [
        (ModuleCtx.Event_Run_State_Deleted, ModuleCtx.Job_Name, 0),
        (ModuleCtx.Event_Command, 'edit_job', job_id),
    ]
    assert env.get_run_state_names() == []

# ################################################################################################################################

def test_an_edit_that_keeps_the_name_keeps_the_run_state(env:'_Environment') -> 'None':

    job_id = env.add_job(ModuleCtx.Job_Name)
    _ = env.run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    _create_edit(env.call(_edit_input(job_id, ModuleCtx.Job_Name)), 'edit')

    assert env.events == [(ModuleCtx.Event_Command, 'edit_job', job_id)]
    assert env.get_run_state_names() == [ModuleCtx.Job_Name]

# ################################################################################################################################

def test_the_commands_of_all_servers_carry_increasing_numbers(redis_conn:'Redis') -> 'None':

    # Two servers share one Redis ..
    first = _RecordingClient(redis_conn)
    second = _RecordingClient(redis_conn)

    first.create_job(1, {})
    second.edit_job(1, {})
    first.delete_job(1)

    # .. so the scheduler orders their commands by one counter.
    sequences = [first.payloads[0][1]['sequence'], second.payloads[0][1]['sequence'], first.payloads[1][1]['sequence']]

    assert sequences == [1, 2, 3]
    assert redis_conn.get(ClientCtx.Sequence_Key) == '3'

# ################################################################################################################################

def test_a_reload_draws_its_number_before_its_odb_read(env:'_Environment', redis_conn:'Redis') -> 'None':

    reloading = _RecordingClient(redis_conn)
    other = _RecordingClient(redis_conn)

    jobs = {1: {'name': ModuleCtx.Job_Name}}
    _ = env.run_state.claim(ModuleCtx.Job_Name, ModuleCtx.First_Slot, ModuleCtx.First_Entry)

    # Another server creates a job while the reload reads the ODB ..
    adapter = _ODBAdapter(jobs, lambda: other.create_job(2, {}))
    reloading.reload(adapter, env.run_state, needs_reply=False)

    command, reload_payload = reloading.payloads[0]
    _, create_payload = other.payloads[0]

    # .. so the creation carries a number above that of the reload, which therefore never removes the job ..
    assert command == 'reload'
    assert reload_payload['sequence'] < create_payload['sequence']

    # .. and the reload sends the run state of each job it read.
    reloaded_job = reload_payload['jobs'][0]
    assert reloaded_job['current_run'] == 1
    assert reloaded_job['last_slot_iso'] == ModuleCtx.First_Slot

# ################################################################################################################################
# ################################################################################################################################
