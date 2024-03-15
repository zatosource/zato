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

import regex as re
import socket
from errno import ENOTCONN

from zato.server.ext.zunicorn._compat import bytes_to_str
from zato.server.ext.zunicorn.http.unreader import SocketUnreader
from zato.server.ext.zunicorn.http.body import ChunkedReader, LengthReader, EOFReader, Body
from zato.server.ext.zunicorn.http.errors import (InvalidHeader, InvalidHeaderName, NoMoreData,
    InvalidRequestLine, InvalidRequestMethod, InvalidHTTPVersion,
    LimitRequestLine, LimitRequestHeaders)
from zato.server.ext.zunicorn.http.errors import InvalidProxyLine, ForbiddenProxyRequest
from zato.server.ext.zunicorn.http.errors import InvalidSchemeHeaders
from zato.server.ext.zunicorn.six import BytesIO, string_types
from zato.server.ext.zunicorn.util import split_request_uri

MAX_REQUEST_LINE = 8190
MAX_HEADERS = 32768
DEFAULT_MAX_HEADERFIELD_SIZE = 8190

HEADER_RE = re.compile(r"[\x00-\x1F\x7F()<>@,;:\[\]={} \t\\\"]")
METHOD_RE = re.compile(r"[A-Z0-9$-_.]{3,20}")
VERSION_RE = re.compile(r"HTTP/(\d+)\.(\d+)")


class Message:
    def __init__(self, cfg, unreader, MAX_HEADERS=MAX_HEADERS,
            DEFAULT_MAX_HEADERFIELD_SIZE=DEFAULT_MAX_HEADERFIELD_SIZE):
        self.cfg = cfg
        self.unreader = unreader
        self.version = None
        self.headers = []
        self.trailers = []
        self.body = None
        self.scheme = "https" if cfg.is_ssl else "http"

        # set headers limits
        self.limit_request_fields = MAX_HEADERS
        self.limit_request_field_size = DEFAULT_MAX_HEADERFIELD_SIZE

        # set max header buffer size
        max_header_field_size = self.limit_request_field_size or DEFAULT_MAX_HEADERFIELD_SIZE
        self.max_buffer_headers = self.limit_request_fields * \
            (max_header_field_size + 2) + 4

        unused = self.parse(self.unreader)
        self.unreader.unread(unused)
        self.set_body_reader()

    def parse(self, unreader):
        raise NotImplementedError()

    def parse_headers(self, data, bytes_to_str=bytes_to_str):
        cfg = self.cfg
        headers = []

        # Split lines on \r\n keeping the \r\n on each line
        lines = [bytes_to_str(line) + "\r\n" for line in data.split(b"\r\n")]

        # handle scheme headers
        scheme_header = False
        secure_scheme_headers = {}
        if '*' in cfg.forwarded_allow_ips:
            secure_scheme_headers = cfg.secure_scheme_headers
        elif isinstance(self.unreader, SocketUnreader):
            remote_addr = self.unreader.sock.getpeername()
            if isinstance(remote_addr, tuple):
                remote_host = remote_addr[0]
                if remote_host in cfg.forwarded_allow_ips:
                    secure_scheme_headers = cfg.secure_scheme_headers
            elif isinstance(remote_addr, string_types):
                secure_scheme_headers = cfg.secure_scheme_headers

        # Parse headers into key/value pairs paying attention
        # to continuation lines.

        self_limit_request_fields = self.limit_request_fields
        self_limit_request_field_size = self.limit_request_field_size
        lines_pop = lines.pop

        while lines:
            if len(headers) >= self_limit_request_fields:
                raise LimitRequestHeaders("limit request headers fields")

            # Parse initial header name : value pair.
            curr = lines_pop(0)
            header_length = len(curr)
            if curr.find(":") < 0:
                raise InvalidHeader(curr.strip())
            name, value = curr.split(":", 1)
            name = name.rstrip(" \t").upper()
            if HEADER_RE.search(name):
                raise InvalidHeaderName(name)

            name, value = name.strip(), [value.lstrip()]

            # Consume value continuation lines
            while lines and lines[0].startswith((" ", "\t")):
                curr = lines_pop(0)
                header_length += len(curr)
                if header_length > self_limit_request_field_size > 0:
                    raise LimitRequestHeaders("limit request headers "
                            + "fields size")
                value.append(curr)
            value = ''.join(value).rstrip()

            if header_length > self_limit_request_field_size > 0:
                raise LimitRequestHeaders("limit request headers fields size")

            if name in secure_scheme_headers:
                secure = value == secure_scheme_headers[name]
                scheme = "https" if secure else "http"
                if scheme_header:
                    if scheme != self.scheme:
                        raise InvalidSchemeHeaders()
                else:
                    scheme_header = True
                    self.scheme = scheme

            headers.append((name, value))

        return headers

    def set_body_reader(self):
        chunked = False
        content_length = None
        for (name, value) in self.headers:
            if name == "CONTENT-LENGTH":
                content_length = value
            elif name == "TRANSFER-ENCODING":
                chunked = value.lower() == "chunked"
            elif name == "SEC-WEBSOCKET-KEY1":
                content_length = 8

        if chunked:
            self.body = Body(ChunkedReader(self, self.unreader))
        elif content_length is not None:
            try:
                content_length = int(content_length)
            except ValueError:
                raise InvalidHeader("CONTENT-LENGTH", req=self)

            if content_length < 0:
                raise InvalidHeader("CONTENT-LENGTH", req=self)

            self.body = Body(LengthReader(self.unreader, content_length))
        else:
            self.body = Body(EOFReader(self.unreader))

    def should_close(self):
        for (h, v) in self.headers:
            if h == "CONNECTION":
                v = v.lower().strip()
                if v == "close":
                    return True
                elif v == "keep-alive":
                    return False
                break
        return self.version <= (1, 0)


