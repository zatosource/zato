# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to be first
from gevent.monkey import patch_all
patch_all()

# stdlib
from datetime import datetime
from tempfile import NamedTemporaryFile
from time import time
from traceback import format_exc

# Bunch
from bunch import bunchify

# gevent
from gevent.pywsgi import WSGIHandler, WSGIServer

# Zato
from zato.common.api import SFTP
from zato.common.json_internal import dumps
from zato.common.sftp import SFTPOutput
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response
from zato.server.connection.connector.subprocess_.impl.events.database import EventsDatabase

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

class _WSGIHandler(WSGIHandler):
    def log_request(self, *ignored_args, **ignored_kwargs):
        pass

class _WSGIServer(WSGIServer):
    handler_class = _WSGIHandler

    def shutdown(self, *ignored_args, **ignored_kwargs):
        # Do nothing, added only for API completeness with what base.py expects
        pass

# ################################################################################################################################
# ################################################################################################################################

class EventsConnectionContainer(BaseConnectionContainer):

    connection_class = object
    ipc_name = conn_type = logging_file_name = 'events'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fs_data_path = '/tmp/zzz-parquet'
        sync_threshold = 120_000
        sync_interval_ms = 120_000

        self.events_db = EventsDatabase(fs_data_path, sync_threshold, sync_interval_ms)

# ################################################################################################################################

    def _on_EVENT_PUSH(self, msg, is_reconnect=False, _utcnow=datetime.utcnow):
        out = {}
        #data = msg['data']

        elem = 'aaa' + utcnow().isoformat()
        x = int(time() * 1_000_000)

        data = {
            'id': elem + utcnow().isoformat(),
            'cid': 'cid.' + elem,
            'timestamp': '2021-05-12T07:07:01.4841' + elem,

            'source_type': 'zato.server' + elem,
            'source_id': 'server1' + elem,

            'object_type': elem,
            'object_id': elem,

            'source_type': elem,
            'source_id': elem,

            'recipient_type': elem,
            'recipient_id': elem,

            'total_time_ms': x,
        }

        self.events_db.push(data)

        return Response(data=dumps(out))

# ################################################################################################################################

    def make_server(self):
        return _WSGIServer((self.host, self.port), self.on_wsgi_request)

# ################################################################################################################################

if __name__ == '__main__':

    container = EventsConnectionContainer()
    container.run()

# ################################################################################################################################
