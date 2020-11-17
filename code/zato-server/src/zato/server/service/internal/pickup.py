# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import csv
import os

# Bunch
from bunch import Bunch

# Zato
from zato.common.broker_message import HOT_DEPLOY, MESSAGE_TYPE
from zato.common.util.api import get_config, get_user_config_name
from zato.server.service import Service

# ################################################################################################################################

class _Logger(Service):
    pickup_data_type = None

    def handle(self):
        self.logger.warn('EEE %s', self)
        self.logger.info('%s data received: `%s`', self.pickup_data_type, self.request.raw_request)

# ################################################################################################################################

class _Updater(Service):
    pickup_action = None

    def handle(self):

        self.broker_client.publish({
            'action': self.pickup_action.value,
            'msg_type': MESSAGE_TYPE.TO_PARALLEL_ALL,
            'file_name': self.request.raw_request['file_name'],

            # We use raw_data to make sure we always have access
            # to what was saved in the file, even if it is not parsed.
            'data': self.request.raw_request['raw_data']
        })

# ################################################################################################################################

class OnUpdateStatic(Service):
    """ Updates a static resource in memory and file system.
    """
    class SimpleIO(object):
        input_required = ('data', 'file_name')

    def handle(self):

        input = self.request.input
        static_config = self.server.static_config

        with self.lock('{}-{}-{}'.format(self.name, self.server.name, input.file_name)):
            with open(os.path.join(static_config.base_dir, input.file_name), 'wb') as f:
                if input.data:
                    data = input.data if isinstance(input.data, bytes) else input.data.encode('utf8')
                    f.write(data)

        static_config.read_file(input.file_name)

# ################################################################################################################################

class UpdateStatic(_Updater):
    """ Picks up static files and distributes them to all server processes.
    """
    pickup_action = HOT_DEPLOY.CREATE_STATIC

# ################################################################################################################################

class OnUpdateUserConf(Service):
    """ Updates user configuration in memory and file system.
    """
    class SimpleIO(object):
        input_required = ('data', 'file_name')

    def handle(self):
        input = self.request.input

        with self.lock('{}-{}-{}'.format(self.name, self.server.name, input.file_name)):
            with open(os.path.join(self.server.user_conf_location, input.file_name), 'wb') as f:
                f.write(input.data)

            conf = get_config(self.server.user_conf_location, input.file_name)
            entry = self.server.user_config.setdefault(get_user_config_name(input.file_name), Bunch())
            entry.clear()
            entry.update(conf)

# ################################################################################################################################

class UpdateUserConf(_Updater):
    """ Picks up user-defined config files and distributes them to all server processes.
    """
    pickup_action = HOT_DEPLOY.CREATE_USER_CONF

# ################################################################################################################################

class LogJSON(_Logger):
    """ Picks up JSON files and logs their contents.
    """
    pickup_data_type = 'JSON'

# ################################################################################################################################

class LogXML(_Logger):
    """ Picks up XML files and logs their contents.
    """
    pickup_data_type = 'XML'

# ################################################################################################################################

class LogCSV(Service):
    """ Picks up CSV files and logs their contents.
    """
    def handle(self):
        with open(self.request.raw_request['full_path'], 'r') as f:
            reader = csv.reader(f)
            for idx, line in enumerate(reader, 1):
                self.logger.info('CSV line #%s `%s`', idx, line)

# ################################################################################################################################
