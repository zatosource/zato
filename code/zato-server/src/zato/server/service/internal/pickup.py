# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

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
from zato.server.service import Service

# ################################################################################################################################

class _Logger(Service):
    pickup_data_type = None

    def handle(self):
        self.logger.info('%s data received: `%s`', self.pickup_data_type, self.request.raw_request)

# ################################################################################################################################

class OnUpdateStatic(Service):
    """ Updates a static resource in memory and file system.
    """
    class SimpleIO(object):
        input_required = ('data', 'file_name')

    def handle(self):

        input = self.request.input
        static_config = self.server.static_config

        with self.lock('{}-{}-{}'.format(self.name, self.server.name, input.data)):
            with open(os.path.join(static_config.base_dir, input.file_name), 'wb') as f:
                f.write(input.data)

        static_config.read_file(input.file_name)

# ################################################################################################################################

class UpdateStatic(Service):
    """ Picks up static files and distributes them to all server processes.
    """
    def handle(self):
        with open(self.request.raw_request['full_path'], 'rb') as f:
            self.broker_client.publish({
                'action': HOT_DEPLOY.CREATE_STATIC.value,
                'msg_type': MESSAGE_TYPE.TO_PARALLEL_ALL,
                'file_name': self.request.raw_request['file_name'],
                'data': f.read(),
            })

# ################################################################################################################################

class Conf(Service):
    """ Picks up configuration files.
    """

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
        with open(self.request.raw_request['full_path'], 'rb') as f:
            reader = csv.reader(f)
            for idx, line in enumerate(reader, 1):
                self.logger.info('CSV line #%s `%s`', idx, line)

# ################################################################################################################################
