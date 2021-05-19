# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import csv
import os
from pathlib import PurePath
from time import sleep
from traceback import format_exc

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
            'full_path': self.request.raw_request['full_path'],
            'file_name': self.request.raw_request['file_name'],
            'relative_dir': self.request.raw_request['relative_dir'],

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
        input_required = ('data', 'full_path', 'file_name', 'relative_dir')

    def handle(self):

        # For later use
        input = self.request.input

        #
        # First, we need to combine relative_dir with our own server's root directory.
        # This is needed because other servers may be in different root directories
        # yet the relative_dir to the file will be the same.
        #
        # For instance, we can have server directories as such
        #
        # /home/zato/env/server1/pickup/incoming/user-conf
        # /zatoroot/server2/pickup/incoming/user-conf
        # C:\prod\zatoserver3\pickup\incoming\user-conf
        #
        # In each case relative_dir is the same  - pickup/incoming/user-conf (slashes do not matter) -
        # but the path leading to it may be different.
        #
        # However, if we do not have relative_dir on input, meaning the event notifier could not build it,
        # we just use the full_path from input which will be always available.
        #

        # Use tue full path from input ..
        if not input.relative_dir:
            file_path = input.file_path

        # Build relative_dir from its constituents
        else:

            relative_dir = PurePath(input.relative_dir)
            relative_dir_parts = relative_dir.parts

            #
            # Now, we can combine all the three elements to give us the full path to save the file under.
            #
            # * Our server directory
            # * The relative path to the file
            # * The actual file name
            #
            elems = []
            elems.extend(relative_dir_parts)
            elems.append(input.file_name)

            file_path = os.path.join(self.server.base_dir, *elems)

        #
        # We have a file on input and we want to save it. However, we cannot do it under the input file_name
        # because that would trigger hot-deployment again leading to an infinite loop
        # of hot-deployment of the same file over and over again.
        #
        # This is why we first (1) add the file name to a skiplist of ignored files,
        # so that our own local notifier does not want to hot-deploy it,
        # then (2) we save the file, and then (3) we remove the name from the ignore ones.
        #

        try:

            #
            # Step (1) - Add the file name to ignored ones
            #
            self.server.worker_store.file_transfer_api.add_local_ignored_path(file_path)

            #
            # Step (2) - Save the file
            #
            with self.lock('{}-{}-{}'.format(self.name, self.server.name, file_path)):
                with open(file_path, 'wb') as f:
                    if isinstance(input.data, str):
                        f.write(input.data.encode('utf8'))

                # .. the file is saved so we can update our in-RAM mirror of it ..
                self.logger.info('Syncing in-RAM contents of `%s`', file_path)

                try:
                    conf = get_config(self.server.user_conf_location, file_path, raise_on_error=True, log_exception=False)
                    entry = self.server.user_config.setdefault(get_user_config_name(file_path), Bunch())
                    entry.clear()
                    entry.update(conf)
                except Exception:
                    self.logger.warn('Could not sync in-RAM contents of `%s`, e:`%s`', file_path, format_exc())
                else:
                    self.logger.info('Finished syncing in-RAM contents of `%s`', file_path)

        except Exception:
            self.logger.warn('Could not update file `%s`, e:`%s`', format_exc())

        #
        # Step (3) - Remove the file name from the ignored ones
        #
        finally:

            #
            # No matter what happened in step (2), we always remove the file from the ignored list.
            #

            # Sleep for a moment to make sure the local notifier loop does not attempt
            # to pick up the file again while we are modifying it.
            sleep(1)

            self.server.worker_store.file_transfer_api.remove_local_ignored_path(file_path)

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
