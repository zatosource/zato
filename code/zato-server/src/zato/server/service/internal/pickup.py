# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import csv

# Zato
from zato.server.service import Service

# ################################################################################################################################

class _Logger(Service):
    pickup_data_type = None

    def handle(self):
        self.logger.info('%s data received: `%s`', self.pickup_data_type, self.request.raw_request)

# ################################################################################################################################

class Static(Service):
    """ Picks up static files.
    """

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
