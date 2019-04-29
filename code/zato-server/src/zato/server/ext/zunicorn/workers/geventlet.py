# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

from functools import partial
import errno
import sys

try:
    import eventlet
except ImportError:
    raise RuntimeError("You need eventlet installed to use this worker.")

# validate the eventlet version
if eventlet.version_info < (0, 9, 7):
    raise RuntimeError("You need eventlet >= 0.9.7")


from eventlet import hubs, greenthread
from eventlet.greenio import GreenSocket
from eventlet.hubs import trampoline
from eventlet.wsgi import ALREADY_HANDLED as EVENTLET_ALREADY_HANDLED
import greenlet

from zato.server.ext.zunicorn.http.wsgi import sendfile as o_sendfile
from zato.server.ext.zunicorn.workers.base_async import AsyncWorker

def _eventlet_sendfile(fdout, fdin, offset, nbytes):
    while True:
        try:
            return o_sendfile(fdout, fdin, offset, nbytes)
        except OSError as e:
            if e.args[0] == errno.EAGAIN:
                trampoline(fdout, write=True)
            else:
                raise


def _eventlet_serve(sock, handle, concurrency):
    """
    Serve requests forever.

    This code is nearly identical to ``eventlet.convenience.serve`` except
    that it attempts to join the pool at the end, which allows for gunicorn
    graceful shutdowns.
    """
    pool = eventlet.greenpool.GreenPool(concurrency)
    server_gt = eventlet.greenthread.getcurrent()

    while True:
        try:
            conn, addr = sock.accept()
            gt = pool.spawn(handle, conn, addr)
            gt.link(_eventlet_stop, server_gt, conn)
            conn, addr, gt = None, None, None
        except eventlet.StopServe:
            sock.close()
            pool.waitall()
            return


def _eventlet_stop(client, server, conn):
    """
    Stop a greenlet handling a request and close its connection.

    This code is lifted from eventlet so as not to depend on undocumented
    functions in the library.
    """
    try:
        try:
            client.wait()
        finally:
            conn.close()
    except greenlet.GreenletExit:
        pass
    except Exception:
        greenthread.kill(server, *sys.exc_info())


def patch_sendfile():
    from zato.server.ext.zunicorn.http import wsgi

    if o_sendfile is not None:
        setattr(wsgi, "sendfile", _eventlet_sendfile)


class EventletWorker(AsyncWorker):

    def patch(self):
        hubs.use_hub()
        eventlet.monkey_patch(os=False)
        patch_sendfile()

    def is_already_handled(self, respiter):
        if respiter == EVENTLET_ALREADY_HANDLED:
            raise StopIteration()
        else:
            return super(EventletWorker, self).is_already_handled(respiter)

    def init_process(self):
        super(EventletWorker, self).init_process()
        self.patch()

    def handle_quit(self, sig, frame):
        eventlet.spawn(super(EventletWorker, self).handle_quit, sig, frame)

    def handle_usr1(self, sig, frame):
        eventlet.spawn(super(EventletWorker, self).handle_usr1, sig, frame)

    def timeout_ctx(self):
        return eventlet.Timeout(self.cfg.keepalive or None, False)

    def handle(self, listener, client, addr):
        if self.cfg.is_ssl:
            client = eventlet.wrap_ssl(client, server_side=True,
                                       **self.cfg.ssl_options)

        super(EventletWorker, self).handle(listener, client, addr)

    def run(self):
        acceptors = []
        for sock in self.sockets:
            gsock = GreenSocket(sock)
            gsock.setblocking(1)
            hfun = partial(self.handle, gsock)
            acceptor = eventlet.spawn(_eventlet_serve, gsock, hfun,
                                      self.worker_connections)

            acceptors.append(acceptor)
            eventlet.sleep(0.0)

        while self.alive:
            self.notify()
            eventlet.sleep(1.0)

        self.notify()
        try:
            with eventlet.Timeout(self.cfg.graceful_timeout) as t:
                for a in acceptors:
                    a.kill(eventlet.StopServe())
                for a in acceptors:
                    a.wait()
        except eventlet.Timeout as te:
            if te != t:
                raise
            for a in acceptors:
                a.kill()
