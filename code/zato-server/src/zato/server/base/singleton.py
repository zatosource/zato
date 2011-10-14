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
import json, logging
from uuid import uuid4
from traceback import format_exc

# lxml
from lxml import etree

# ZeroMQ
import zmq

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient
from zato.common import ZATO_CONFIG_REQUEST, ZATO_CONFIG_RESPONSE, ZATO_NOT_GIVEN, \
     ZATO_ERROR, ZATO_OK, ZatoException
from zato.common.broker_message import code_to_name, MESSAGE
from zato.common.util import TRACE1, zmq_names

class SingletonServer(object):
    """ A server of which one instance only may be running in a Zato container.
    Holds and processes data which can't be made parallel, such as scheduler,
    hot-deployment or on-disk configuration management.
    """
    
    def __init__(self, parallel_server=None, scheduler=None, broker_token=None, 
                 zmq_context=None, broker_host=None, broker_push_port=None, 
                 broker_sub_port=None):
        self.parallel_server = parallel_server
        self.scheduler = scheduler
        self.broker_token = broker_token
        self.broker_host = broker_host
        self.broker_push_port = broker_push_port
        self.broker_sub_port = broker_sub_port
        self.zmq_context = zmq_context
    
    def on_inproc_message_handler(self, msg):
        print('Singleton handler', msg)

    def run(self, *ignored_args, **kwargs):
        self.logger = logging.getLogger('{0}.{1}:{2}'.format(__name__, 
                                        self.__class__.__name__, hex(id(self))))

        for name in('broker_token', 'zmq_context', 'broker_host', 'broker_push_port', 
                    'broker_sub_port'):
            if name in kwargs:
                setattr(self, name, kwargs[name])
                
        self.broker_push_addr = 'tcp://{0}:{1}'.format(self.broker_host, self.broker_push_port)
        self.broker_sub_addr = 'tcp://{0}:{1}'.format(self.broker_host, self.broker_sub_port)
        
        # Initialize scheduler.
        self.scheduler.singleton = self
        
        self.broker_client = BrokerClient(self.broker_token, self.zmq_context, 
            self.broker_push_addr,  self.broker_sub_addr, self.on_config_msg)
        self.broker_client.start_subscriber()
        
        '''
        # Start the pickup monitor.
        self.logger.debug("Pickup notifier starting.")
        self.pickup.watch()
        
        '''
        
################################################################################

    def on_config_msg(self, msg):
        """ Receives a configuration message, parses its JSON contents and invokes
        an appropriate handler, the one indicated by the msg's 'action' key so
        if the action is '1000' then self.on_config_SCHEDULER_CREATE
        will be invoked (because '1000' happens to be the code for creating
        a new scheduler's job, see zato.common.broker_message for the list
        of all actions).
        """
        
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('Got message [{0}]'.format(msg))
            
        msg_type = msg[:MESSAGE.MESSAGE_TYPE_LENGTH]
        msg = loads(msg[MESSAGE.PAYLOAD_START:])
        msg = Bunch(msg)
        
        action = code_to_name[msg['action']]
        handler = 'on_config_{0}'.format(action)
        handler = getattr(self, handler)
        handler(msg)
        
    def on_config_SCHEDULER_CREATE(self, msg):
        self.scheduler.create(msg)
            

################################################################################

    def load_egg_services(self, egg_path):
        """ Tells each of parallel servers to load Zato services off an .egg
        distribution. The .egg is guaranteed to contain at least one service to
        load.
        """

        # XXX: That loop could be refactored out to some common place.
        for q in self.partner_request_queues.values():
            req = self._create_ipc_config_request("LOAD_EGG_SERVICES", egg_path)
            code, reason = self._send_config_request(req, q, timeout=1.0)

            if code != ZATO_OK:
                # XXX: Add the parallel server's PID/name here.
                msg = "Could not update a parallel server, server may have been left in an unstable state, reason=[%s]" % reason
                self.logger.error(msg)
                raise ZatoException(msg)

        return ZATO_OK, ""


