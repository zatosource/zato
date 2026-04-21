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

import errno
import os
import socket
import stat
import sys
import time

from zato.common.util.platform_ import is_posix
from zato.server.ext.zunicorn import util
from zato.server.ext.zunicorn.six import string_types


class BaseSocket:

    def __init__(self, address, conf, log, fd=None):
        self.log = log
        self.conf = conf

        self.cfg_addr = address
        if fd is None:
            sock = socket.socket(self.FAMILY, socket.SOCK_STREAM)
            bound = False
        else:
            sock = socket.fromfd(fd, self.FAMILY, socket.SOCK_STREAM)
            os.close(fd)
            bound = True

        self.sock = self.set_options(sock, bound=bound)

    def __str__(self):
        return "<socket %d>" % self.sock.fileno()

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def set_options(self, sock, bound=False):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if (self.conf.reuse_port
            and hasattr(socket, 'SO_REUSEPORT')):  # pragma: no cover
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except socket.error as err:
                if err.errno not in (errno.ENOPROTOOPT, errno.EINVAL):
                    raise
        if not bound:
            self.bind(sock)
        sock.setblocking(0)

        # make sure that the socket can be inherited
        if hasattr(sock, "set_inheritable"):
            sock.set_inheritable(True)

        sock.listen(self.conf.backlog)
        return sock

    def bind(self, sock):
        sock.bind(self.cfg_addr)

    def close(self):
        if self.sock is None:
            return

        try:
            self.sock.close()
        except socket.error as e:
            self.log.info("Error while closing socket %s", str(e))

        self.sock = None


class TCPSocket(BaseSocket):

    FAMILY = socket.AF_INET

    def __str__(self):
        if self.conf.is_ssl:
            scheme = "https"
        else:
            scheme = "http"

        addr = self.sock.getsockname()
        return "%s://%s:%d" % (scheme, addr[0], addr[1])

    def set_options(self, sock, bound=False):
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return super(TCPSocket, self).set_options(sock, bound=bound)


class TCP6Socket(TCPSocket):

    FAMILY = socket.AF_INET6

    def __str__(self):
        (host, port, _, _) = self.sock.getsockname()
        return "http://[%s]:%d" % (host, port)


class UnixSocket(BaseSocket):

    # This is POSIX-only
    if is_posix:
        FAMILY = socket.AF_UNIX
    else:
        FAMILY = None

    def __init__(self, addr, conf, log, fd=None):
        if fd is None:
            try:
                st = os.stat(addr)
            except OSError as e:
                if e.args[0] != errno.ENOENT:
                    raise
            else:
                if stat.S_ISSOCK(st.st_mode):
                    os.remove(addr)
                else:
                    raise ValueError("%r is not a socket" % addr)
        super(UnixSocket, self).__init__(addr, conf, log, fd=fd)

    def __str__(self):
        return "unix:%s" % self.cfg_addr

    def bind(self, sock):
        old_umask = os.umask(self.conf.umask)
        sock.bind(self.cfg_addr)
        util.chown(self.cfg_addr, self.conf.uid, self.conf.gid)
        os.umask(old_umask)


def _sock_type(addr):
    if isinstance(addr, tuple):
        if util.is_ipv6(addr[0]):
            sock_type = TCP6Socket
        else:
            sock_type = TCPSocket
    elif isinstance(addr, string_types):
        sock_type = UnixSocket
    else:
        raise TypeError("Unable to create socket from: %r" % addr)
    return sock_type


def create_sockets(conf, log, fds=None):
    """
    Create a new socket for the configured addresses or file descriptors.

    If a configured address is a tuple then a TCP socket is created.
    If it is a string, a Unix socket is created. Otherwise, a TypeError is
    raised.
    """
    listeners = []

    # get it only once
    laddr = conf.address

    # check ssl config early to raise the error on startup
    # only the certfile is needed since it can contains the keyfile
    if conf.certfile and not os.path.exists(conf.certfile):
        raise ValueError('certfile "%s" does not exist' % conf.certfile)

    if conf.keyfile and not os.path.exists(conf.keyfile):
        raise ValueError('keyfile "%s" does not exist' % conf.keyfile)

    # sockets are already bound
    if fds is not None:
        for fd in fds:
            sock = socket.fromfd(fd, socket.AF_UNIX, socket.SOCK_STREAM)
            sock_name = sock.getsockname()
            sock_type = _sock_type(sock_name)
            listener = sock_type(sock_name, conf, log, fd=fd)
            listeners.append(listener)

        return listeners

    # no sockets is bound, first initialization of gunicorn in this env.
    for addr in laddr:
        sock_type = _sock_type(addr)
        sock = None
        for i in range(5):
            try:
                sock = sock_type(addr, conf, log)
            except socket.error as e:
                if e.args[0] == errno.EADDRINUSE:
                    log.error("Connection in use: %s", str(addr))
                if e.args[0] == errno.EADDRNOTAVAIL:
                    log.error("Invalid address: %s", str(addr))
                if i < 5:
                    msg = "connection to {addr} failed: {error}"
                    log.debug(msg.format(addr=str(addr), error=str(e)))
                    log.error("Retrying in 1 second.")
                    time.sleep(1)
            else:
                break

        if sock is None:
            log.error("Can't connect to %s", str(addr))
            sys.exit(1)

        listeners.append(sock)

    return listeners


def close_sockets(listeners, unlink=True):
    for sock in listeners:
        sock_name = sock.getsockname()
        sock.close()
        if unlink and _sock_type(sock_name) is UnixSocket:
            os.unlink(sock_name)
