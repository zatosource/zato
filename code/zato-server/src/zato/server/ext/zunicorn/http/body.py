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

from io import BytesIO

from zato.server.ext.zunicorn.http.errors import (NoMoreData, ChunkMissingTerminator,
        InvalidChunkSize)
from zato.server.ext.zunicorn import six


class ChunkedReader:
    def __init__(self, req, unreader, BytesIO=BytesIO):
        self.req = req
        self.parser = self.parse_chunked(unreader)
        self.buf = BytesIO()

    def read(self, size, integer_types=six.integer_types, BytesIO=BytesIO):
        if not isinstance(size, integer_types):
            raise TypeError("size must be an integral type")
        if size < 0:
            raise ValueError("Size must be positive.")
        if size == 0:
            return b""

        buf_tell = self.buf.tell
        buf_write = self.buf.write

        if self.parser:
            while buf_tell() < size:
                try:
                    buf_write(next(self.parser))
                except StopIteration:
                    self.parser = None
                    break

        data = self.buf.getvalue()
        ret, rest = data[:size], data[size:]
        self.buf = BytesIO()
        self.buf.write(rest)
        return ret

    def parse_trailers(self, unreader, data, BytesIO=BytesIO):
        buf = BytesIO()
        buf.write(data)

        buf_getvalue = buf.getvalue

        value = buf_getvalue()

        idx = value.find(b"\r\n\r\n")
        done = value[:2] == b"\r\n"

        while idx < 0 and not done:
            self.get_data(unreader, buf.write)
            idx = buf_getvalue().find(b"\r\n\r\n")
            done = buf_getvalue()[:2] == b"\r\n"
        if done:
            unreader.unread(buf_getvalue()[2:])
            return b""
        self.req.trailers = self.req.parse_headers(buf_getvalue()[:idx])
        unreader.unread(buf_getvalue()[idx + 4:])

    def parse_chunked(self, unreader):
        (size, rest) = self.parse_chunk_size(unreader)
        while size > 0:
            while size > len(rest):
                size -= len(rest)
                yield rest
                rest = unreader.read()
                if not rest:
                    raise NoMoreData()
            yield rest[:size]
            # Remove \r\n after chunk
            rest = rest[size:]
            while len(rest) < 2:
                rest += unreader.read()
            if rest[:2] != b'\r\n':
                raise ChunkMissingTerminator(rest[:2])
            (size, rest) = self.parse_chunk_size(unreader, data=rest[2:])

    def parse_chunk_size(self, unreader, data=None, BytesIO=BytesIO):
        buf = BytesIO()
        buf_write = buf.write

        if data is not None:
            buf_write(data)

        idx = buf.getvalue().find(b"\r\n")
        while idx < 0:
            self.get_data(unreader, buf_write)
            idx = buf.getvalue().find(b"\r\n")

        data = buf.getvalue()
        line, rest_chunk = data[:idx], data[idx + 2:]

        chunk_size = line.split(b";", 1)[0].strip()
        try:
            chunk_size = int(chunk_size, 16)
        except ValueError:
            raise InvalidChunkSize(chunk_size)

        if chunk_size == 0:
            try:
                self.parse_trailers(unreader, rest_chunk)
            except NoMoreData:
                pass
            return (0, None)
        return (chunk_size, rest_chunk)

    def get_data(self, unreader, buf_write, NoMoreData=NoMoreData):
        data = unreader.read()
        if not data:
            raise NoMoreData()
        buf_write(data)


class LengthReader:
    def __init__(self, unreader, length):
        self.unreader = unreader
        self.length = length

    def read(self, size, integer_types=six.integer_types, BytesIO=BytesIO):
        if not isinstance(size, integer_types):
            raise TypeError("size must be an integral type")

        size = min(self.length, size)
        if size < 0:
            raise ValueError("Size must be positive.")
        if size == 0:
            return b""

        buf = BytesIO()

        buf_write = buf.write
        buf_tell = buf.tell
        self_unreader_read = self.unreader.read

        data = self_unreader_read()

        while data:
            buf_write(data)
            if buf_tell() >= size:
                break
            data = self_unreader_read()

        buf = buf.getvalue()
        ret, rest = buf[:size], buf[size:]
        self.unreader.unread(rest)
        self.length -= size
        return ret


class EOFReader:
    def __init__(self, unreader):
        self.unreader = unreader
        self.buf = six.BytesIO()
        self.finished = False

    def read(self, size):
        if not isinstance(size, six.integer_types):
            raise TypeError("size must be an integral type")
        if size < 0:
            raise ValueError("Size must be positive.")
        if size == 0:
            return b""

        if self.finished:
            data = self.buf.getvalue()
            ret, rest = data[:size], data[size:]
            self.buf = six.BytesIO()
            self.buf.write(rest)
            return ret

        data = self.unreader.read()
        while data:
            self.buf.write(data)
            if self.buf.tell() > size:
                break
            data = self.unreader.read()

        if not data:
            self.finished = True

        data = self.buf.getvalue()
        ret, rest = data[:size], data[size:]
        self.buf = six.BytesIO()
        self.buf.write(rest)
        return ret


class Body:
    def __init__(self, reader, BytesIO=BytesIO):
        self.reader = reader
        self.buf = BytesIO()

    def __iter__(self):
        return self

    def __next__(self):
        ret = self.readline()
        if not ret:
            raise StopIteration()
        return ret
    next = __next__

    def getsize(self, size):
        if size is None:
            return six.MAXSIZE
        elif not isinstance(size, six.integer_types):
            raise TypeError("size must be an integral type")
        elif size < 0:
            return six.MAXSIZE
        return size

    def read(self, size=None, BytesIO=BytesIO):
        size = self.getsize(size)
        if size == 0:
            return b""

        if size < self.buf.tell():
            data = self.buf.getvalue()
            ret, rest = data[:size], data[size:]
            self.buf = six.BytesIO()
            self.buf.write(rest)
            return ret

        self_buf_tell = self.buf.tell
        self_buf_write = self.buf.write
        self_reader_read = self.reader.read

        while size > self_buf_tell():
            data = self_reader_read(1024)
            if not data:
                break
            self_buf_write(data)

        data = self.buf.getvalue()
        ret, rest = data[:size], data[size:]
        self.buf = BytesIO()
        self.buf.write(rest)
        return ret

    def readline(self, size=None, BytesIO=BytesIO):
        size = self.getsize(size)
        if size == 0:
            return b""

        data = self.buf.getvalue()
        self.buf = BytesIO()
        ret = []

        data_find = data.find
        ret_append = ret.append
        self_reader_read = self.reader.read
        self_buf_write = self.buf.write

        while 1:
            idx = data_find(b"\n", 0, size)
            idx = idx + 1 if idx >= 0 else size if len(data) >= size else 0
            if idx:
                ret_append(data[:idx])
                self_buf_write(data[idx:])
                break

            ret_append(data)
            size -= len(data)
            data = self_reader_read(min(1024, size))
            if not data:
                break

        return b"".join(ret)

    def readlines(self, size=None):
        ret = []
        data = self.read()
        while data:
            pos = data.find(b"\n")
            if pos < 0:
                ret.append(data)
                data = b""
            else:
                line, data = data[:pos + 1], data[pos + 1:]
                ret.append(line)
        return ret
