# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The runtime of the config process of a server. The process loads the whole configuration, as a worker does,
# but it receives no messages. It runs the services that change configuration, those that the worker forwards
# and those that its own startup invokes, one change at a time, and the events of each change reach the worker
# through the arbiter. It sends the worker a mark between two changes when the worker loads its configuration.

# stdlib
import os
import signal
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import get_hub, signal_handler, spawn
from gevent.event import Event

# Zato
from zato.common.audit_log.buffer import flush_all_buffers
from zato.common.config_dispatcher import handle_config_event
from zato.common.db_env.connection import SQLite_Busy_Timeout_Ms
from zato.common.db_env.engine import bind_process_queues
from zato.common.db_env.process_queue import get_deadline_seconds
from zato.common.pubsub.sql.replaced import set_on_replaced
from zato.common.typing_ import cast_
from zato.server.arbiter_config import ModuleCtx as ArbiterCtx
from zato.server.config_forward import describe_error, invoke_forwarded
from zato.server.config_gate import ChangeGate
from zato.server.config_runner import bind_config_runner
from zato.server.control.client import ControlClient
from zato.server.control.envelope import MessageType, new_message
from zato.server.outgoing_region import bind_outgoing_control
from zato.server.worker_liveness import reopen_worker_logs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import any_, anydict, strintdict
    from zato.server.arbiter_config import WorkerContext
    from zato.server.base.parallel import ParallelServer
    from zato.server.control.envelope import Message
    from zato.server.service import Service
    from zato_ipc_core.zato_ipc_core import SharedRegion

    any_ = any_
    anydict = anydict
    Greenlet = Greenlet
    Message = Message
    ParallelServer = ParallelServer
    Service = Service
    SharedRegion = SharedRegion
    strintdict = strintdict
    WorkerContext = WorkerContext

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ConfigRuntime:
    """ The binding of the config process to its arbiter, to the shared region of its server and to its server object.
    """

    def __init__(self, region:'SharedRegion', ctx:'WorkerContext', queue_by_path:'strintdict') -> 'None':

        # The queue of the shared region of each SQLite file of the server, by the real path of the file
        self.region = region
        self.ctx = ctx
        self.queue_by_path = queue_by_path

        self.slot = ctx.slot
        self.generation = ctx.generation

        # The server is assigned when the process binds it
        self._server:'ParallelServer | None' = None

        # A drain runs once, and the main greenlet returns once it completed
        self.is_draining = False
        self.drained = Event()

        # The arbiter is told only once that another server took over the pub/sub database
        self.is_replaced_reported = False

        self.client = ControlClient(ctx.control_fd, ctx.body_dir, self.on_event, self.on_query, self.on_drain,
            self.on_reload, reopen_worker_logs)

        self.client.handlers[MessageType.Forward] = self.on_forward
        self.client.handlers[MessageType.Load_Request] = self.on_load_request
        self.client.handlers[MessageType.Load_Done] = self.on_load_done
        self.client.handlers[MessageType.Worker_Gone] = self.on_worker_gone
        self.client.handlers[MessageType.Loading_State] = self.on_loading_state

        # Each change runs only while the worker does not load its configuration
        self.gate = ChangeGate(self.send_mark)

        # A notice that another server took over may come from a thread of the pool, which hands it to this hub
        self.hub = get_hub()

# ################################################################################################################################

    @property
    def server(self) -> 'ParallelServer':
        out = cast_('ParallelServer', self._server)
        return out

# ################################################################################################################################

    def bind(self, server:'ParallelServer') -> 'None':
        """ Binds the process to its region and to its arbiter before its server starts.
        """
        self._server = server
        server.worker = self

        # The writes of the process to each SQLite file take turns with those of the worker ..
        deadline_seconds = get_deadline_seconds(SQLite_Busy_Timeout_Ms)
        bind_process_queues(self.region, self.region.config_place, deadline_seconds, self.queue_by_path)

        # .. the control channel is read from now on, and the process exits once the arbiter closes it ..
        reader = self.client.start()
        reader.link(self.on_control_closed)

        # .. the worker pauses the delivery of an outgoing queue that a change renames or deletes on request ..
        bind_outgoing_control(self.client)

        # .. a process that learns that this server is no longer the active one tells the arbiter ..
        set_on_replaced(self.on_replaced)

        # .. and the SIGTERM that an active-standby node sends to the process group drains the process at once.
        _ = signal_handler(signal.SIGTERM, self.on_sigterm)

# ################################################################################################################################

    def on_started(self) -> 'None':
        """ Reports ready once the server loaded its configuration, after which the arbiter starts the worker
        and the events of each change reach it.
        """
        self.server.config_dispatcher.relay = self.client.publish

        # Each service that changes configuration runs through the gate from now on, while those that the startup
        # of the process invoked ran before the worker could load, because the worker does not start before this process is ready
        # and the loads that its predecessor left reach it only once it is ready.
        bind_config_runner(self.run_change)

        self.client.report_ready()

        logger.info('Config process, generation %s, PID %s is ready', self.generation, os.getpid())

