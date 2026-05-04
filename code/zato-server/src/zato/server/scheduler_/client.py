# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import time
from uuid import uuid4

# redis
from redis import Redis

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Command_Stream = 'zato:scheduler:stream:command'
    Reply_Stream = 'zato:scheduler:stream:reply'
    Fire_Stream = 'zato:scheduler:stream:fire'
    Timeout_Stream = 'zato:scheduler:stream:timeout'
    Consumer_Group = 'server'
    Consumer_Name = 'server-0'
    Http_Base = 'http://127.0.0.1:35100'
    Reply_Timeout = 1.0

# ################################################################################################################################
# ################################################################################################################################

class SchedulerClient:
    """ Thin client that replaces the in-process PyO3 Scheduler.

    Write commands go via Redis Streams (XADD to the command stream).
    Read queries go via HTTP GET to the scheduler's actix-web API.
    """

    def __init__(self, redis_conn:'Redis | None'=None) -> 'None':
        if redis_conn:
            self.redis = redis_conn
        else:
            redis_host = os.environ.get('Zato_Scheduler_Redis_Host', 'localhost')
            redis_port = int(os.environ.get('Zato_Scheduler_Redis_Port', '6379'))
            redis_password = os.environ.get('Zato_Scheduler_Redis_Password', None)
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
            )

        self._ensure_reply_group()

# ################################################################################################################################

    def new_redis_conn(self) -> 'Redis':
        """ Returns a new Redis connection using the same config as this client. """
        return Redis(
            host=self.redis.connection_pool.connection_kwargs['host'],
            port=self.redis.connection_pool.connection_kwargs['port'],
            password=self.redis.connection_pool.connection_kwargs.get('password'),
            decode_responses=True,
        )

    def _ensure_reply_group(self) -> 'None':
        try:
            self.redis.xgroup_create(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, id='$', mkstream=True)
        except Exception as exc:
            if 'BUSYGROUP' in str(exc):
                pass
            else:
                raise

# ################################################################################################################################

    def invoke(self, command:'str', payload:'any_'=None, needs_reply:'bool'=False) -> 'anydict | None':
        """ Core method - XADDs a command to the scheduler stream.

        If needs_reply is True, blocks until the scheduler acks via the reply stream.
        """
        correlation_id = uuid4().hex
        payload_json = json.dumps(payload) if payload is not None else '{}'

        self.redis.xadd(ModuleCtx.Command_Stream, {
            'command': command,
            'correlation_id': correlation_id,
            'payload': payload_json,
        }, maxlen=100_000)

        if not needs_reply:
            return None

        deadline = time.monotonic() + ModuleCtx.Reply_Timeout

        while time.monotonic() < deadline:
            result = self.redis.xreadgroup(
                groupname=ModuleCtx.Consumer_Group,
                consumername=ModuleCtx.Consumer_Name,
                streams={ModuleCtx.Reply_Stream: '>'},
                count=10,
                block=1000,
            )

            if not result:
                continue

            for _stream_name, messages in result:
                for msg_id, fields in messages:
                    reply_corr = fields['correlation_id']
                    if reply_corr == correlation_id:
                        self.redis.xack(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, msg_id)
                        return {'status': fields['status']}

                    self.redis.xack(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, msg_id)

        logger.info('Timed out waiting for reply to command=%s correlation_id=%s', command, correlation_id)
        return {'status': 'timeout'}

# ################################################################################################################################

    def _http_get(self, path:'str', params:'anydict | None'=None) -> 'any_':
        """ Sends a GET request to the scheduler's HTTP API. """
        url = f'{ModuleCtx.Http_Base}{path}'
        response = requests.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        return response.json()

# ################################################################################################################################

    def start(self, config:'anydict') -> 'None':
        """ No-op - the scheduler binary is started externally. """
        pass

# ################################################################################################################################

    def stop(self, timeout_s:'float'=30.0) -> 'None':
        self.invoke('stop', needs_reply=True)

