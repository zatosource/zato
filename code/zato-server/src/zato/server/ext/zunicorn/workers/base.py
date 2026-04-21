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
import os
from random import randint
import signal
from ssl import SSLError
import sys
import time
import traceback

from zato.common.util.platform_ import is_posix
from zato.server.ext.zunicorn import six
from zato.server.ext.zunicorn import util
from zato.server.ext.zunicorn.workers.workertmp import PassThroughTmp, WorkerTmp
from zato.server.ext.zunicorn.reloader import reloader_engines
from zato.server.ext.zunicorn.http.errors import (
    InvalidHeader, InvalidHeaderName, InvalidRequestLine, InvalidRequestMethod,
    InvalidHTTPVersion, LimitRequestLine, LimitRequestHeaders,
)
from zato.server.ext.zunicorn.http.errors import InvalidProxyLine, ForbiddenProxyRequest
from zato.server.ext.zunicorn.http.errors import InvalidSchemeHeaders
from zato.server.ext.zunicorn.http.wsgi import default_environ, Response
from zato.server.ext.zunicorn.six import MAXSIZE


class Worker:

    if is_posix:
        SIGNALS = [getattr(signal, "SIG%s" % x)for x in "ABRT HUP QUIT INT TERM USR1 USR2 WINCH CHLD".split()]
    else:
        SIGNALS = []

    PIPE = []

    def __init__(self, age, ppid, sockets, app, timeout, cfg, log):
        """\
        This is called pre-fork so it shouldn't do anything to the
        current process. If there's a need to make process wide
        changes you'll want to do that in ``self.init_process()``.
        """
        self.age = age
        self.pid = "[booting]"
        self.ppid = ppid
        self.sockets = sockets
        self.app = app
        self.timeout = timeout
        self.cfg = cfg
        self.booted = False
        self.aborted = False
        self.reloader = None

        self.nr = 0
        jitter = randint(0, cfg.max_requests_jitter)
        self.max_requests = cfg.max_requests + jitter or MAXSIZE
        self.alive = True
        self.log = log

        # Under POSIX, we use a real class that communicates with arbiter via temporary files.
        # On other systems, this is a pass-through class that does nothing.
        worker_tmp_class = WorkerTmp if is_posix else PassThroughTmp
        self.tmp = worker_tmp_class(cfg)

    def __str__(self):
        return "<Worker %s>" % self.pid

    def notify(self):
        """\
        Your worker subclass must arrange to have this method called
        once every ``self.timeout`` seconds. If you fail in accomplishing
        this task, the master process will murder your workers.
        """
        self.tmp.notify()

    def run(self):
        """\
        This is the mainloop of a worker process. You should override
        this method in a subclass to provide the intended behaviour
        for your particular evil schemes.
        """
        raise NotImplementedError()

    def init_process(self):
        """\
        If you override this method in a subclass, the last statement
        in the function should be to call this method with
        super(MyWorkerClass, self).init_process() so that the ``run()``
        loop is initiated.
        """
        # Reseed the random number generator
        util.seed()

        # set environment' variables
        if self.cfg.env:
            for k, v in self.cfg.env.items():
                os.environ[k] = v

        if is_posix:
            util.set_owner_process(self.cfg.uid, self.cfg.gid, initgroups=self.cfg.initgroups)

            # Reseed the random number generator
            util.seed()

            # For waking ourselves up
            self.PIPE = os.pipe()
            for p in self.PIPE:
                util.set_non_blocking(p)
                util.close_on_exec(p)

            # Prevent fd inheritance
            for s in self.sockets:
                util.close_on_exec(s)

            util.close_on_exec(self.tmp.fileno())
            self.log.close_on_exec()

            self.init_signals()

        # start the reloader
        if self.cfg.reload:
            def changed(fname):
                self.log.info("Worker reloading: %s modified", fname)
                self.alive = False
                self.cfg.worker_int(self)
                time.sleep(0.1)
                sys.exit(0)

            reloader_cls = reloader_engines[self.cfg.reload_engine]
            self.reloader = reloader_cls(extra_files=self.cfg.reload_extra_files,
                                         callback=changed)
            self.reloader.start()

        self.load_wsgi()
        self.cfg.post_worker_init(self)

        # Enter main run loop
        self.booted = True
        self.run()

    def load_wsgi(self):
        try:
            self.wsgi = self.app.wsgi()
        except SyntaxError as e:
            if not self.cfg.reload:
                raise

            self.log.exception(e)

            # fix from PR #1228
            # storing the traceback into exc_tb will create a circular reference.
            # per https://docs.python.org/2/library/sys.html#sys.exc_info warning,
            # delete the traceback after use.
            try:
                _, exc_val, exc_tb = sys.exc_info()
                self.reloader.add_extra_file(exc_val.filename)

                tb_string = six.StringIO()
                traceback.print_tb(exc_tb, file=tb_string)
                self.wsgi = util.make_fail_app(tb_string.getvalue())
            finally:
                del exc_tb

    def init_signals(self):

        # reset signaling
        for s in self.SIGNALS:
            signal.signal(s, signal.SIG_DFL)

        # init new signaling
        signal.signal(signal.SIGQUIT, self.handle_quit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_quit)
        signal.signal(signal.SIGWINCH, self.handle_winch)
        signal.signal(signal.SIGUSR1, self.handle_usr1)
        signal.signal(signal.SIGABRT, self.handle_abort)

        # Don't let SIGTERM and SIGUSR1 disturb active requests
        # by interrupting system calls
        if hasattr(signal, 'siginterrupt'):  # python >= 2.6
            signal.siginterrupt(signal.SIGTERM, False)
            signal.siginterrupt(signal.SIGUSR1, False)

        if hasattr(signal, 'set_wakeup_fd'):
            signal.set_wakeup_fd(self.PIPE[1])

    def handle_usr1(self, sig, frame):
        self.log.reopen_files()

    def handle_exit(self, sig, frame):
        self.alive = False

    def handle_quit(self, sig, frame):
        self.alive = False
        try:
            self.app.zato_wsgi_app.cleanup_on_stop()
        except Exception:
            # At this poing logging may not be available anymore hence we are using print() instead.
            from traceback import format_exc
            print('Exception in handle_quit', format_exc())
        finally:
            time.sleep(0.1)
            sys.exit(0)

    def handle_abort(self, sig, frame):
        self.alive = False
        self.cfg.worker_abort(self)
        sys.exit(1)

    def handle_error(self, req, client, addr, exc):
        request_start = datetime.now()
        addr = addr or ('', -1)  # unix socket case
        if isinstance(exc, (InvalidRequestLine, InvalidRequestMethod,
                InvalidHTTPVersion, InvalidHeader, InvalidHeaderName,
                LimitRequestLine, LimitRequestHeaders,
                InvalidProxyLine, ForbiddenProxyRequest,
                InvalidSchemeHeaders,
                SSLError)):

            status_int = 400
            reason = "Bad Request"

            if isinstance(exc, InvalidRequestLine):
                mesg = "Invalid Request Line '%s'" % str(exc)
            elif isinstance(exc, InvalidRequestMethod):
                mesg = "Invalid Method '%s'" % str(exc)
            elif isinstance(exc, InvalidHTTPVersion):
                mesg = "Invalid HTTP Version '%s'" % str(exc)
            elif isinstance(exc, (InvalidHeaderName, InvalidHeader,)):
                mesg = "%s" % str(exc)
                if not req and hasattr(exc, "req"):
                    req = exc.req  # for access log
            elif isinstance(exc, LimitRequestLine):
                mesg = "%s" % str(exc)
            elif isinstance(exc, LimitRequestHeaders):
                mesg = "Error parsing headers: '%s'" % str(exc)
            elif isinstance(exc, InvalidProxyLine):
                mesg = "'%s'" % str(exc)
            elif isinstance(exc, ForbiddenProxyRequest):
                reason = "Forbidden"
                mesg = "Request forbidden"
                status_int = 403
            elif isinstance(exc, InvalidSchemeHeaders):
                mesg = "%s" % str(exc)
            elif isinstance(exc, SSLError):
                reason = "Forbidden"
                mesg = "'%s'" % str(exc)
                status_int = 403

            msg = "Invalid request from ip={ip}: {error}"
            self.log.debug(msg.format(ip=addr[0], error=str(exc)))
        else:
            if hasattr(req, "uri"):
                self.log.exception("Error handling request %s", req.uri)
            status_int = 500
            reason = "Internal Server Error"
            mesg = ""

        if req is not None:
            request_time = datetime.now() - request_start
            environ = default_environ(req, client, self.cfg)
            environ['REMOTE_ADDR'] = addr[0]
            environ['REMOTE_PORT'] = str(addr[1])
            resp = Response(req, client, self.cfg)
            resp.status = "%s %s" % (status_int, reason)
            resp.response_length = len(mesg)
            self.log.access(resp, req, environ, request_time)

        try:
            util.write_error(client, status_int, reason, mesg)
        except:
            self.log.debug("Failed to send error message.")

    def handle_winch(self, sig, fname):
        # Ignore SIGWINCH in worker. Fixes a crash on OpenBSD.
        self.log.debug("worker: SIGWINCH ignored.")