# ################################################################################################################################

    def serve(self) -> 'None':
        """ Returns once a drain completed and the server released its resources.
        """
        _ = self.drained.wait()
        _ = self.server.release_resources()

# ################################################################################################################################

    def run_change(self, invoker:'Service', service:'Service', channel:'str', request_ctx:'anydict') -> 'None':
        """ Runs a service that changes configuration once the worker does not load its configuration.
        """
        _ = self.gate.run(invoker._run_handle, service, channel, request_ctx)

# ################################################################################################################################

    def on_forward(self, message:'Message') -> 'None':
        _ = spawn(self.run_forward, message)

# ################################################################################################################################

    def run_forward(self, message:'Message') -> 'None':
        """ Runs an invocation that the worker forwarded and sends its result, which the arbiter delivers to the worker
        after the events of the change.
        """
        body:'anydict' = message.body

        try:
            result = invoke_forwarded(self.server, body)
        except Exception as e:
            logger.warning('Forwarded invocation of `%s` from slot %s failed -> %s', body['name'], message.slot, format_exc())
            result = {'error': describe_error(e)}

        response = new_message(MessageType.Forward_Result, result, message.cid, message.slot)
        self.client.send(response)

# ################################################################################################################################

    def send_mark(self, slot:'int', cid:'str') -> 'None':
        message = new_message(MessageType.Mark, None, cid, slot)
        self.client.send(message)

# ################################################################################################################################

    def request_worker_reload(self) -> 'None':
        """ Asks the arbiter for a reload of the worker, after a change that reached the ODB without its events.
        """
        message = new_message(MessageType.Reload, None)
        self.client.send(message)

# ################################################################################################################################

    def on_load_request(self, message:'Message') -> 'None':
        _ = spawn(self.gate.request_load, message.slot, message.cid)

# ################################################################################################################################

    def on_load_done(self, message:'Message') -> 'None':
        self.gate.on_load_done(message.slot, message.cid)

# ################################################################################################################################

    def on_worker_gone(self, message:'Message') -> 'None':
        slot:'int' = message.body
        self.gate.on_worker_gone(slot)

# ################################################################################################################################

    def on_loading_state(self, message:'Message') -> 'None':
        """ Takes over the loads that were in progress when the previous config process exited.
        """
        loading:'dict[int, str]' = {}

        for slot, cid in message.body:
            loading[slot] = cid

        self.gate.set_loading(loading)

# ################################################################################################################################

    def on_event(self, message:'Message') -> 'None':
        """ Applies an event of the worker, which is a change that does not pass through the config process.
        """
        body:'anydict' = message.body

        # An event that cannot be applied is logged, and the events that follow it are applied
        try:
            _ = handle_config_event(body, self.server.config_manager)
        except Exception:
            logger.exception('Could not apply an event of the worker -> %s', message.cid)

# ################################################################################################################################

    def on_query(self, body:'anydict') -> 'any_':
        """ The arbiter sends no query to the config process.
        """
        logger.warning('Ignoring a query in the config process -> %s', body)

# ################################################################################################################################

    def on_reload(self) -> 'None':
        """ The arbiter sends no reload to the config process, whose configuration is the one that it committed.
        """
        logger.warning('Ignoring a reload in the config process')

# ################################################################################################################################

    def on_drain(self) -> 'None':
        _ = spawn(self.drain)

# ################################################################################################################################

    def on_sigterm(self) -> 'None':
        _ = spawn(self.drain)

# ################################################################################################################################

    def drain(self) -> 'None':
        """ Waits for the change in progress and writes the buffered audit events, within the grace period of the arbiter.
        """
        if self.is_draining:
            return

        self.is_draining = True
        logger.info('Config process is draining')

        # A change in progress completes, and no other change begins after it ..
        _ = self.gate.lock.acquire()

        # .. and the audit events that wait in a buffer are written before the process exits.
        flush_all_buffers()

        self.drained.set()

# ################################################################################################################################

    def on_control_closed(self, _reader:'Greenlet') -> 'None':
        """ Exits once the arbiter closed the control channel, which it does only when it terminated.
        """
        logger.warning('Config process exits because its arbiter terminated')
        os._exit(ArbiterCtx.Exit_Code_Parent_Gone)

# ################################################################################################################################

    def on_replaced(self) -> 'None':
        _ = self.hub.loop.run_callback_threadsafe(self.report_replaced)

# ################################################################################################################################

    def report_replaced(self) -> 'None':
        if self.is_replaced_reported:
            return

        self.is_replaced_reported = True
        self.client.report_replaced()

# ################################################################################################################################
# ################################################################################################################################
