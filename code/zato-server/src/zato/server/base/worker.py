# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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
import logging
from copy import deepcopy
from thread import start_new_thread
from threading import local
from traceback import format_exc

# zope.server
from zope.server.http.httpserverchannel import HTTPServerChannel
from zope.server.http.httptask import HTTPTask
from zope.server.serverchannelbase import task_lock
from zope.server.taskthreads import ThreadedTaskDispatcher

# Bunch
from bunch import Bunch

# Zato
from zato.broker.zato_client import BrokerClient

logger = logging.getLogger(__name__)

class _HTTPTask(HTTPTask):
    """ An HTTP task which knows how to use ZMQ sockets.
    """
    def service(self, thread_data):
        try:
            try:
                self.start()
                self.channel.server.executeRequest(self, thread_data)
                self.finish()
            except socket.error:
                self.close_on_finish = 1
                if self.channel.adj.log_socket_errors:
                    raise
        finally:
            if self.close_on_finish:
                self.channel.close_when_done()
                
class _HTTPServerChannel(HTTPServerChannel):
    """ A subclass which uses Zato's own _HTTPTasks.
    """
    task_class = _HTTPTask
    
    def service(self, thread_data):
        """Execute all pending tasks"""
        while True:
            task = None
            task_lock.acquire()
            try:
                if self.tasks:
                    task = self.tasks.pop(0)
                else:
                    # No more tasks
                    self.running_tasks = False
                    self.set_async()
                    break
            finally:
                task_lock.release()
            try:
                task.service(thread_data)
            except:
                # propagate the exception, but keep executing tasks
                self.server.addTask(self)
                raise
        
class _TaskDispatcher(ThreadedTaskDispatcher):
    """ A task dispatcher which knows how to pass custom arguments down to
    the worker threads.
    """
    def __init__(self, pull_handler, sub_handler, broker_token, 
                 zmq_context, broker_push_addr, broker_pull_addr, broker_sub_addr):
        super(_TaskDispatcher, self).__init__()
        self.pull_handler = pull_handler
        self.sub_handler = sub_handler
        self.broker_token = broker_token
        self.zmq_context = zmq_context
        self.broker_push_addr = broker_push_addr
        self.broker_pull_addr = broker_pull_addr
        self.broker_sub_addr = broker_sub_addr
        
    def setThreadCount(self, count):
        """ Mostly copy & paste from the base classes except for the part
        that passes the arguments to the thread.
        """
        mlock = self.thread_mgmt_lock
        mlock.acquire()
        try:
            threads = self.threads
            thread_no = 0
            running = len(threads) - self.stop_count
            while running < count:
                # Start threads.
                while thread_no in threads:
                    thread_no = thread_no + 1
                threads[thread_no] = 1
                running += 1

                thread_data = Bunch()
                thread_data.broker_token = self.broker_token
                thread_data.broker_push_addr = self.broker_push_addr
                thread_data.broker_pull_addr = self.broker_pull_addr
                thread_data.broker_sub_addr = self.broker_sub_addr
                
                # Each thread gets its own copy of the initial configuration ..
                thread_data = deepcopy(thread_data)
                
                # .. though some things are OK to be shared among multiple threads.
                thread_data.zmq_context = self.zmq_context
                thread_data.broker_pull_handler = self.pull_handler
                
                start_new_thread(self.handlerThread, (thread_no, thread_data))
                
                thread_no = thread_no + 1
            if running > count:
                # Stop threads.
                to_stop = running - count
                self.stop_count += to_stop
                for n in range(to_stop):
                    self.queue.put(None)
                    running -= 1
        finally:
            mlock.release()
            
    def handlerThread(self, thread_no, thread_data):
        """ Mostly copy & paste from the base classes except for the part
        that passes the arguments to the thread.
        """
        _local = local()
        
        def _on_sub_message_handler(msg, args):
            """ Invoked for each message sent through the ZeroMQ SUB socket.
            """
            logger.error(str([msg, args, _local]))
        
        # We're in a new thread so we can start the broker client now.
        _local.broker_client = BrokerClient()
        _local.broker_client.name = 'parallel/thread'
        _local.broker_client.token = thread_data.broker_token
        _local.broker_client.zmq_context = thread_data.zmq_context
        _local.broker_client.push_addr = thread_data.broker_push_addr
        _local.broker_client.pull_addr = thread_data.broker_pull_addr
        _local.broker_client.sub_addr = thread_data.broker_sub_addr
        _local.broker_client.on_pull_handler = thread_data.broker_pull_handler
        _local.broker_client.on_sub_handler = _on_sub_message_handler
        _local.broker_client.init()
        _local.broker_client.start()
        
        threads = self.threads
        try:
            while threads.get(thread_no):
                task = self.queue.get()
                if task is None:
                    # Special value: kill this thread.
                    break
                try:
                    task.service(_local)
                except Exception, e:
                    logger.error('Exception during task {0}'.format(
                        format_exc(e)))
        finally:
            mlock = self.thread_mgmt_lock
            mlock.acquire()
            try:
                self.stop_count -= 1
                try: del threads[thread_no]
                except KeyError: pass
            finally:
                mlock.release()