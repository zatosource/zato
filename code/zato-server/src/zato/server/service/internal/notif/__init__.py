# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, spawn

# Zato
from zato.server.service import Service
from zato.server.service.internal import AdminService

# ################################################################################################################################

class InvokeRunNotifier(Service):
    def handle(self):

        # Maps notification type to a service handling it
        notif_type_service = {
            'openstack_swift': 'zato.notif.cloud.openstack.swift.run-notifier',
            'sql': 'zato.notif.sql.run-notifier',
        }

        '''request = {
            'payload': dumps(self.request.payload['config']),
            'service': notif_type_service[self.request.payload['config']['notif_type']],
            'target_server_token': self.server.fs_server_config.main.token,
            'cid': new_cid(),
            'data_format': DATA_FORMAT.JSON
        }
        '''

        spawn(self.invoke, notif_type_service[self.request.payload['config']['notif_type']], self.request.payload['config'])

# ################################################################################################################################

class InitNotifiers(Service):
    def handle(self):

        # One entry for each notification type
        config_dicts = [
            self.server.worker_store.worker_config.notif_cloud_openstack_swift,
            self.server.worker_store.worker_config.notif_sql,
        ]

        for config_dict in config_dicts:
            for value in config_dict.values():
                self.invoke(InvokeRunNotifier.get_name(), {'config': value.config})

# ################################################################################################################################

class NotifierService(AdminService):
    notif_type = None

    def run_notifier_impl(self, config):
        raise NotImplementedError('Needs to be overridden in subclasses')

    def run_notifier(self, config):
        """ Invoked as a greenlet - fetches data from a remote data source and invokes the target service.
        """
        # It's possible our config has changed since the last time we run so we need to check the current one.
        current_config = self.server.worker_store.get_notif_config(self.notif_type, config.name)

        # The notification definition has been deleted in between the invocations of ours so we need to stop now.
        if not current_config:
            self.keep_running = False
            return

        if not current_config.config['is_active']:
            return

        # Ok, overwrite old config with current one.
        config.update(current_config.config)

        self.environ['notif_sleep_interval'] = config.interval

        # Grab a distributed lock so we are sure it is only us who connects to pull newest data.
        with self.lock('zato:lock:{}:{}'.format(self.notif_type, config.name), block=None):
            self.run_notifier_impl(config)

    def handle(self):
        self.keep_running = True
        config = bunchify(self.request.payload)
        self.environ['notif_sleep_interval'] = config.interval

        while self.keep_running:
            spawn(self.run_notifier, config)
            sleep(self.environ['notif_sleep_interval'])

        self.logger.info('Stopped `%s` notifier `%s`', self.notif_type, config.name)
