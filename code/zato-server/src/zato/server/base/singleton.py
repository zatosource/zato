# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta
from time import sleep

# Bunch
from zato.bunch import Bunch

# Zato
from zato.common import ENSURE_SINGLETON_JOB
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER, SINGLETON
from zato.server.base import BrokerMessageReceiver
from zato.server.scheduler import Scheduler

_accepted_messages = SCHEDULER.values() + SINGLETON.values()

class SingletonServer(BrokerMessageReceiver):
    """ A server of which one instance only may be running in a Zato container.
    Holds and processes data which can't be made parallel, such as scheduler,
    hot-deployment or on-disk configuration management.
    """
    def __init__(self, parallel_server=None, server_id=None, scheduler=None, 
                 broker_client=None, initial_sleep_time=None, is_cluster_wide=False):
        self.parallel_server = parallel_server
        self.server_id = server_id
        self.scheduler = scheduler or Scheduler()
        self.broker_client = broker_client
        self.initial_sleep_time = initial_sleep_time
        self.is_cluster_wide = is_cluster_wide
        self.logger = logging.getLogger('zato_singleton')

    def run(self, *ignored_args, **kwargs):
        # So that other moving parts - like connector subprocesses - have time
        # to initialize before the singleton server starts the scheduler.
        self.logger.debug('Sleeping for %s s', self.initial_sleep_time)
        sleep(self.initial_sleep_time)

        for name in('broker_client',):
            if name in kwargs:
                setattr(self, name, kwargs[name])

        # Initialize scheduler
        self.scheduler.singleton = self
        self.scheduler.init()

        # Start the hot-reload pickup monitor
        self.logger.info('Pickup notifier starting')
        self.pickup.watch()

    def wait_for_worker(self):
        """ OK, we have already slept for a while however this isn't neccessarily enough. The thing is, we can't publish messages
        from the scheduler yet. This would be good in itself, but we must be sure there is at least one server (worker) to handle
        the message. We don't know how many server there are in this cluster so the only thing we can do is to assume that our
        parallel_server's worker is the only one. Hence we wait until this very worker is initialized.
        """
        worker_not_ready_sleep_time = 0.25 # In seconds

        while not self.parallel_server.worker_store.is_ready:
            self.logger.info('Worker not ready, sleeping for %s s', worker_not_ready_sleep_time)
            sleep(worker_not_ready_sleep_time)

    def become_cluster_wide(self, connector_server_keep_alive_job_time, connector_server_grace_time, 
            server_id, cluster_id, starting_up):
        """ Attempts to become a connector server, the one to start the connector
        processes.
        """
        base_job_data = Bunch({
            'id': 0, # Dummy ID
            'weeks': None, 'days': None, 
            'hours': None, 'minutes': None, 
            'seconds': connector_server_keep_alive_job_time, 
            'repeats': None, 
            'extra': 'server_id:{};cluster_id:{}'.format(server_id, cluster_id),
        })
        job_data = None

        if self.parallel_server.odb.become_cluster_wide(connector_server_grace_time):
            self.is_cluster_wide = True

            # Schedule a job for letting the other servers know we're still alive
            job_data = Bunch(base_job_data.copy())
            job_data.start_date = datetime.utcnow()
            job_data.name = 'zato.server.cluster-wide-singleton-keep-alive'
            job_data.service = 'zato.server.cluster-wide-singleton-keep-alive'

        else:
            # All other singleton servers that are just starting up get this job
            # for checking whether the connector server is alive or not
            if starting_up:
                job_data = Bunch(base_job_data.copy())
                job_data.start_date = datetime.utcnow() + timedelta(seconds=10) # Let's give the other server some time to warm up
                job_data.name = ENSURE_SINGLETON_JOB
                job_data.service = 'zato.server.ensure-cluster-wide-singleton'

        if job_data:
            self.scheduler.create_interval_based(job_data, MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ALL)

        return self.is_cluster_wide

################################################################################

    def filter(self, msg):
        """ Filters out messages not meant to be received by a singleton server.
        """
        if msg.action in _accepted_messages:
            return True
        return False

    def on_broker_msg_SCHEDULER_CREATE(self, msg, *ignored_args):
        if self.is_cluster_wide:
            self.scheduler.create_edit('create', msg)

    def on_broker_msg_SCHEDULER_EDIT(self, msg, *ignored_args):
        if self.is_cluster_wide:
            self.scheduler.create_edit('edit', msg)

    def on_broker_msg_SCHEDULER_DELETE(self, msg, *ignored_args):
        if self.is_cluster_wide:
            self.scheduler.delete(msg)

    def on_broker_msg_SCHEDULER_EXECUTE(self, msg, *ignored_args):
        if self.is_cluster_wide:
            self.scheduler.execute(msg)

    def on_broker_msg_SINGLETON_CLOSE(self, msg, *ignored_args):
        self.broker_client.close()