class Request(Message):
    def __init__(self, cfg, unreader, req_number=1):
        self.method = None
        self.uri = None
        self.path = None
        self.query = None
        self.fragment = None

        # get max request line size
        self.limit_request_line = cfg.limit_request_line
        if (self.limit_request_line < 0
            or self.limit_request_line >= MAX_REQUEST_LINE):
            self.limit_request_line = MAX_REQUEST_LINE

        self.req_number = req_number
        self.proxy_protocol_info = None
        super(Request, self).__init__(cfg, unreader)

    def get_data(self, unreader, buf, stop=False, NoMoreData=NoMoreData):
        data = unreader.read()
        if not data:
            if stop:
                raise StopIteration()
            raise NoMoreData(buf.getvalue())
        buf.write(data)

    def parse(self, unreader, BytesIO=BytesIO):
        buf = BytesIO()
        self.get_data(unreader, buf, stop=True)

        # get request line
        line, rbuf = self.read_line(unreader, buf, self.limit_request_line)

        # proxy protocol
        if self.cfg.proxy_protocol:
            if self.proxy_protocol(bytes_to_str(line)):
                # get next request line
                buf = BytesIO()
                buf.write(rbuf)
                line, rbuf = self.read_line(unreader, buf, self.limit_request_line)

        self.parse_request_line(line)
        buf = BytesIO()
        buf.write(rbuf)

        # Headers
        data = buf.getvalue()
        idx = data.find(b"\r\n\r\n")

        done = data[:2] == b"\r\n"

        data_find = data.find
        self_get_data = self.get_data
        buf_getvalue = buf.getvalue
        self_max_buffer_headers = self.max_buffer_headers

        while True:
            idx = data_find(b"\r\n\r\n")
            done = data[:2] == b"\r\n"

            if idx < 0 and not done:
                self_get_data(unreader, buf)
                data = buf_getvalue()
                if len(data) > self_max_buffer_headers:
                    raise LimitRequestHeaders("max buffer headers")
            else:
                break

        if done:
            self.unreader.unread(data[2:])
            return b""

        self.headers = self.parse_headers(data[:idx])

        ret = data[idx + 4:]
        buf = None

        return ret

    def read_line(self, unreader, buf, limit=0):
        data = buf.getvalue()
        data_find = data.find
        self_get_data = self.get_data
        buf_getvalue = buf.getvalue

        while True:
            idx = data_find(b"\r\n")
            if idx >= 0:
                # check if the request line is too large
                if idx > limit > 0:
                    raise LimitRequestLine(idx, limit)
                break
            elif len(data) - 2 > limit > 0:
                raise LimitRequestLine(len(data), limit)
            self_get_data(unreader, buf)
            data = buf_getvalue()

        return (data[:idx],  # request line,
                data[idx + 2:])  # residue in the buffer, skip \r\n

    def proxy_protocol(self, line):
        """\
        Detect, check and parse proxy protocol.

        :raises: ForbiddenProxyRequest, InvalidProxyLine.
        :return: True for proxy protocol line else False
        """
        if not self.cfg.proxy_protocol:
            return False

        if self.req_number != 1:
            return False

        if not line.startswith("PROXY"):
            return False

        self.proxy_protocol_access_check()
        self.parse_proxy_protocol(line)

        return True

    def proxy_protocol_access_check(self):
        # check in allow list
        if isinstance(self.unreader, SocketUnreader):
            try:
                remote_host = self.unreader.sock.getpeername()[0]
            except socket.error as e:
                if e.args[0] == ENOTCONN:
                    raise ForbiddenProxyRequest("UNKNOW")
                raise
            if ("*" not in self.cfg.proxy_allow_ips and
                    remote_host not in self.cfg.proxy_allow_ips):
                raise ForbiddenProxyRequest(remote_host)

    def parse_proxy_protocol(self, line):
        bits = line.split()

        if len(bits) != 6:
            raise InvalidProxyLine(line)

        # Extract data
        proto = bits[1]
        s_addr = bits[2]
        d_addr = bits[3]

        # Validation
        if proto not in ["TCP4", "TCP6"]:
            raise InvalidProxyLine("protocol '%s' not supported" % proto)
        if proto == "TCP4":
            try:
                socket.inet_pton(socket.AF_INET, s_addr)
                socket.inet_pton(socket.AF_INET, d_addr)
            except socket.error:
                raise InvalidProxyLine(line)
        elif proto == "TCP6":
            try:
                socket.inet_pton(socket.AF_INET6, s_addr)
                socket.inet_pton(socket.AF_INET6, d_addr)
            except socket.error:
                raise InvalidProxyLine(line)

        try:
            s_port = int(bits[4])
            d_port = int(bits[5])
        except ValueError:
            raise InvalidProxyLine("invalid port %s" % line)

        if not ((0 <= s_port <= 65535) and (0 <= d_port <= 65535)):
            raise InvalidProxyLine("invalid port %s" % line)

        # Set data
        self.proxy_protocol_info = {
            "proxy_protocol": proto,
            "client_addr": s_addr,
            "client_port": s_port,
            "proxy_addr": d_addr,
            "proxy_port": d_port
        }

    def parse_request_line(self, line_bytes, METHOD_RE=METHOD_RE, VERSION_RE=VERSION_RE,
            split_request_uri=split_request_uri, bytes_to_str=bytes_to_str):

        bits = [bytes_to_str(bit) for bit in line_bytes.split(None, 2)]
        if len(bits) != 3:
            raise InvalidRequestLine(bytes_to_str(line_bytes))

        # Method
        if not METHOD_RE.match(bits[0]):
            raise InvalidRequestMethod(bits[0])
        self.method = bits[0].upper()

        # URI
        self.uri = bits[1]

        try:
            parts = split_request_uri(self.uri)
        except ValueError:
            raise InvalidRequestLine(bytes_to_str(line_bytes))
        self.path = parts.path or ""
        self.query = parts.query or ""
        self.fragment = parts.fragment or ""

        # Version
        match = VERSION_RE.match(bits[2])
        if match is None:
            raise InvalidHTTPVersion(bits[2])
        self.version = (int(match.group(1)), int(match.group(2)))

    def set_body_reader(self, EOFReader=EOFReader, Body=Body, LengthReader=LengthReader):
        super(Request, self).set_body_reader()
        if isinstance(self.body.reader, EOFReader):
            self.body = Body(LengthReader(self.unreader, 0))
