# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import csv
import os
from pathlib import PurePath

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
        self.logger.info('%s data received: `%s`', self.pickup_data_type, self.request.raw_request)

# ################################################################################################################################

class _Updater(Service):
    pickup_action = None

    def handle(self):

        self.broker_client.publish({
            'action': self.pickup_action.value,
            'msg_type': MESSAGE_TYPE.TO_PARALLEL_ALL,
            'file_name': self.request.raw_request['file_name'],
            'full_path': self.request.raw_request['full_path'],

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

zzz

class OnUpdateUserConf(Service):
    """ Updates user configuration in memory and file system.
    """
    class SimpleIO(object):
        input_required = ('data', 'file_name', 'full_path')

    def handle(self):

        # For later use
        input = self.request.input

        #
        # We have a file on input and we want to save it. However, we cannot do it under the input file_name
        # because that would trigger hot-deployment again leading to an infinite loop
        # of hot-deployment of the same file over and over again.
        #
        # This is why we first (1) add the file name to a skiplist of ignored files,
        # so that our own local notifier does not want to hot-deploy it,
        # then (2) we save the file, and then (3) we remove the name from the ignore ones.
        #

        #
        # Step (1) - Add the file name to ignored ones
        #
        self.server.worker_store.file_transfer_api.add_local_ignored_path(input.full_path)

        zzz

        return

        #
        # Step (2) - Save the file
        #
        try:
            with self.lock('{}-{}-{}'.format(self.name, self.server.name, input.file_name)):
                with open(os.path.join(self.server.user_conf_location, input.file_name), 'wb') as f:
                    if isinstance(input.data, str):
                        f.write(input.data.encode('utf8'))

                # .. the file is saved so we can update our in-RAM mirror of it ..

                conf = get_config(self.server.user_conf_location, input.file_name)
                entry = self.server.user_config.setdefault(get_user_config_name(input.file_name), Bunch())
                entry.clear()
                entry.update(conf)
        #
        # Step (3) - Remove the file name from the ignored ones
        #
        finally:
            # No matter what happened in step (2), we always remove the file from the ignored list.
            self.server.worker_store.file_transfer_api.remove_local_ignored_path(input.file_name)

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
