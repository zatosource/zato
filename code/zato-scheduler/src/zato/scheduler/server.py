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
from gevent import spawn
from gevent.pywsgi import WSGIServer

# Zato
from zato.common import ZATO_ODB_POOL_NAME
from zato.common.odb.api import ODBManager
from zato.scheduler.api import Scheduler

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

ok = b'200 OK'
headers = [(b'Content-Type', b'application/json')]

# ################################################################################################################################

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
        self.scheduler = Scheduler()
        self.odb = ODBManager()

# ################################################################################################################################

    def serve_forever(self):
        self.odb.init_session(ZATO_ODB_POOL_NAME, self.config.odb, self.odb.pool, False)
        self.scheduler.serve_forever()
        self.api_server.serve_forever()

# ################################################################################################################################

    def __call__(self, env, start_response):
        try:
            start_response(ok, headers)
            return [b'{}\n']
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################
