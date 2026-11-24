# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The runtime of the worker process of a server. It binds the worker to the shared region and to the control channel
# of its arbiter before the server starts, loads its configuration after the mark of the config process, reports ready,
# records its heartbeat, applies the events and answers the queries that the arbiter relays, forwards the services
# that change configuration to the config process, and drains the worker on the drain command of the arbiter
# or on its own SIGTERM.

# stdlib
import os
import signal
from logging import getLogger
from time import monotonic

# gevent
from gevent import get_hub, getcurrent, signal_handler, sleep, spawn
from gevent.event import Event

# Zato
from zato.common.config_dispatcher import handle_config_event
from zato.common.pubsub.sql.replaced import set_on_replaced
from zato.common.typing_ import cast_
from zato.server.arbiter_config import ModuleCtx as ArbiterCtx
from zato.server.config_forward import apply_forward_result, new_forward_body
from zato.server.config_runner import bind_config_runner
from zato.server.control.client import ControlClient
from zato.server.outgoing_region import bind_outgoing_control, handle_outgoing_query
from zato.server.reload_retry import next_reload_retry_delay, Reload_Retry_Initial_Seconds
from zato.server.worker_liveness import reopen_worker_logs, write_heartbeat

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import any_, anydict
    from zato.server.arbiter_config import WorkerContext
    from zato.server.base.parallel import ParallelServer
    from zato.server.control.envelope import Message
    from zato.server.service import Service
    from zato_ipc_core.zato_ipc_core import SharedRegion
    from zato_server_core.zato_server_core import HTTPServer

    any_ = any_
    anydict = anydict
    Greenlet = Greenlet
    HTTPServer = HTTPServer
    Message = Message
    ParallelServer = ParallelServer
    Service = Service
    SharedRegion = SharedRegion
    WorkerContext = WorkerContext

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often a draining worker checks whether its requests in progress completed, in seconds
    Drain_Check_Interval = 0.05

# ################################################################################################################################
# ################################################################################################################################

class WorkerRuntime:
    """ The binding of the worker process to its arbiter, to the shared region of its server and to its server object.
    """

    def __init__(self, region:'SharedRegion', ctx:'WorkerContext') -> 'None':
        self.region = region
        self.ctx = ctx

        self.slot = ctx.slot
        self.generation = ctx.generation

        # The server is assigned when the worker binds it, and the listener once the worker serves requests
        self._server:'ParallelServer | None' = None
        self.http_server:'HTTPServer | None' = None

        # The greenlet that reads the control channel and applies the events, assigned when the worker binds its server
        self.reader:'Greenlet | None' = None

        # How many requests the worker is processing, which a drain waits for
        self.in_flight = 0

        # A drain runs once, and the main greenlet returns once it completed
        self.is_draining = False
        self.drained = Event()

        # The arbiter is told only once that another server took over the pub/sub database
        self.is_replaced_reported = False

        # One reload runs at a time, and the reloads requested while it runs are served by one more reload after it
        self.is_reloading = False
        self.is_reload_requested = False

        self.client = ControlClient(ctx.control_fd, ctx.body_dir, self.on_event, self.on_query, self.on_drain,
            self.on_reload, reopen_worker_logs)

        # A notice that another server took over may come from a thread of the pool, which hands it to this hub
        self.hub = get_hub()

# ################################################################################################################################

    @property
    def server(self) -> 'ParallelServer':
        out = cast_('ParallelServer', self._server)
        return out

# ################################################################################################################################

    def bind(self, server:'ParallelServer') -> 'None':
        """ Binds the worker to its region and to its arbiter before its server starts.
        """
        self._server = server
        server.worker = self

        # The control channel is read from now on, and the worker exits once the arbiter closes it ..
        reader = self.client.start()
        reader.link(self.on_control_closed)
        self.reader = reader

        # .. the heartbeat is recorded whenever the hub of the worker runs ..
        _ = spawn(self.write_heartbeats)

        # .. the queues of outgoing connections reach the config process ..
        bind_outgoing_control(self.client)

        # .. a worker that learns that this server is no longer the active one tells the arbiter ..
        set_on_replaced(self.on_replaced)

        # .. and the SIGTERM that an active-standby node sends to the process group drains the worker at once.
        _ = signal_handler(signal.SIGTERM, self.on_sigterm)

# ################################################################################################################################

    def request_load(self) -> 'str':
        """ Waits for the mark of the config process, after which no change is committed until the worker loaded
        its configuration, and returns the correlation ID of the load.
        """
        out = self.client.request_load()
        return out

# ################################################################################################################################

    def on_started(self, load_cid:'str') -> 'None':
        """ Reports ready once the server loaded its configuration, after which the arbiter relays to the worker the events
        that it held for it and the configuration events of the worker reach the config process, and lets the config process
        resume its changes.
        """
        server = self.server

        server.config_dispatcher.relay = self.client.publish

        # The services that change configuration run in the config process from now on, while those that the startup
        # of the worker invoked deployed what each process deploys for itself, such as the files of the pickup directory.
        bind_config_runner(self.forward_change)

        self.client.report_ready()
        self.client.report_load_done(load_cid)

        logger.info('Worker, generation %s, PID %s is ready', self.generation, os.getpid())

