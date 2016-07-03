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
from zato.common.util import invoke_startup_services
from zato.server.base import BrokerMessageReceiver

# ################################################################################################################################

messages_allowed = SCHEDULER.values() + SINGLETON.values()

# ################################################################################################################################

class SingletonServer(BrokerMessageReceiver):
    """ A server of which one instance only may be running in a Zato container. Holds and processes data which can't be made
    parallel, such as initial notifications, hot-deployment or on-disk configuration management.
    """
    def __init__(self, parallel_server=None, server_id=None,  broker_client=None, initial_sleep_time=None, is_cluster_wide=False):
        self.parallel_server = parallel_server
        self.server_id = server_id
        self.broker_client = broker_client
        self.initial_sleep_time = initial_sleep_time
        self.is_cluster_wide = is_cluster_wide
        self.initial_job_data = None
        self.logger = logging.getLogger('zato_singleton')

# ################################################################################################################################

    def run(self, *ignored_args, **kwargs):
        # So that other moving parts - like connector subprocesses - have time to initialize before the singleton server boots up.
        self.logger.debug('Sleeping for %s s', self.initial_sleep_time)
        sleep(self.initial_sleep_time)

        for name in('broker_client',):
            if name in kwargs:
                setattr(self, name, kwargs[name])

        # Start the hot-reload pickup monitor
        self.logger.info('Pickup notifier starting')
        self.pickup.watch()

# ################################################################################################################################

    def wait_for_worker(self):
        """ OK, we have already slept for a while however this isn't neccessarily enough. The thing is, we can't publish messages
        from yet. This would be good in itself, but we must be sure there is at least one server (worker) to handle
        the message. We don't know how many server there are in this cluster so the only thing we can do is to assume that our
        parallel_server's worker is the only one. Hence we wait until this very worker is initialized.
        """
        worker_not_ready_sleep_time = 0.25 # In seconds

        while not self.parallel_server.worker_store.is_ready:
            self.logger.info('Worker not ready, sleeping for %s s', worker_not_ready_sleep_time)
            sleep(worker_not_ready_sleep_time)

# ################################################################################################################################

    def init_notifiers(self):

        invoke_startup_services(
            'Singleton', 'startup_services_first_worker', self.parallel_server.fs_server_config,
            self.parallel_server.repo_location, None, 'zato.notif.init-notifiers', False, self.parallel_server.worker_store)

# ################################################################################################################################

    def filter(self, msg):
        """ Filters out messages not meant to be received by a singleton server.
        """
        self.logger.warn('666 %r', msg)
        if msg.action in messages_allowed:
            return True
        return False

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_CREATE(self, msg, *ignored_args):
        raise Exception(msg)
        #if self.is_cluster_wide:
        #    self.scheduler.create_edit('create', msg)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_EDIT(self, msg, *ignored_args):
        raise Exception(msg)
        #if self.is_cluster_wide:
        #    self.scheduler.create_edit('edit', msg)

    def on_broker_msg_SCHEDULER_DELETE(self, msg, *ignored_args):
        raise Exception(msg)
        #if self.is_cluster_wide:
        #    self.scheduler.delete(msg)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_EXECUTE(self, msg, *ignored_args):
        raise Exception(msg)
        #if self.is_cluster_wide:
        #    self.scheduler.execute(msg)

# ################################################################################################################################

    def on_broker_msg_SINGLETON_CLOSE(self, msg, *ignored_args):
        self.broker_client.close()

# ################################################################################################################################
