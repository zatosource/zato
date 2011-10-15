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
from thread import start_new_thread
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
    """ An HTTP task which knows how to uses ZMQ sockets.
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
    the newly created threads.
    """
    def __init__(self, message_handler, broker_token, zmq_context, 
            broker_push_addr, broker_pull_addr):
        super(_TaskDispatcher, self).__init__()
        self.message_handler = message_handler
        self.broker_token = broker_token
        self.zmq_context = zmq_context
        self.broker_push_addr = broker_push_addr
        self.broker_pull_addr = broker_pull_addr
        
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

                # It's safe to pass ZMQ contexts between threads.
                thread_data = Bunch({
                    'message_handler': self.message_handler,
                    'broker_token':self.broker_token,
                    'zmq_context': self.zmq_context,
                    'broker_push_addr': self.broker_push_addr,
                    'broker_pull_addr': self.broker_pull_addr})
                
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

        # We're in a new thread now so we can start the broker client though note
        # that the message handler will be assigned to it later on.
        thread_data.broker_client = BrokerClient('parallel', self.broker_token,
                thread_data.zmq_context, thread_data.broker_push_addr, 
                thread_data.broker_pull_addr, self.message_handler)
        
        args = Bunch({'broker_client': thread_data.broker_client})
        thread_data.broker_client.set_message_handler_args(args)
        
        thread_data.broker_client.start_subscriber()
        
        threads = self.threads
        try:
            while threads.get(thread_no):
                task = self.queue.get()
                if task is None:
                    # Special value: kill this thread.
                    break
                try:
                    task.service(thread_data)
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