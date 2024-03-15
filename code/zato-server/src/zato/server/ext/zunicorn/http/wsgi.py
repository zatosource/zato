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

import io
import logging
import os
import regex as re

from zato.server.ext.zunicorn import SERVER_SOFTWARE, util
from zato.server.ext.zunicorn._compat import unquote_to_wsgi_str
from zato.server.ext.zunicorn.http.message import HEADER_RE
from zato.server.ext.zunicorn.http.errors import InvalidHeader, InvalidHeaderName
from zato.server.ext.zunicorn.six import string_types, binary_type, reraise

try:
    # Python 3.3 has os.sendfile().
    from os import sendfile
except ImportError:
    try:
        from ._sendfile import sendfile
    except ImportError:
        sendfile = None

# Send files in at most 1GB blocks as some operating systems can have problems
# with sending files in blocks over 2GB.
BLKSIZE = 0x3FFFFFFF

HEADER_VALUE_RE = re.compile(r'[\x00-\x1F\x7F]')

log = logging.getLogger(__name__)


class FileWrapper:

    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        if hasattr(filelike, 'close'):
            self.close = filelike.close

    def __getitem__(self, key):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise IndexError

def base_environ(cfg, FileWrapper=FileWrapper, SERVER_SOFTWARE=SERVER_SOFTWARE):
    return {
        "wsgi.version": (1, 0),
        "wsgi.multithread": False,
        "wsgi.multiprocess": (cfg.workers > 1),
        "wsgi.run_once": False,
        "wsgi.file_wrapper": FileWrapper,
        "SERVER_SOFTWARE": SERVER_SOFTWARE
    }


def default_environ(req, sock, cfg, base_environ=base_environ):
    env = base_environ(cfg)
    env.update({
        "wsgi.input": req.body,
        "gunicorn.socket": sock,
        "REQUEST_METHOD": req.method,
        "QUERY_STRING": req.query,
        "RAW_URI": req.uri,
        "SERVER_PROTOCOL": "HTTP/%s" % ".".join([str(v) for v in req.version])
    })
    return env


def proxy_environ(req):
    info = req.proxy_protocol_info

    if not info:
        return {}

    return {
        "PROXY_PROTOCOL": info["proxy_protocol"],
        "REMOTE_ADDR": info["client_addr"],
        "REMOTE_PORT": str(info["client_port"]),
        "PROXY_ADDR": info["proxy_addr"],
        "PROXY_PORT": str(info["proxy_port"]),
    }


class Response:

    def __init__(self, req, sock, cfg):
        self.req = req
        self.sock = sock
        self.version = cfg.server_software
        self.status = None
        self.chunked = False
        self.must_close = False
        self.headers = []
        self.headers_sent = False
        self.response_length = None
        self.sent = 0
        self.upgrade = False
        self.cfg = cfg

    def force_close(self):
        self.must_close = True

    def should_close(self):
        if self.must_close or self.req.should_close():
            return True
        if self.response_length is not None or self.chunked:
            return False
        if self.req.method == 'HEAD':
            return False
        if self.status_code < 200 or self.status_code in (204, 304):
            return False
        return True

    def start_response(self, status, headers, exc_info=None):
        if exc_info:
            try:
                if self.status and self.headers_sent:
                    reraise(exc_info[0], exc_info[1], exc_info[2])
            finally:
                exc_info = None
        elif self.status is not None:
            raise AssertionError("Response headers already set!")

        self.status = status

        # get the status code from the response here so we can use it to check
        # the need for the connection header later without parsing the string
        # each time.
        try:
            self.status_code = int(self.status.split()[0])
        except ValueError:
            self.status_code = None

        self.process_headers(headers)
        self.chunked = self.is_chunked()
        return self.write

    def process_headers(self, headers, HEADER_RE=HEADER_RE, HEADER_VALUE_RE=HEADER_VALUE_RE,
            string_types=string_types, util_is_hoppish=util.is_hoppish):

        self_headers_append = self.headers.append

        for name, value in headers:

            if not isinstance(name, string_types):
                name = str(name)

            if not isinstance(value, string_types):
                value = str(value)

            if HEADER_RE.search(name):
                raise InvalidHeaderName('%r' % name)

            if HEADER_VALUE_RE.search(value):
                raise InvalidHeader('%r' % value)

            value = str(value).strip()
            lname = name.lower().strip()
            if lname == "content-length":
                self.response_length = int(value)
            elif util_is_hoppish(name):
                if lname == "connection":
                    # handle websocket
                    if value.lower().strip() == "upgrade":
                        self.upgrade = True
                elif lname == "upgrade":
                    if value.lower().strip() == "websocket":
                        self_headers_append((name.strip(), value))

                # ignore hopbyhop headers
                continue
            self_headers_append((name.strip(), value))

    def is_chunked(self):
        # Only use chunked responses when the client is
        # speaking HTTP/1.1 or newer and there was
        # no Content-Length header set.
        if self.response_length is not None:
            return False
        elif self.req.version <= (1, 0):
            return False
        elif self.req.method == 'HEAD':
            # Responses to a HEAD request MUST NOT contain a response body.
            return False
        elif self.status_code in (204, 304):
            # Do not use chunked responses when the response is guaranteed to
            # not have a response body.
            return False
        return True

    def default_headers(self, util_http_date=util.http_date):
        # set the connection header
        if self.upgrade:
            connection = "upgrade"
        elif self.should_close():
            connection = "close"
        else:
            connection = "keep-alive"

        headers = [
            "HTTP/%s.%s %s\r\n" % (self.req.version[0],
                self.req.version[1], self.status),
            "Server: %s\r\n" % self.version,
            "Date: %s\r\n" % util_http_date(),
            "Connection: %s\r\n" % connection
        ]
        if self.chunked:
            headers.append("Transfer-Encoding: chunked\r\n")
        return headers

    def send_headers(self, util_write=util.write, util_to_bytestring=util.to_bytestring):
        if self.headers_sent:
            return
        tosend = self.default_headers()
        tosend.extend(["%s: %s\r\n" % (k, v) for k, v in self.headers])

        header_str = "%s\r\n" % "".join(tosend)
        util_write(self.sock, util_to_bytestring(header_str, "ascii"))
        self.headers_sent = True

    def write(self, arg, binary_type=binary_type, util_write=util.write):
        self.send_headers()
        if not isinstance(arg, binary_type):
            raise TypeError('{!r} is not a byte'.format(arg))
        arglen = len(arg)
        tosend = arglen
        if self.response_length is not None:
            if self.sent >= self.response_length:
                # Never write more than self.response_length bytes
                return

            tosend = min(self.response_length - self.sent, tosend)
            if tosend < arglen:
                arg = arg[:tosend]

        # Sending an empty chunk signals the end of the
        # response and prematurely closes the response
        if self.chunked and tosend == 0:
            return

        self.sent += tosend
        util_write(self.sock, arg, self.chunked)

    def can_sendfile(self):
        return self.cfg.sendfile is not False and sendfile is not None

    def sendfile(self, respiter):
        if self.cfg.is_ssl or not self.can_sendfile():
            return False

        if not util.has_fileno(respiter.filelike):
            return False

        fileno = respiter.filelike.fileno()
        try:
            offset = os.lseek(fileno, 0, os.SEEK_CUR)
            if self.response_length is None:
                filesize = os.fstat(fileno).st_size

                # The file may be special and sendfile will fail.
                # It may also be zero-length, but that is okay.
                if filesize == 0:
                    return False

                nbytes = filesize - offset
            else:
                nbytes = self.response_length
        except (OSError, io.UnsupportedOperation):
            return False

        self.send_headers()

        if self.is_chunked():
            chunk_size = "%X\r\n" % nbytes
            self.sock.sendall(chunk_size.encode('utf-8'))

        sockno = self.sock.fileno()
        sent = 0

        while sent != nbytes:
            count = min(nbytes - sent, BLKSIZE)
            sent += sendfile(sockno, fileno, offset + sent, count)

        if self.is_chunked():
            self.sock.sendall(b"\r\n")

        os.lseek(fileno, offset, os.SEEK_SET)

        return True

    def write_file(self, respiter):
        if not self.sendfile(respiter):
            for item in respiter:
                self.write(item)

    def close(self):
        if not self.headers_sent:
            self.send_headers()
        if self.chunked:
            util.write_chunk(self.sock, b"")


