# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, shutil
from contextlib import closing
from datetime import datetime
from errno import ENOENT
from time import sleep
from traceback import format_exc

# anyjson
from anyjson import dumps

# Python 2/3 compatibility
from builtins import bytes

# Zato
from zato.common import DEPLOYMENT_STATUS, KVDB
from zato.common.broker_message import HOT_DEPLOY
from zato.common.odb.model import DeploymentPackage, DeploymentStatus
from zato.common.util import fs_safe_now, is_python_file, is_archive_file, new_cid
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # Zato
    from zato.server.service.store import InRAMService

    # For pyflakes
    InRAMService = InRAMService

# ################################################################################################################################

MAX_BACKUPS = 1000
_first_prefix = '0' * (len(str(MAX_BACKUPS)) - 1) # So it runs from, e.g.,  000 to 999

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
                self.logger.warn(msg, item, os.stat(item))

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

    def _deploy_file(self, current_work_dir, payload, file_name):

        f = open(file_name, 'w')
        f.write(payload.decode('utf8') if isinstance(payload, bytes) else payload)
        f.close()

        services_deployed = []
        info = self.server.service_store.import_services_from_anywhere(file_name, current_work_dir)

        for service in info.to_process: # type: InRAMService

            service_id = self.server.service_store.impl_name_to_id[service.impl_name]
            services_deployed.append(service_id)

            msg = {}
            msg['cid'] = new_cid()
            msg['service_id'] = service_id
            msg['service_name'] = service.name
            msg['service_impl_name'] = service.impl_name
            msg['action'] = HOT_DEPLOY.AFTER_DEPLOY.value

            self.broker_client.publish(msg)

        return services_deployed

# ################################################################################################################################

    def _deploy_package(self, session, package_id, payload_name, payload):
        """ Deploy a package, either a plain Python file or an archive, and update
        the deployment status.
        """
        current_work_dir = self.server.hot_deploy_config.current_work_dir
        file_name = os.path.join(current_work_dir, payload_name)
        services_deployed = self._deploy_file(current_work_dir, payload, file_name)

        if services_deployed:
            self._update_deployment_status(session, package_id, DEPLOYMENT_STATUS.DEPLOYED)
            msg = 'Uploaded package id:`%s`, payload_name:`%s`'
            self.logger.info(msg, package_id, payload_name)
            return services_deployed
        else:
            msg = 'No services were deployed from module `%s`'
            self.logger.warn(msg, payload_name)

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

        if is_archive_file(dp.payload_name) or is_python_file(dp.payload_name):
            return self._deploy_package(session, package_id, dp.payload_name, dp.payload)
        else:
            # This shouldn't really happen at all because the pickup notifier is to
            # filter such things out but life is full of surprises
            self._update_deployment_status(session, package_id, DEPLOYMENT_STATUS.IGNORED)
            self.logger.warn(
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
                    if not self.server.kvdb.conn.get(already_deployed_flag):
                        self.backup_current_work_dir()

                        self.server.kvdb.conn.set(already_deployed_flag, dumps({'create_time_utc':datetime.utcnow().isoformat()}))
                        self.server.kvdb.conn.expire(already_deployed_flag, self.server.deployment_lock_expires)

                    # .. all workers get here.
                    services_deployed = self.deploy_package(self.request.input.package_id, session)

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

                except(IOError, OSError) as e:
                    if e.errno == ENOENT:
                        self.logger.debug('Caught ENOENT e:`%s`', format_exc())
                    else:
                        raise

# ################################################################################################################################
# ################################################################################################################################
