# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import asyncore, json, logging, multiprocessing, ssl, time

# Zope
from zope.server.http.httpserver import HTTPServer
from zope.server.taskthreads import ThreadedTaskDispatcher

# Spring Python
from springpython.util import synchronized

# Zato
from zato.common import ZATO_CONFIG_REQUEST, ZATO_OK
from zato.common.util import TRACE1
from zato.common.odb import create_pool
from zato.server.base import BaseServer, IPCMessage


class ZatoHTTPServer(HTTPServer):
    def __init__(self, host, port, task_dispatcher):

        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))
        super(ZatoHTTPServer, self).__init__(host, port, task_dispatcher)

    def executeRequest(self, task):

        # Currently, we always return text/xml.
        task.response_headers["Content-Type"] = "text/xml"

        try:
            # Collect necessary request data.
            request_body = task.request_data.getBodyStream().getvalue()
            headers = task.request_data.headers
            #time.sleep(0.1)
            #print(headers.get('X_ZATO_PEERCERT'))

            print(33, headers)

            # Fetch the response.
            response = '<?xml version="1.0" encoding="utf-8"?><axx />' #self.soap_dispatcher.handle(request_body, headers)

        # Any exception at this point must be our fault.
        except Exception:
            tb = get_last_traceback(e)
            self.logger.error("Exception caught [%s]" % tb)
            response = server_soap_error(tb)

        # Return HTTP response.
        task.response_headers["Content-Length"] = str(len(response))
        task.write(response)


class ParallelServer(object):
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def run_forever(self):
        task_dispatcher = ThreadedTaskDispatcher()
        task_dispatcher.setThreadCount(90)

        self.logger.debug("host=[{0}], port=[{1}]".format(self.host, self.port))

        ZatoHTTPServer(self.host, self.port, task_dispatcher)

        try:
            while True:
                asyncore.poll(5)

        except KeyboardInterrupt:
            self.logger.info("Shutting down.")
            task_dispatcher.shutdown()


    def send_config_request(self, command, data=None, timeout=None):
        """ Sends a synchronous IPC request to the SingletonServer.
        """
        request = self._create_ipc_config_request(command, data)
        return self._send_config_request(request, self.partner_request_queues.values()[0], timeout)

################################################################################

    def _on_config_sql(self, msg):
        """ A common method for handling all SQL connection pools-related config
        requests. Must always be called from within a concrete, synchronized,
        configuration handler (such as _on_config_EDIT_SQL_CONNECTION_POOL etc.)
        """
        command = msg.command
        params = json.loads(msg.params["data"])

        command_handler = getattr(self.sql_pool, "_on_config_" + command)
        command_handler(params)

        return ZATO_OK, ""

    @synchronized()
    def _on_config_EDIT_SQL_CONNECTION_POOL(self, msg):
        """ Updates all of SQL connection pool's parameters, except for
        the password.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_CREATE_SQL_CONNECTION_POOL(self, msg):
        """ Creates a new SQL connection pool with no password set.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_DELETE_SQL_CONNECTION_POOL(self, msg):
        """ Deletes an SQL connection pool.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_CHANGE_PASSWORD_SQL_CONNECTION_POOL(self, msg):
        """ Deletes an SQL connection pool.
        """
        return self._on_config_sql(msg)

################################################################################

    @synchronized()
    def _on_config_LOAD_EGG_SERVICES(self, msg):
        """ Loads Zato services from a given .egg distribution and makes them
        available for immediate use.
        """
        egg_path = json.loads(msg.params["data"])
        self.service_store.import_services_from_egg(egg_path, self)

        return ZATO_OK, ""

################################################################################

    @synchronized()
    def _on_config_ADD_TO_WSS_NONCE_CACHE(self, msg):
        wsse_nonce, recycle_time = json.loads(msg.params["data"])

        # Note that the method is already synchronized.
        self.wss_nonce_cache[wsse_nonce] = recycle_time

        return ZATO_OK, ""
