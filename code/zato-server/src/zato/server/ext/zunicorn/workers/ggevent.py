# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
BELOW IS THE ORIGINAL LICENSE ON WHICH THIS SOFTWARE IS BASED.

2009-2018 (c) Benoît Chesneau <benoitc@e-engura.org>
2009-2015 (c) Paul J. Davis <paul.joseph.davis@gmail.com>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

# flake8: noqa

from datetime import datetime
from functools import partial
from traceback import format_exc
import errno
import os
import sys
import time

_socket = __import__("socket")

# workaround on osx, disable kqueue
if sys.platform == "darwin":
    os.environ['EVENT_NOKQUEUE'] = "1"

try:
    import gevent
except ImportError:
    raise RuntimeError("You need gevent installed to use this worker.")
from gevent.pool import Pool
from gevent.server import StreamServer
from gevent.socket import wait_write, socket
from gevent import pywsgi

from zato.common.api import OS_Env
from zato.common.util.platform_ import is_windows
from zato.server.ext.zunicorn import SERVER_SOFTWARE
from zato.server.ext.zunicorn.http.wsgi import base_environ
from zato.server.ext.zunicorn.workers.base_async import AsyncWorker
from zato.server.ext.zunicorn.http.wsgi import sendfile as o_sendfile
from zato.server.ext.zunicorn.util import is_forking

def _gevent_sendfile(fdout, fdin, offset, nbytes):
    while True:
        try:
            return o_sendfile(fdout, fdin, offset, nbytes)
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                wait_write(fdout)
            else:
                raise

def patch_sendfile():
    from zato.server.ext.zunicorn.http import wsgi

    if o_sendfile is not None:
        setattr(wsgi, "sendfile", _gevent_sendfile)


class GeventWorker(AsyncWorker):

    server_class = None
    wsgi_handler = None

    def patch(self):
        from gevent import monkey
        monkey.noisy = False

        os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

        # if the new version is used make sure to patch subprocess
        if gevent.version_info[0] == 0:
            monkey.patch_all()
        else:
            monkey.patch_all(subprocess=True)

        # monkey patch sendfile to make it none blocking
        patch_sendfile()

        # patch sockets
        sockets = []
        for s in self.sockets:
            if sys.version_info[0] == 3:
                sockets.append(socket(s.FAMILY, _socket.SOCK_STREAM,
                    fileno=s.sock.fileno()))
            else:
                sockets.append(socket(s.FAMILY, _socket.SOCK_STREAM,
                    _sock=s))
        self.sockets = sockets

    def notify(self):
        super(GeventWorker, self).notify()
        if self.ppid != os.getppid():

            # We have forked only if we can fork on this system and if memory profiling is not enabled.
            needs_fork = is_forking and (not os.environ.get(OS_Env.Zato_Enable_Memory_Profiler))

            if needs_fork:
                self.log.info("Parent changed, shutting down: %s", self)
                sys.exit(0)

    def timeout_ctx(self):
        return gevent.Timeout(self.cfg.keepalive, False)

    def run(self):
        servers = []
        ssl_args = {}

        if self.cfg.is_ssl:
            ssl_args = dict(server_side=True, **self.cfg.ssl_options)

        for s in self.sockets:
            s.setblocking(1)
            pool = Pool(self.worker_connections)
            if self.server_class is not None:
                environ = base_environ(self.cfg)
                environ.update({
                    "wsgi.multithread": True,
                    "SERVER_SOFTWARE": SERVER_SOFTWARE,
                })
                server = self.server_class(
                    s, application=self.wsgi, spawn=pool, log=self.log,
                    handler_class=self.wsgi_handler, environ=environ,
                    **ssl_args)
            else:
                hfun = partial(self.handle, s)
                server = StreamServer(s, handle=hfun, spawn=pool, **ssl_args)

            server.start()
            servers.append(server)

        try:

            while self.alive:
                self.notify()
                gevent.sleep(1.0)

            # Stop accepting requests
            for server in servers:
                if hasattr(server, 'close'):  # gevent 1.0
                    server.close()
                if hasattr(server, 'kill'):  # gevent < 1.0
                    server.kill()

            # Handle current requests until graceful_timeout
            ts = time.time()
            while time.time() - ts <= self.cfg.graceful_timeout:
                accepting = 0
                for server in servers:
                    if server.pool.free_count() != server.pool.size:
                        accepting += 1

                # if no server is accepting a connection, we can exit
                if not accepting:
                    return

                self.notify()
                gevent.sleep(1.0)

            # Force kill all active the handlers
            self.log.warning("Worker graceful timeout (pid:%s)" % self.pid)
            for server in servers:
                server.stop(timeout=1)

        except KeyboardInterrupt:
            if is_windows:
                sys.exit(0)
            else:
                raise

        except Exception as e:
            self.log.warning('Exception in GeventWorker.run (pid:%s) -> `%s`', self.pid, format_exc())

    def handle(self, listener, client, addr):
        # Connected socket timeout defaults to socket.getdefaulttimeout().
        # This forces to blocking mode.
        client.setblocking(1)
        super(GeventWorker, self).handle(listener, client, addr)

    def handle_request(self, listener_name, req, sock, addr):
        try:
            super(GeventWorker, self).handle_request(listener_name, req, sock,
                                                     addr)
        except gevent.GreenletExit:
            pass
        except SystemExit:
            pass

    def handle_quit(self, sig, frame):
        # Move this out of the signal handler so we can use
        # blocking calls. See #1126
        gevent.spawn(super(GeventWorker, self).handle_quit, sig, frame)

    def handle_usr1(self, sig, frame):
        # Make the gevent workers handle the usr1 signal
        # by deferring to a new greenlet. See #1645
        gevent.spawn(super(GeventWorker, self).handle_usr1, sig, frame)

    def init_process(self):
        # monkey patch here
        self.patch()

        # reinit the hub
        from gevent import hub
        hub.reinit()

        # then initialize the process
        super(GeventWorker, self).init_process()


class GeventResponse:

    status = None
    headers = None
    sent = None

    def __init__(self, status, headers, clength):
        self.status = status
        self.headers = headers
        self.sent = clength


class PyWSGIHandler(pywsgi.WSGIHandler):

    def log_request(self):
        start = datetime.fromtimestamp(self.time_start)
        finish = datetime.fromtimestamp(self.time_finish)
        response_time = finish - start
        resp_headers = getattr(self, 'response_headers', {})
        resp = GeventResponse(self.status, resp_headers, self.response_length)
        if hasattr(self, 'headers'):
            req_headers = self.headers.items()
        else:
            req_headers = []
        self.server.log.access(resp, req_headers, self.environ, response_time)

    def get_environ(self):
        env = super(PyWSGIHandler, self).get_environ()
        env['gunicorn.sock'] = self.socket
        env['RAW_URI'] = self.path
        return env


class PyWSGIServer(pywsgi.WSGIServer):
    pass


class GeventPyWSGIWorker(GeventWorker):
    "The Gevent StreamServer based workers."
    server_class = PyWSGIServer
    wsgi_handler = PyWSGIHandler
