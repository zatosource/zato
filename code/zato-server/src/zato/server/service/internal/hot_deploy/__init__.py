# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from base64 import b64decode
from dataclasses import dataclass
from errno import ENOENT
from time import sleep
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.common.util.api import is_python_file, is_archive_file, publish_file
from zato.common.util.file_system import fs_safe_now
from zato.common.util.open_ import open_w
from zato.common.util.python_ import import_module_by_path
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anylistnone, commoniter, intlist, strbytes, strlist, strset
    from zato.server.service.store import InRAMService
    strbytes = strbytes
    InRAMService = InRAMService

# ################################################################################################################################

MAX_BACKUPS = 1000
_first_prefix = '0' * (len(str(MAX_BACKUPS)) - 1) # So it runs from, e.g.,  000 to 999

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeploymentCtx:
    model_name_list:   'strlist'
    service_id_list:   'intlist'
    service_name_list: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates all the filesystem directories and files out of a deployment package stored in the ODB.
    """
    class SimpleIO(AdminSIO):
        input_required = 'payload', 'payload_name'
        input_optional = 'is_startup'
        output_optional = AsIs('services_deployed'), 'success'

# ################################################################################################################################

    def _delete(self, items:'commoniter') -> 'None':
        for item in items:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
            else:
                msg = 'Could not delete `%s`, it is neither file nor a directory, stat:`%s`'
                self.logger.warning(msg, item, os.stat(item))

# ################################################################################################################################

    def _backup_last(self, fs_now:'str', current_work_dir:'str', backup_format:'str', last_backup_work_dir:'str') -> 'None':

        # We want to grab the directory's contents right now, before we place the
        # new backup in there
        last_backup_contents = []
        for item in os.listdir(last_backup_work_dir):
            last_backup_contents.append(os.path.join(last_backup_work_dir, item))

        # First make the backup to the special 'last' directory
        last_backup_path = os.path.join(last_backup_work_dir, fs_now)

        _ = shutil.make_archive(last_backup_path, backup_format, current_work_dir, verbose=True, logger=None)

        # Delete everything previously found in the last backup directory
        self._delete(last_backup_contents)

# ################################################################################################################################

    def _backup_linear_log(
        self,
        fs_now,           # type: str
        current_work_dir, # type: str
        backup_format,    # type: str
        backup_work_dir,  # type: str
        backup_history,   # type: int
    ) -> 'None':

        delete_previous_backups = False

        # Aren't we going to exceed the limit?
        max_backups = min(backup_history, MAX_BACKUPS)
        backup_contents = []

        for item in os.listdir(backup_work_dir):
            item = os.path.join(backup_work_dir, item)

            # We tally files only and assume each file must be one of ours so we can safely drop it if need be
            if os.path.isfile(item):
                backup_contents.append(item)

        len_backups = len(backup_contents)

        # It's the first backup or we're past the limit so we need a fresh prefix
        if not len_backups or len_backups >= max_backups:
            next_prefix = _first_prefix
        else:
            next_prefix = str(len_backups).zfill(len(_first_prefix))

        # Also, we need to delete previous backups if we're starting anew
        if len_backups >= max_backups:
            delete_previous_backups = True

        backup_name = '{}-{}'.format(next_prefix, fs_now)
        backup_path = os.path.join(backup_work_dir, backup_name)
        _ = shutil.make_archive(backup_path, backup_format, current_work_dir, verbose=True, logger=None)

        if delete_previous_backups:
            self._delete(backup_contents)

# ################################################################################################################################

    def backup_current_work_dir(self):

        # Save a few keystrokes
        last_backup_work_dir = self.server.hot_deploy_config.last_backup_work_dir
        current_work_dir = self.server.hot_deploy_config.current_work_dir
        backup_work_dir = self.server.hot_deploy_config.backup_work_dir
        backup_history = self.server.hot_deploy_config.backup_history
        backup_format = self.server.hot_deploy_config.backup_format

        # Safe to use as a directory name
        fs_now = fs_safe_now()

        # Store the last backup
        self._backup_last(fs_now, current_work_dir, backup_format, last_backup_work_dir)

        # Now store the same thing in the linear log of backups
        self._backup_linear_log(fs_now, current_work_dir, backup_format, backup_work_dir, backup_history)

# ################################################################################################################################

    def _redeploy_module_dependencies(self, file_name:'str') -> 'None':

        # Reload the module so its newest contents is in sys path ..
        mod_info = import_module_by_path(file_name)

        # .. we enter here if the reload succeeded ..
        if mod_info:

            # .. get all the files with that are making use of this module ..
            # .. which may mean both files with services or models ..
            file_name_list = self.server.service_store.get_module_importers(mod_info.name)

            # .. and redeploy all such files.

            for item in file_name_list:

                # Publish the file to the broker
                _ = publish_file(self.server.broker_client, self.cid, item)

# ################################################################################################################################

    def _deploy_models(self, current_work_dir:'str', model_file_name:'str') -> 'strset':

        # This returns details of all the model classes deployed from the file
        model_info_list = self.server.service_store.import_models_from_file(
            model_file_name,
            False,
            current_work_dir,
        )

        # .. extract unique names only ..
        model_name_list = {item.name for item in model_info_list}

        # .. if we have deployed any models ..
        if model_name_list:

            # .. redeploy all the modules that depend on the one we have just deployed ..
            self._redeploy_module_dependencies(model_file_name)

        # .. and return to the caller the list of models deployed.
        return model_name_list

# ################################################################################################################################

    def _deploy_services(self, current_work_dir:'str', service_file_name:'str') -> 'intlist':

        # Local aliases
        service_id_list:'intlist' = []

        # This returns details of all the model classes deployed from the file
        service_info_list = self.server.service_store.import_services_from_anywhere(service_file_name, current_work_dir)

        # .. if we have deployed any models ..
        for service in service_info_list.to_process: # type: ignore

            # .. add type hints ..
            service = cast_('InRAMService', service)

            # .. extract the ID of the deployed service ..
            service_id = self.server.service_store.impl_name_to_id[service.impl_name]

            # .. append it for later use ..
            service_id_list.append(service_id)

            # .. redeploy all the modules that depend on the one we have just deployed ..
            self._redeploy_module_dependencies(service.source_code_info.path)

        # .. and return to the caller the list of IDs of all the services deployed.
        return service_id_list

# ################################################################################################################################

    def _deploy_file(
        self,
        current_work_dir, # type: str
        payload,          # type: any_
        file_name,        # type: str
        should_deploy_in_place # type: bool
    ) -> 'DeploymentCtx':

        if not should_deploy_in_place:
            with open(file_name, 'wb') as f:
                _ = f.write(payload)

        model_name_list = self._deploy_models(current_work_dir, file_name)
        service_id_list = self._deploy_services(current_work_dir, file_name)

        ctx = DeploymentCtx()
        ctx.model_name_list = model_name_list # type: ignore
        ctx.service_id_list = service_id_list
        ctx.service_name_list = [self.server.service_store.get_service_name_by_id(elem) for elem in service_id_list]

        return ctx

# ################################################################################################################################

    def _deploy_package(
        self,
        payload,      # type: str
        payload_name, # type: str
    ) -> 'anylistnone':
        """ Deploy a package, either a plain Python file or an archive, and update
        the deployment status.
        """

        should_deploy_in_place = True

        # Local objects
        if should_deploy_in_place:
            work_dir = os.path.dirname(payload_name)
        else:
            work_dir:'str' = self.server.hot_deploy_config.current_work_dir

        file_name = os.path.join(work_dir, payload_name)

        # Deploy some objects of interest from the file ..
        ctx = self._deploy_file(work_dir, payload, file_name, should_deploy_in_place)

        # We enter here if there were some models or services that we deployed ..
        if ctx.model_name_list or ctx.service_name_list:

            # .. report any models found ..
            if ctx.model_name_list:
                self._report_deployment(file_name, ctx.model_name_list, 'model')

            # .. report any services found ..
            if ctx.service_name_list:
                self._report_deployment(file_name, ctx.service_name_list, 'service')

            # .. our callers only need services ..
            return ctx.service_id_list

        # .. we could not find anything to deploy in the file.
        else:
            # Log only if payload does not point to our own store.py module.
            if payload_name != 'store.py':
                msg = 'No services nor models were deployed from module `%s`'
                self.logger.info(msg, payload_name)

# ################################################################################################################################

    def _report_deployment(self, file_name:'str', items:'anylist', noun:'str') -> 'None':
        msg = 'Deployed %s {}%sfrom `%s` -> %s'.format(noun)
        len_items = len(items)
        suffix = 's ' if len_items > 1 else ' '
        self.logger.info(msg, len_items, suffix, file_name, sorted(items))

# ################################################################################################################################

    def deploy_package(self, payload:'str', payload_name:'str') -> 'any_':

        if is_archive_file(payload_name) or is_python_file(payload_name):
            return self._deploy_package(payload, payload_name)
        else:
            self.logger.warning('Ignoring package id:`%s`, payload_name:`%s`, not a Python file nor an archive', payload_name)

# ################################################################################################################################

    def handle(self):

        payload = self.request.input.payload
        payload_name = self.request.input.payload_name

        # If it's just a file name, it means it must've been uploaded via the plugin,
        # so we need to save it in our local deployment directory and it will be picked up
        # by a background listener, which will in turn invokes again, but this time the file
        # will be already on disk. But we need to do it only for files that are not internal ones.

        internal_path = os.path.join('server', 'service', 'internal')
        payload_name = os.path.normpath(payload_name)

        is_external = internal_path not in payload_name
        is_relative = not os.path.isabs(payload_name)

        if is_external and is_relative:

            full_path = os.path.join(self.server.hot_deploy_config.pickup_dir, payload_name)
            full_path = os.path.abspath(full_path)

            payload = b64decode(payload)
            payload = payload.decode('utf8')

            with open_w(full_path) as f:
                _ = f.write(payload)

            # All went fine
            self.response.payload.success = True

            # Now, we can return early
            return

        server_token = self.server.fs_server_config.main.token
        lock_name = '{}{}:{}'.format('uploading', server_token, payload_name)

        ttl = self.server.deployment_lock_expires
        block = self.server.deployment_lock_timeout

        # Now, it's possible we don't have the broker_client yet - this will happen if we are deploying
        # missing services found on other servers during our own server's startup. In that case we just
        # need to wait a moment for the server we are on to fully initialize.
        while not self.server.broker_client:
            sleep(0.2)

        with self.lock(lock_name, ttl, block):

            try:
                self.backup_current_work_dir()
                services_deployed = self.deploy_package(payload, payload_name) or []

                # Go through all services deployed, check if any needs post-processing
                # and if does, call the relevant function and clear the flag.
                service_store = self.server.service_store
                needs_post_deploy_attr = service_store.needs_post_deploy_attr

                for service_id in services_deployed:

                    service_info = service_store.get_service_info_by_id(service_id)
                    class_ = service_info['service_class']

                    if getattr(class_, needs_post_deploy_attr, None):
                        service_store.post_deploy(class_)
                        delattr(class_, needs_post_deploy_attr)

                self.response.payload.services_deployed = services_deployed

            except OSError as e:
                if e.errno == ENOENT:
                    self.logger.debug('Caught ENOENT e:`%s`', format_exc())
                else:
                    raise

# ################################################################################################################################
# ################################################################################################################################
