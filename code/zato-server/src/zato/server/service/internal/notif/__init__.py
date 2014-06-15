# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps

# Zato
from zato.common.broker_message import NOTIF
from zato.common import DATA_FORMAT
from zato.common.util import new_cid
from zato.server.service import Service

class InvokeRunNotifier(Service):
    def handle(self):

        # Maps notification type to a service handling it
        notif_type_service = {
            'openstack_swift': 'zato.notif.cloud.openstack.swift.run-notifier',
        }

        request = {
            'payload': dumps(self.request.payload['config']),
            'service': notif_type_service[self.request.payload['config']['notif_type']],
            'target_server_token': self.server.fs_server_config.main.token,
            'cid': new_cid(),
            'data_format': DATA_FORMAT.JSON
        }

        msg = {'action': NOTIF.RUN_NOTIFIER, 'request': dumps(request)}
        self.broker_client.publish(msg)


class InitNotifiers(Service):
    def handle(self):

        # One entry for each notification type
        config_dicts = [
            self.server.worker_store.worker_config.notif_cloud_openstack_swift
        ]

        for config_dict in config_dicts:
            for value in config_dict.values():
                self.invoke(InvokeRunNotifier.get_name(), {'config': value.config})