# ################################################################################################################################

    def serve(self, http_server:'HTTPServer') -> 'None':
        """ Serves requests until a drain closes the listening socket, and returns once the drain completed
        and the server released its resources.
        """
        self.http_server = http_server
        http_server.serve_forever()

        _ = self.drained.wait()
        _ = self.server.release_resources()

# ################################################################################################################################

    def write_heartbeats(self) -> 'None':
        while True:
            write_heartbeat(self.region)
            sleep(ArbiterCtx.Heartbeat_Interval)

# ################################################################################################################################

    def on_event(self, message:'Message') -> 'None':
        """ Applies an event that the config process published.
        """
        body:'anydict' = message.body

        # An event that cannot be applied is logged, and the events that follow it are applied
        try:
            _ = handle_config_event(body, self.server.config_manager)
        except Exception:
            logger.exception('Could not apply an event of the config process -> %s', message.cid)

# ################################################################################################################################

    def on_query(self, body:'anydict') -> 'None':
        """ Answers a query of the config process, which is an action on the delivery of an outgoing queue.
        """
        handle_outgoing_query(self.server.pubsub_push_delivery, body)

# ################################################################################################################################

    def forward_change(self, invoker:'Service', service:'Service', channel:'str', request_ctx:'anydict') -> 'None':
        """ Runs a service that changes configuration in the config process, and returns once the worker applied the events
        of the change, because the arbiter delivers its result after them.
        """
        # A service that an event invokes applies in this worker a change that the config process committed already,
        # and the greenlet that applies the events would wait for a result that only it reads.
        if getcurrent() is self.reader:
            invoker._run_handle(service, channel, request_ctx)
            return

        body = new_forward_body(service, channel, request_ctx)
        result = self.client.forward(body)

        apply_forward_result(service, result)

# ################################################################################################################################

    def on_reload(self) -> 'None':
        """ Reads the configuration again, because the config process may have committed a change whose event it never sent.
        """
        self.is_reload_requested = True

        # The reload in progress is followed by one more, which reads the configuration of this request
        if self.is_reloading:
            return

        _ = spawn(self.reload)

# ################################################################################################################################

    def reload(self) -> 'None':
        """ Reads the configuration again after the mark of the config process, as many times as it was requested,
        and again after a growing delay after each reload that failed, until a reload succeeds or the worker drains.
        """
        self.is_reloading = True
        retry_delay = Reload_Retry_Initial_Seconds

        while self.is_reload_requested and not self.is_draining:
            self.is_reload_requested = False

            load_cid = self.request_load()

            try:
                self.server.reload_config()
            except Exception:
                logger.exception('Could not reload the configuration of the worker, reloading it again in %ss', retry_delay)
                self.is_reload_requested = True
                is_failed = True
            else:
                is_failed = False

            self.client.report_load_done(load_cid)

            # A file deployed in a process that terminated before it relayed the deployment is in effect here as well
            self.server.deploy_pickup_dir(is_relayed=True)

            # The next reload after a failed one waits, so that a database that cannot be reached is not polled at once
            if is_failed:
                sleep(retry_delay)
                retry_delay = next_reload_retry_delay(retry_delay)
            else:
                retry_delay = Reload_Retry_Initial_Seconds

        self.is_reloading = False

# ################################################################################################################################

    def on_drain(self) -> 'None':
        _ = spawn(self.drain)

# ################################################################################################################################

    def on_sigterm(self) -> 'None':
        _ = spawn(self.drain)

# ################################################################################################################################

    def drain(self) -> 'None':
        """ Stops accepting connections, waits for the requests in progress and pauses every subscriber between two of its
        batches, all within the grace period of the arbiter. Every audit event was committed by the call that wrote it.
        """
        if self.is_draining:
            return

        self.is_draining = True
        logger.info('Worker is draining')

        # A worker that serves no requests yet has nothing to complete ..
        if self.http_server is None:
            os._exit(ArbiterCtx.Exit_Code_OK)

        # .. otherwise the listening socket closes, so that no new connection is accepted ..
        self.http_server.stop()

        # .. the requests in progress complete ..
        deadline = monotonic() + ArbiterCtx.Request_Drain_Period

        while self.in_flight:
            if monotonic() >= deadline:
                logger.warning('Worker stops with %s requests in progress', self.in_flight)
                break
            sleep(ModuleCtx.Drain_Check_Interval)

        # .. and a message whose delivery is in progress remains in its queue for the next worker.
        self.server.pubsub_push_delivery.pause_all(ArbiterCtx.Delivery_Pause_Period)

        self.drained.set()

# ################################################################################################################################

    def on_control_closed(self, _reader:'Greenlet') -> 'None':
        """ Exits once the arbiter closed the control channel, which it does only when it terminated.
        """
        logger.warning('Worker exits because its arbiter terminated')
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
