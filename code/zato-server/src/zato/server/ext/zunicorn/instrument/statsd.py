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

"Bare-bones implementation of statsD's protocol, client-side"

import socket
import logging
from re import sub

from zato.server.ext.zunicorn.glogging import Logger
from zato.server.ext.zunicorn import six

# Instrumentation constants
METRIC_VAR = "metric"
VALUE_VAR = "value"
MTYPE_VAR = "mtype"
GAUGE_TYPE = "gauge"
COUNTER_TYPE = "counter"
HISTOGRAM_TYPE = "histogram"

class Statsd(Logger):
    """statsD-based instrumentation, that passes as a logger
    """
    def __init__(self, cfg):
        """host, port: statsD server
        """
        Logger.__init__(self, cfg)
        self.prefix = sub(r"^(.+[^.]+)\.*$", "\\g<1>.", cfg.statsd_prefix)
        try:
            host, port = cfg.statsd_host
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.connect((host, int(port)))
        except Exception:
            self.sock = None

    # Log errors and warnings
    def critical(self, msg, *args, **kwargs):
        Logger.critical(self, msg, *args, **kwargs)
        self.increment("gunicorn.log.critical", 1)

    def error(self, msg, *args, **kwargs):
        Logger.error(self, msg, *args, **kwargs)
        self.increment("gunicorn.log.error", 1)

    def warning(self, msg, *args, **kwargs):
        Logger.warning(self, msg, *args, **kwargs)
        self.increment("gunicorn.log.warning", 1)

    def exception(self, msg, *args, **kwargs):
        Logger.exception(self, msg, *args, **kwargs)
        self.increment("gunicorn.log.exception", 1)

    # Special treatement for info, the most common log level
    def info(self, msg, *args, **kwargs):
        self.log(logging.INFO, msg, *args, **kwargs)

    # skip the run-of-the-mill logs
    def debug(self, msg, *args, **kwargs):
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs):
        """Log a given statistic if metric, value and type are present
        """
        try:
            extra = kwargs.get("extra", None)
            if extra is not None:
                metric = extra.get(METRIC_VAR, None)
                value = extra.get(VALUE_VAR, None)
                typ = extra.get(MTYPE_VAR, None)
                if metric and value and typ:
                    if typ == GAUGE_TYPE:
                        self.gauge(metric, value)
                    elif typ == COUNTER_TYPE:
                        self.increment(metric, value)
                    elif typ == HISTOGRAM_TYPE:
                        self.histogram(metric, value)
                    else:
                        pass

            # Log to parent logger only if there is something to say
            if msg:
                Logger.log(self, lvl, msg, *args, **kwargs)
        except Exception:
            Logger.warning(self, "Failed to log to statsd", exc_info=True)

    # access logging
    def access(self, resp, req, environ, request_time):
        """Measure request duration
        request_time is a datetime.timedelta
        """
        Logger.access(self, resp, req, environ, request_time)
        duration_in_ms = request_time.seconds * 1000 + float(request_time.microseconds) / 10 ** 3
        status = resp.status
        if isinstance(status, str):
            status = int(status.split(None, 1)[0])
        self.histogram("gunicorn.request.duration", duration_in_ms)
        self.increment("gunicorn.requests", 1)
        self.increment("gunicorn.request.status.%d" % status, 1)

    # statsD methods
    # you can use those directly if you want
    def gauge(self, name, value):
        self._sock_send("{0}{1}:{2}|g".format(self.prefix, name, value))

    def increment(self, name, value, sampling_rate=1.0):
        self._sock_send("{0}{1}:{2}|c|@{3}".format(self.prefix, name, value, sampling_rate))

    def decrement(self, name, value, sampling_rate=1.0):
        self._sock_send("{0}{1}:-{2}|c|@{3}".format(self.prefix, name, value, sampling_rate))

    def histogram(self, name, value):
        self._sock_send("{0}{1}:{2}|ms".format(self.prefix, name, value))

    def _sock_send(self, msg):
        try:
            if isinstance(msg, six.text_type):
                msg = msg.encode("ascii")
            if self.sock:
                self.sock.send(msg)
        except Exception:
            Logger.warning(self, "Error sending message to statsd", exc_info=True)
