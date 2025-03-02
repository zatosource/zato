# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
from zato.common.api import EnvFile, FILE_TRANSFER
from zato.common.broker_message import ValueConstant, HOT_DEPLOY, MESSAGE_TYPE
from zato.common.typing_ import cast_, dataclass, from_dict, optional
from zato.common.util.api import get_config, get_user_config_name
from zato.common.util.open_ import open_r
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class UpdateCtx:
    data: str
    full_path: str
    file_name: str
    relative_dir: optional[str]

# ################################################################################################################################
# ################################################################################################################################

class _Logger(Service):
    pickup_data_type = None

    def handle(self) -> 'None':
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
    def handle(self) -> 'None':
        raw_request = cast_('stranydict', self.request.raw_request)
        with open_r(raw_request['full_path']) as f:
            reader = csv.reader(f)
            for idx, line in enumerate(reader, 1):
                self.logger.info('CSV line #%s `%s`', idx, line)

# ################################################################################################################################
# ################################################################################################################################

class _Updater(Service):
    pickup_action: 'ValueConstant'

    def handle(self) -> 'None':
        raw_request = cast_('stranydict', self.request.raw_request)

        self.broker_client.publish({
            'action': self.pickup_action.value,
            'msg_type': MESSAGE_TYPE.TO_PARALLEL_ALL,
            'full_path': raw_request['full_path'],
            'file_name': raw_request['file_name'],
            'relative_dir': raw_request['relative_dir'],

            # We use raw_data to make sure we always have access
            # to what was saved in the file, even if it is not parsed.
            'data': raw_request['raw_data']
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

class UpdateEnmasse(Service):
    """ Runs an enmasse file if its contents is changed.
    """
    def handle(self) -> 'None':

        # Add type hints ..
        raw_request = cast_('stranydict', self.request.raw_request)

        # .. extract the path to the enmasse file ..
        enmasse_file_path = raw_request['full_path']

        # .. ignore files with environment variables ..
        if enmasse_file_path.endswith('env.ini'):
            return

        # .. and execute it now.
        _ = self.commands.run_enmasse_async(enmasse_file_path)

# ################################################################################################################################
# ################################################################################################################################

class _OnUpdate(Service):
    """ Updates user configuration in memory and file system.
    """
    update_type = '<update-type-_OnUpdate>'

    class SimpleIO:
        input_required = ('data', 'full_path', 'file_name', 'relative_dir')

    def handle(self) -> 'None':

        # For later use
        ctx = from_dict(UpdateCtx, self.request.input) # type: ignore

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
        # However, if we do not have relative_dir on input, or if it is the default one,
        # meaning in either case that the event notifier could not build it,
        # we just use the full_path from input which will be always available.
        #

        # Use tue full path from input ..
        if (not ctx.relative_dir) or (ctx.relative_dir == FILE_TRANSFER.DEFAULT.RelativeDir):
            full_path = ctx.full_path

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

            full_path = os.path.join(self.server.base_dir, *elems)

        # Assign the newly constructed full_path to our input for later use
        ctx.full_path = full_path

        #
        # We have a file on input and we want to save it. However, we cannot do it under the input file_name
        # because that would trigger hot-deployment again leading to an infinite loop
        # of hot-deployment of the same file over and over again.
        #
        # This is why we first (1) add the file name to a skiplist of ignored files,
        # so that our own local notifier does not want to hot-deploy it,
        # then (2) we save the file, and then (3) we remove the name from the ignored ones.
        #

        try:

            #
            # Step (1) - Add the file name to ignored ones
            #
            self.server.worker_store.file_transfer_api.add_local_ignored_path(ctx.full_path)

            #
            # Step (2) - Save the file
            #
            with self.lock('{}-{}-{}'.format(self.name, self.server.name, ctx.full_path)): # type: ignore

                with open(ctx.full_path, 'wb') as f:
                    _ = f.write(ctx.data.encode('utf8'))

                # Reusable
                update_type = self.get_update_type(ctx.full_path)

                try:
                    # The file is saved so we can update our in-RAM mirror of it ..
                    self.logger.info('Syncing in-RAM contents of `%s` (%s)', ctx.full_path, update_type)

                    # The file is saved on disk so we can call our handler function to post-process it.
                    self.sync_pickup_file_in_ram(ctx)

                except Exception:
                    self.logger.warning('Could not sync in-RAM contents of `%s`, e:`%s` (%s)',
                        ctx.full_path, format_exc(), update_type)
                else:
                    self.logger.info('Successfully finished syncing in-RAM contents of `%s` (%s)',
                        ctx.full_path, update_type)

        except Exception:
            self.logger.warning('Could not update file `%s`, e:`%s`', ctx.full_path, format_exc())

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

            self.server.worker_store.file_transfer_api.remove_local_ignored_path(ctx.full_path)

# ################################################################################################################################

    def _get_update_type(self, file_path:'str') -> 'str':
        if '.zrules' in file_path:
            return 'rules'
        else:
            return ''

# ################################################################################################################################

    def get_update_type(self, file_path:'str') -> 'str':

        update_type = self._get_update_type(file_path) or self.update_type
        return update_type

# ################################################################################################################################

    def sync_pickup_file_in_ram(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('Should be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class OnUpdateUserConf(_OnUpdate):
    """ Updates user configuration in memory and file system.
    """
    update_type = 'user config file'

    def _is_env_file(self, file_path:'str') -> 'bool':
        return EnvFile.Default in file_path

    def _is_rules_file(self, file_path:'str') -> 'bool':
        return file_path.endswith('.zrules')

# ################################################################################################################################

    def sync_pickup_file_in_ram(self, ctx:'UpdateCtx') -> 'None':

        # We enter here if this is a file with environment variables ..
        if self._is_env_file(ctx.full_path):
            self.server.update_environment_variables_from_file(ctx.full_path)

        # .. or a rules file ..
        elif self._is_rules_file(ctx.full_path):
            _ = self.server.rules.load_rules_from_file(ctx.full_path)

        # .. otherwise, this is a file with user configuration.
        else:
            conf_key = ctx.file_name
            conf_base_dir = os.path.dirname(ctx.full_path)
            conf = get_config(conf_base_dir, conf_key, raise_on_error=True, log_exception=False)

            user_config_name = get_user_config_name(conf_key)
            entry:'Bunch' = self.server.user_config.setdefault(user_config_name, Bunch())
            entry.clear()
            entry.update(conf)

# ################################################################################################################################

    def _get_update_type(self, file_path:'str') -> 'str':

        if self._is_env_file(file_path):
            return EnvFile.Default
        elif self._is_rules_file(file_path):
            return 'rules'
        else:
            return self.update_type

# ################################################################################################################################
# ################################################################################################################################

class OnUpdateStatic(_OnUpdate):
    """ Updates a static resource in memory and file system.
    """
    update_type = 'static file'

    def sync_pickup_file_in_ram(self, ctx:'UpdateCtx') -> 'None':
        _:'any_' = self.server.static_config.read_file(ctx.full_path, ctx.file_name)

# ################################################################################################################################
# ################################################################################################################################