'''
################################################################################

    def _on_config_GET_JOB_LIST(self, msg):
        """ Returns a list of all jobs defined in the SingletonServer's scheduler.
        """
        job_list = etree.Element("job_list")

        def _handle_one_time(job_elem, info):
            for attr in ["date_time"]:
                self.logger.log(TRACE1, "attr=[%s], info[attr]=[%r]" % (attr, info[attr]))
                item = etree.SubElement(job_elem, attr)
                item.text = unicode(info[attr])
                job_elem.append(item)

        def _handle_interval_based(job_elem, info):
            for attr in ["start_date", "weeks", "days", "hours", "minutes", "seconds", "repeat"]:
                self.logger.log(TRACE1, "attr=[%s], info[attr]=[%r]" % (attr, info[attr]))
                item = etree.SubElement(job_elem, attr)
                item.text = unicode(info[attr] if info[attr] else "")
                job_elem.append(item)

        _locals = locals()

        for name in sorted(self.scheduler.job_list):
            info = self.scheduler.job_list[name]
            self.logger.log(TRACE1, "name=[%s], info=[%s]" % (name, info))

            job_elem = etree.Element("job")
            job_list.append(job_elem)

            # Common attributes.
            item = etree.SubElement(job_elem, "name")
            item.text = name
            job_elem.append(item)

            for attr in ["type", "service", "extra"]:
                self.logger.log(TRACE1, "attr=[%s], info[attr]=[%r]" % (attr, info[attr]))

                item = etree.SubElement(job_elem, attr)
                item.text = info[attr]
                job_elem.append(item)

            # Call the handler which will, basing on the job's type,
            # create appropriate XML elements.
            _locals["_handle_" + info["type"]](job_elem, info)

        return ZATO_OK, json.dumps(etree.tostring(job_list))

    def _on_config_CREATE_JOB(self, msg):
        """ Creates a new scheduler job.
        """
        # TODO: Refactoring (merge with EDIT_JOB)
        data = json.loads(msg.params["data"])
        self.logger.log(TRACE1, "_on_config_CREATE_JOB data=[%s]" % data)
        for idx, item in enumerate(data):
            self.logger.log(TRACE1, "idx=[%s] item=[%s]" % (idx, item))

        job_type, job_name, service, extra, params = data

        try:
            if job_type == "one_time":
                self.scheduler.create_one_time(job_name, service, extra, params)
            elif job_type == "interval_based":
                self.scheduler.create_interval_based(job_name, service, extra, params)
            else:
                raise ZatoException("Unknow job_type=[%s]" % job_type)
            return ZATO_OK, ""
        except Exception, e:
            exc = format_exc()
            self.logger.error("_on_config_CREATE_JOB, exc=[%s]" % exc)
            return ZATO_ERROR, json.dumps(exc)

    def _on_config_EDIT_JOB(self, msg):
        """ Creates a new scheduler job.
        """
        # TODO: Refactoring (merge with CREATE_JOB)
        # TODO: Every handler needs to load the data so it makes sense to do
        # it earlier.
        data = json.loads(msg.params["data"])
        self.logger.log(TRACE1, "_on_config_EDIT_JOB data=[%s]" % data)
        for idx, item in enumerate(data):
            self.logger.log(TRACE1, "idx=[%s] item=[%s]" % (idx, item))

        job_type, job_name, original_job_name, service, extra, params = data

        try:
            if job_type == "one_time":
                self.scheduler.edit_one_time(job_name, original_job_name, service, extra, params)
            elif job_type == "interval_based":
                self.scheduler.edit_interval_based(job_name, original_job_name, service, extra, params)
            else:
                raise ZatoException("Unknow job_type=[%s]" % job_type)
            return ZATO_OK, ""
        except Exception, e:
            exc = format_exc()
            self.logger.error("_on_config_EDIT_JOB, exc=[%s]" % exc)
            return ZATO_ERROR, json.dumps(exc)

    def _on_config_DELETE_JOB(self, msg):
        """ Deletes a scheduler's job.
        """
        job_name = json.loads(msg.params["data"])
        self.scheduler.delete(job_name)

        return ZATO_OK, ""

    def _on_config_EXECUTE_JOB(self, msg):
        """ Executes a scheduler's job.
        """
        job_name = json.loads(msg.params["data"])
        self.scheduler.execute(job_name)

        return ZATO_OK, ""

################################################################################

    def _on_config_sql(self, msg):
        """ A common method for handling all SQL connection pools-related config
        requests. Must always be called from within a concrete, synchronized,
        configuration handler (such as _on_config_EDIT_SQL_CONNECTION_POOL etc.)
        """
        command = msg.command
        params = json.loads(msg.params["data"])

        command_handler = getattr(self.sql_pool_config, "_on_config_" + command)
        command_handler(params)

        # XXX: That loop could be refactored out to some common place.
        for q in self.partner_request_queues.values():
            req = self._create_ipc_config_request(msg)
            code, reason = self._send_config_request(req, q, timeout=1.0)

            if code != ZATO_OK:
                # XXX: Add the parallel server's PID/name here.
                msg = "Could not update a parallel server, server may have been left in an unstable state, reason=[%s]" % reason
                self.logger.error(msg)
                raise ZatoException(msg)

        return ZATO_OK, ""

    @synchronized()
    def _on_config_EDIT_SQL_CONNECTION_POOL(self, msg):
        """ Updates all of SQL connection pool's parameters, except for
        the password. Updates persistent storage and all parallel servers.
        This singleton server's method is synchronized in order to make sure no
        concurrent updates to the connection pool will be performed.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_CREATE_SQL_CONNECTION_POOL(self, msg):
        """ Creates a new SQL connection pool with no password set. Updates
        persistent storage and all parallel servers. This singleton server's
        method is synchronized in order to make sure no concurrent updates to
        the lists of connection pools will be performed.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_DELETE_SQL_CONNECTION_POOL(self, msg):
        """ Delete an SQL connection pools. Updates persistent storage and all
        parallel servers. This singleton server's method is synchronized in
        order to make sure no concurrent updates to the lists of connection
        pools will be performed.
        """
        return self._on_config_sql(msg)

    @synchronized()
    def _on_config_CHANGE_PASSWORD_SQL_CONNECTION_POOL(self, msg):
        """ Change the SQL connection pool's password. Updates persistent storage
        and all parallel servers. This singleton server's method is synchronized in
        order to make sure no concurrent updates to the lists of connection
        pools will be performed.
        """
        return self._on_config_sql(msg)

################################################################################
    @synchronized()
    def _on_config_ADD_TO_WSS_NONCE_CACHE(self, msg):
        # XXX: That loop could be refactored out to some common place.
        for q in self.partner_request_queues.values():
            req = self._create_ipc_config_request("ADD_TO_WSS_NONCE_CACHE",
                                                  json.loads(msg.params["data"]))
            self._send_config_request(req, q)

        return ZATO_OK, ""
'''