# ################################################################################################################################

    def create_job(self, job_id:'int', job_data:'anydict') -> 'None':
        job_data['id'] = job_id
        self.invoke('create_job', {'job_id': job_id, 'job_data': job_data})

# ################################################################################################################################

    def edit_job(self, job_id:'int', job_data:'anydict') -> 'None':
        job_data['id'] = job_id
        self.invoke('edit_job', {'job_id': job_id, 'job_data': job_data})

# ################################################################################################################################

    def delete_job(self, job_id:'int') -> 'None':
        self.invoke('delete_job', {'job_id': job_id})

# ################################################################################################################################

    def execute_job(self, job_id:'int') -> 'None':
        self.invoke('execute_job', {'job_id': job_id})

# ################################################################################################################################

    def mark_complete(self, job_id:'int', outcome:'str', duration_ms:'int', current_run:'int') -> 'None':
        self.invoke('mark_complete', {
            'job_id': job_id,
            'outcome': outcome,
            'duration_ms': duration_ms,
            'current_run': current_run,
        })

# ################################################################################################################################

    def append_log_entry(self, job_id:'int', current_run:'int', timestamp_iso:'str', level:'str', message:'str') -> 'None':
        self.invoke('append_log_entry', {
            'job_id': job_id,
            'current_run': current_run,
            'timestamp_iso': timestamp_iso,
            'level': level,
            'message': message,
        })

# ################################################################################################################################

    def reload(self, odb_adapter:'any_'=None) -> 'None':
        """ Loads all jobs from ODB via the adapter and sends them to the scheduler. """
        if odb_adapter is None:
            self.invoke('reload', {'jobs': []}, needs_reply=True)
            return

        raw_jobs = odb_adapter.get_scheduler_jobs()
        jobs = []
        for job_id, entry in raw_jobs.items():
            job = dict(entry)
            job['id'] = job_id
            jobs.append(job)

        self.invoke('reload', {'jobs': jobs}, needs_reply=True)

# ################################################################################################################################

    def get_job_summaries(self) -> 'anylist':
        return self._http_get('/api/get_job_summaries')

# ################################################################################################################################

    def get_timeline_events(self, max_events:'int'=1000) -> 'anylist':
        return self._http_get('/api/get_timeline_events', {'max_events': max_events})

# ################################################################################################################################

    def get_history_page(self, job_id:'int', offset:'int', limit:'int', outcomes:'any_') -> 'anydict':
        params = {
            'job_id': job_id,
            'offset': offset,
            'limit': limit,
        }
        if isinstance(outcomes, list):
            params['outcomes'] = ','.join(outcomes)
        elif isinstance(outcomes, str):
            params['outcomes'] = outcomes

        return self._http_get('/api/get_history_page', params)

# ################################################################################################################################

    def get_history_since(self, job_id:'int', since_iso:'str', outcomes:'any_', running_runs:'list | None'=None) -> 'anydict':
        params = {
            'job_id': job_id,
            'since_iso': since_iso,
        }
        if isinstance(outcomes, list):
            params['outcomes'] = ','.join(outcomes)
        elif isinstance(outcomes, str):
            params['outcomes'] = outcomes

        if running_runs:
            params['running_runs'] = ','.join(str(run) for run in running_runs)

        return self._http_get('/api/get_history_since', params)

# ################################################################################################################################

    def get_run_detail(self, job_id:'int', current_run:'int') -> 'anydict':
        return self._http_get('/api/get_run_detail', {'job_id': job_id, 'current_run': current_run})

# ################################################################################################################################

    def get_log_entries(self, job_id:'int', current_run:'int', since_idx:'int') -> 'anylist':
        return self._http_get('/api/get_log_entries', {
            'job_id': job_id,
            'current_run': current_run,
            'since_idx': since_idx,
        })

# ################################################################################################################################
# ################################################################################################################################
