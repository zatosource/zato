# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import gc
import os
import shutil
from contextlib import closing
from datetime import datetime
from errno import ENOENT
from importlib import import_module
from inspect import getsourcefile
from json import loads
from time import sleep
from traceback import format_exc

# Zato
from zato.common.api import DEPLOYMENT_STATUS, KVDB
from zato.common.broker_message import HOT_DEPLOY
from zato.common.json_internal import dumps
from zato.common.odb.model import DeploymentPackage, DeploymentStatus
from zato.common.util.api import is_python_file, is_archive_file, new_cid
from zato.common.util.file_system import fs_safe_now
from zato.server.service import AsIs, dataclass
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

if 0:

    from zato.server.service.store import InRAMService
    InRAMService = InRAMService

# ################################################################################################################################

MAX_BACKUPS = 1000
_first_prefix = '0' * (len(str(MAX_BACKUPS)) - 1) # So it runs from, e.g.,  000 to 999

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeploymentCtx:
    model_name_list:   list
    service_id_list:   list
    service_name_list: list

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates all the filesystem directories and files out of a deployment package stored in the ODB.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_hot_deploy_create_request'
        response_elem = 'zato_hot_deploy_create_response'
        input_required = ('package_id',)
        input_optional = ('is_startup',)
        output_optional = (AsIs('services_deployed'),)

# ################################################################################################################################

    def _delete(self, items):
        for item in items:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
            else:
                msg = "Could not delete `%s`, it's neither file nor a directory, stat:`%s`"
                self.logger.warning(msg, item, os.stat(item))

# ################################################################################################################################

    def _backup_last(self, fs_now, current_work_dir, backup_format, last_backup_work_dir):

        # We want to grab the directory's contents right now, before we place the
        # new backup in there
        last_backup_contents = []
        for item in os.listdir(last_backup_work_dir):
            last_backup_contents.append(os.path.join(last_backup_work_dir, item))

        # First make the backup to the special 'last' directory
        last_backup_path = os.path.join(last_backup_work_dir, fs_now)

        shutil.make_archive(last_backup_path, backup_format, current_work_dir, verbose=True, logger=self.logger)

        # Delete everything previously found in the last backup directory
        self._delete(last_backup_contents)

# ################################################################################################################################

    def _backup_linear_log(self, fs_now, current_work_dir, backup_format, backup_work_dir, backup_history):

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
        shutil.make_archive(backup_path, backup_format, current_work_dir, verbose=True, logger=self.logger)

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

    def _deploy_models(self, current_work_dir, file_name):
        # type: (str, str) -> list

        # This returns names of all the model classes deployed from the file
        model_name_list = set(self.server.service_store.import_models_from_file(file_name, False, current_work_dir))

        # A set of Python objects, each representing a model class (rather than its name)
        model_classes = set()

        # All the modules to be reloaded due to changes to the data model
        to_auto_deploy = set()

        for item in gc.get_objects():

            # It may be None in case it has been already GC-collected
            if item is not None:
                if isinstance(item, type):
                    item_impl_name = '{}.{}'.format(item.__module__, item.__name__)
                    if item_impl_name in model_name_list:
                        model_classes.add(item)

        for model_class in model_classes:
            for ref in gc.get_referrers(model_class):

                if isinstance(ref, dict):
                    mod_name = ref.get('__module__')
                    if mod_name:

                        mod = import_module(mod_name)
                        module_path = getsourcefile(mod)

                        # It is possible that the model class is deployed along
                        # with a service that uses it. In that case, we do not redeploy
                        # the service because it will be done anyway in _deploy_services,
                        # which means that we need to skip this file ..
                        if file_name != module_path:
                            to_auto_deploy.add(module_path)

        # If there are any services to be deployed ..
        if to_auto_deploy:

            # .. format lexicographically for logging ..
            to_auto_deploy = sorted(to_auto_deploy)

            #  .. nform users that we are to auto-redeploy services and why we are doing it ..
            self.logger.info('Model class `%s` changed; auto-redeploying `%s`', model_class, to_auto_deploy)

            # .. go through each child service found and hot-deploy it ..
            for module_path in to_auto_deploy:
                shutil.copy(module_path, self.server.hot_deploy_config.pickup_dir)

        return model_name_list

# ################################################################################################################################

    def _deploy_services(self, current_work_dir, file_name):
        # type: (str, str) -> list

        service_id_list = []
        info = self.server.service_store.import_services_from_anywhere(file_name, current_work_dir)

        for service in info.to_process: # type: InRAMService

            service_id = self.server.service_store.impl_name_to_id[service.impl_name]
            service_id_list.append(service_id)

            msg = {}
            msg['cid'] = new_cid()
            msg['service_id'] = service_id
            msg['service_name'] = service.name
            msg['service_impl_name'] = service.impl_name
            msg['action'] = HOT_DEPLOY.AFTER_DEPLOY.value

            self.broker_client.publish(msg)

        return service_id_list