def create(req, sock, client, server, cfg, Response=Response, default_environ=default_environ,
        string_types=string_types, binary_type=binary_type,
        unquote_to_wsgi_str=unquote_to_wsgi_str, proxy_environ=proxy_environ):
    resp = Response(req, sock, cfg)

    # set initial environ
    environ = default_environ(req, sock, cfg)

    # default variables
    host = None
    script_name = os.environ.get("SCRIPT_NAME", "")

    # add the headers to the environ
    for hdr_name, hdr_value in req.headers:
        if hdr_name == "EXPECT":
            # handle expect
            if hdr_value.lower() == "100-continue":
                sock.send(b"HTTP/1.1 100 Continue\r\n\r\n")
        elif hdr_name == 'HOST':
            host = hdr_value
        elif hdr_name == "SCRIPT_NAME":
            script_name = hdr_value
        elif hdr_name == "CONTENT-TYPE":
            environ['CONTENT_TYPE'] = hdr_value
            continue
        elif hdr_name == "CONTENT-LENGTH":
            environ['CONTENT_LENGTH'] = hdr_value
            continue

        key = 'HTTP_' + hdr_name.replace('-', '_')
        if key in environ:
            hdr_value = "%s,%s" % (environ[key], hdr_value)
        environ[key] = hdr_value

    # set the url scheme
    environ['wsgi.url_scheme'] = req.scheme

    # set the REMOTE_* keys in environ
    # authors should be aware that REMOTE_HOST and REMOTE_ADDR
    # may not qualify the remote addr:
    # http://www.ietf.org/rfc/rfc3875
    if isinstance(client, string_types):
        environ['REMOTE_ADDR'] = client
    elif isinstance(client, binary_type):
        environ['REMOTE_ADDR'] = client.decode()
    else:
        environ['REMOTE_ADDR'] = client[0]
        environ['REMOTE_PORT'] = str(client[1])

    # handle the SERVER_*
    # Normally only the application should use the Host header but since the
    # WSGI spec doesn't support unix sockets, we are using it to create
    # viable SERVER_* if possible.
    if isinstance(server, string_types):
        server = server.split(":")
        if len(server) == 1:
            # unix socket
            if host:
                server = host.split(':')
                if len(server) == 1:
                    if req.scheme == "http":
                        server.append(80)
                    elif req.scheme == "https":
                        server.append(443)
                    else:
                        server.append('')
            else:
                # no host header given which means that we are not behind a
                # proxy, so append an empty port.
                server.append('')
    environ['SERVER_NAME'] = server[0]
    environ['SERVER_PORT'] = str(server[1])

    # set the path and script name
    path_info = req.path
    if script_name:
        path_info = path_info.split(script_name, 1)[1]
    environ['PATH_INFO'] = unquote_to_wsgi_str(path_info)
    environ['SCRIPT_NAME'] = script_name

    # override the environ with the correct remote and server address if
    # we are behind a proxy using the proxy protocol.
    if req.proxy_protocol_info:
        environ.update(proxy_environ(req))
    return resp, environ
