# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# gevent
from gevent.pywsgi import WSGIServer

logger = logging.getLogger(__name__)

ok = b'200 OK'
headers = [(b'Content-Type', b'application/json')]

class SchedulerServer(object):
    """ Main class spawning scheduler-related tasks and listening for HTTP API requests.
    """
    def __init__(self, config):
        self.config = config

        if self.config.crypto.use_tls:
            priv_key, cert = self.config.crypto.priv_key_location, self.config.crypto.cert_location
        else:
            priv_key, cert = None, None

        self.api_server = WSGIServer((config.bind.host, int(config.bind.port)), self, keyfile=priv_key, certfile=cert)

    def serve_forever(self):
        self.api_server.serve_forever()

    def __call__(self, env, start_response):
        try:
            start_response(ok, headers)
            return [b'{}\n']
        except Exception, e:
            logger.warn(format_exc(e))

'''
def hello_world(env, start_response):
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"<b>hello world</b>"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']
'''