# ################################################################################################################################

    def _deploy_file(self, current_work_dir, payload, file_name, should_deploy_in_place):
        # type: (str, object, str) -> DeploymentCtx

        if not should_deploy_in_place:
            with open(file_name, 'w', encoding='utf-8') as f:
                payload = payload.decode('utf8') if isinstance(payload, bytes) else payload
                f.write(payload)

        model_name_list = self._deploy_models(current_work_dir, file_name)
        service_id_list = self._deploy_services(current_work_dir, file_name)

        ctx = DeploymentCtx()
        ctx.model_name_list = model_name_list
        ctx.service_id_list = service_id_list
        ctx.service_name_list = [self.server.service_store.get_service_name_by_id(elem) for elem in service_id_list]

        return ctx

# ################################################################################################################################

    def _deploy_package(self, session, package_id, payload_name, payload, should_deploy_in_place, in_place_dir_name):
        """ Deploy a package, either a plain Python file or an archive, and update
        the deployment status.
        """
        # type: (object, int, str, str)

        # Local objects
        if should_deploy_in_place:
            work_dir = in_place_dir_name
        else:
            work_dir = self.server.hot_deploy_config.current_work_dir

        file_name = os.path.join(work_dir, payload_name)

        # Deploy some objects of interest from the file ..
        ctx = self._deploy_file(work_dir, payload, file_name, should_deploy_in_place)

        # We enter here if there were some models or services that we deployed ..
        if ctx.model_name_list or ctx.service_name_list:

            # .. no matter what kind of objects we found, the package has been deployed ..
            self._update_deployment_status(session, package_id, DEPLOYMENT_STATUS.DEPLOYED)

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
                self.logger.warning(msg, payload_name)

# ################################################################################################################################

    def _report_deployment(self, file_name, items, noun):
        # type: (str, list, str)
        msg = 'Deployed %s {}%sfrom `%s` -> %s'.format(noun)
        len_items = len(items)
        suffix = 's ' if len_items > 1 else ' '
        self.logger.info(msg, len_items, suffix, file_name, sorted(items))

# ################################################################################################################################

    def _update_deployment_status(self, session, package_id, status):
        ds = session.query(DeploymentStatus).\
            filter(DeploymentStatus.package_id==package_id).\
            filter(DeploymentStatus.server_id==self.server.id).\
            one()
        ds.status = status
        ds.status_change_time = datetime.utcnow()

        session.add(ds)
        session.commit()

# ################################################################################################################################

    def deploy_package(self, package_id, session):
        dp = self.get_package(package_id, session)

        # Load JSON details so that we can find out if we are to hot-deploy in place or not ..
        details = loads(dp.details)

        should_deploy_in_place = details['should_deploy_in_place']
        in_place_dir_name = os.path.dirname(details['fs_location'])

        if is_archive_file(dp.payload_name) or is_python_file(dp.payload_name):
            return self._deploy_package(session, package_id, dp.payload_name, dp.payload,
                should_deploy_in_place, in_place_dir_name)
        else:
            # This shouldn't really happen at all because the pickup notifier is to
            # filter such things out but life is full of surprises
            self._update_deployment_status(session, package_id, DEPLOYMENT_STATUS.IGNORED)

            # Log a warning but only if it is not about a compiled bytecode file.
            if not dp.payload_name.endswith('.pyc'):
                self.logger.warning(
                    'Ignoring package id:`%s`, payload_name:`%s`, not a Python file nor an archive', dp.id, dp.payload_name)

# ################################################################################################################################

    def get_package(self, package_id, session):
        return session.query(DeploymentPackage).\
            filter(DeploymentPackage.id==package_id).\
            first()

# ################################################################################################################################

    def handle(self):
        package_id = self.request.input.package_id
        server_token = self.server.fs_server_config.main.token
        lock_name = '{}{}:{}'.format(KVDB.LOCK_PACKAGE_UPLOADING, server_token, package_id)
        already_deployed_flag = '{}{}:{}'.format(KVDB.LOCK_PACKAGE_ALREADY_UPLOADED, server_token, package_id)

        # TODO: Stuff below - and the methods used - needs to be rectified.
        # As of now any worker process will always set deployment status
        # to DEPLOYMENT_STATUS.DEPLOYED but what we really want is per-worker
        # reporting of whether the deployment succeeded or not.

        ttl = self.server.deployment_lock_expires
        block = self.server.deployment_lock_timeout

        # Now, it's possible we don't have the broker_client yet - this will happen if we are deploying
        # missing services found on other servers during our own server's startup. In that case we just
        # need to wait a moment for the server we are on to fully initialize.
        while not self.server.broker_client:
            sleep(0.2)

        with self.lock(lock_name, ttl, block):
            with closing(self.odb.session()) as session:
                try:
                    # Only one of workers will get here ..
                    if not self.server.kv_data_api.get(already_deployed_flag):
                        self.backup_current_work_dir()

                        self.server.kv_data_api.set(
                            already_deployed_flag,
                            dumps({'create_time_utc':datetime.utcnow().isoformat()}),
                            self.server.deployment_lock_expires,
                        )

                    # .. all workers get here.
                    services_deployed = self.deploy_package(self.request.input.package_id, session) or []

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
