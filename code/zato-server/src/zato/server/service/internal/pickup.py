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
from zato.common.typing_ import dataclass, from_dict
from zato.common.util.api import get_config, get_user_config_name
from zato.common.util.open_ import open_r
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class UpdateCtx:
    data: str
    full_path: str
    file_name: str
    relative_dir: str

# ################################################################################################################################
# ################################################################################################################################

class _Logger(Service):
    pickup_data_type = None

    def handle(self):
        self.logger.info('%s data received: `%s`', self.pickup_data_type, self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class LogJSON(_Logger):
    """ Picks up JSON files and logs their contents.
    """
    pickup_data_type = 'JSON'

# ################################################################################################################################
# ################################################################################################################################

class LogXML(_Logger):
    """ Picks up XML files and logs their contents.
    """
    pickup_data_type = 'XML'

# ################################################################################################################################
# ################################################################################################################################

class LogCSV(Service):
    """ Picks up CSV files and logs their contents.
    """
    def handle(self):
        with open_r(self.request.raw_request['full_path']) as f:
            reader = csv.reader(f)
            for idx, line in enumerate(reader, 1):
                self.logger.info('CSV line #%s `%s`', idx, line)

# ################################################################################################################################
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
# ################################################################################################################################

class UpdateStatic(_Updater):
    """ Picks up static files and distributes them to all server processes.
    """
    pickup_action = HOT_DEPLOY.CREATE_STATIC

# ################################################################################################################################
# ################################################################################################################################

class UpdateUserConf(_Updater):
    """ Picks up user-defined config files and distributes them to all server processes.
    """
    pickup_action = HOT_DEPLOY.CREATE_USER_CONF

# ################################################################################################################################
# ################################################################################################################################

class _OnUpdate(Service):
    """ Updates user configuration in memory and file system.
    """
    update_type = '<update-type-_OnUpdate>'

    class SimpleIO:
        input_required = ('data', 'full_path', 'file_name', 'relative_dir')

    def handle(self):

        # For later use
        ctx = from_dict(UpdateCtx, self.request.input) # type: UpdateCtx

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
        if not ctx.relative_dir:
            file_path = ctx.file_path

        # Build relative_dir from its constituents
        else:

            relative_dir = PurePath(ctx.relative_dir)
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
            elems.append(ctx.file_name)

            file_path = os.path.join(self.server.base_dir, *elems)

        # Assign the newly constructed file_path to our input for later use
        ctx.file_path = file_path

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
            self.server.worker_store.file_transfer_api.add_local_ignored_path(ctx.file_path)

            #
            # Step (2) - Save the file
            #
            with self.lock('{}-{}-{}'.format(self.name, self.server.name, ctx.file_path)):
                with open(ctx.file_path, 'wb') as f:
                    if isinstance(ctx.data, str):
                        f.write(ctx.data.encode('utf8'))

                try:
                    # The file is saved so we can update our in-RAM mirror of it ..
                    self.logger.info('Syncing in-RAM contents of `%s` (%s)', ctx.file_path, self.update_type)

                    # The file is saved on disk so we can call our handler function to post-process it.
                    self.sync_pickup_file_in_ram(ctx)

                except Exception:
                    self.logger.warning('Could not sync in-RAM contents of `%s`, e:`%s` (%s)',
                        ctx.file_path, format_exc(), self.update_type)
                else:
                    self.logger.info('Successfully finished syncing in-RAM contents of `%s` (%s)',
                        ctx.file_path, self.update_type)

        except Exception:
            self.logger.warning('Could not update file `%s`, e:`%s`', format_exc())

        #
        # Step (3) - Remove the file name from the ignored ones
        #
        finally:

            #
            # No matter what happened in step (2), we always remove the file from the ignored list.
            #

            # Sleep for a moment to make sure the local notifier loop does not attempt
            # to pick up the file again while we are modifying it.
            sleep(2)

            self.server.worker_store.file_transfer_api.remove_local_ignored_path(ctx.file_path)

# ################################################################################################################################

    def sync_pickup_file_in_ram(self, *args, **kwargs):
        raise NotImplementedError('Should be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class OnUpdateUserConf(_OnUpdate):
    """ Updates user configuration in memory and file system.
    """
    update_type = 'user config file'

    def sync_pickup_file_in_ram(self, ctx):
        # type: (UpdateCtx) -> None
        conf_key = ctx.file_name
        conf = get_config(self.server.user_conf_location, conf_key, raise_on_error=True, log_exception=False)
        entry = self.server.user_config.setdefault(get_user_config_name(conf_key), Bunch())
        entry.clear()
        entry.update(conf)

# ################################################################################################################################
# ################################################################################################################################

class OnUpdateStatic(_OnUpdate):
    """ Updates a static resource in memory and file system.
    """
    update_type = 'static file'

    def sync_pickup_file_in_ram(self, ctx):
        # type: (UpdateCtx) -> None
        self.server.static_config.read_file(ctx.file_path, ctx.file_name)

# ################################################################################################################################
# ################################################################################################################################
