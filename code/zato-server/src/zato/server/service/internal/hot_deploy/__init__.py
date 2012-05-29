# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, shutil
from contextlib import closing
from datetime import datetime
from tempfile import mkdtemp, NamedTemporaryFile
from traceback import format_exc

# pip
from pip.download import is_archive_file

# Zato
from zato.common import DEPLOYMENT_STATUS
from zato.common.odb.model import DeploymentPackage, DeploymentStatus
from zato.common.util import decompress, fs_safe_now, is_python_file, visit_py_source_from_distribution
from zato.server.service.internal import AdminService

MAX_BACKUPS = 1000
_first_prefix = '0' * (len(str(MAX_BACKUPS)) - 1) # So it runs from, e.g.,  000 to 999

class Create(AdminService):
    """ Creates all the needed filesystem directories and files out of a deployment
    package stored in the ODB and starts all the services contained within the
    package.
    """
    class SimpleIO:
        input_required = ('package_id',)
        
    def _delete(self, items):
        for item in items:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
            else:
                msg = "Could not delete [{}], it's neither file nor a directory, stat:[{}]".format(item, os.stat(item))
                self.logger.warn(msg)
            
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
        
    def _deploy_file(self, current_work_dir, payload, file_name):
        f = open(file_name, 'wb')
        f.write(payload)
        f.close()
        self.server.service_store.import_services_from_file(file_name, False, current_work_dir)
        
        return True
    
    def _deploy_archive(self, current_work_dir, payload, payload_name):
        
        with NamedTemporaryFile(prefix='zato-hd', suffix=payload_name) as tf:
            tf.write(payload)
            tf.flush()

            tmp_dir = mkdtemp(prefix='zato-hd-')
            decompress(tf.name, tmp_dir)

            for py_path in visit_py_source_from_distribution(tmp_dir):
                print(333, py_path)
            
            shutil.rmtree(tmp_dir)
            
            return True
        
    def _deploy_package(self, session, package_id, payload_name, payload):
        """ Deploy a package, either a plain Python file or an archive, and update
        the deployment status.
        """
        success = False
        current_work_dir = self.server.hot_deploy_config.current_work_dir
        
        if is_python_file(payload_name):
            file_name = os.path.join(current_work_dir, payload_name)
            success = self._deploy_file(current_work_dir, payload, file_name)
        elif is_archive_file(payload_name):
            success = self._deploy_archive(current_work_dir, payload, payload_name)
            
        if success:
            self._update_deployment_status(session, package_id, DEPLOYMENT_STATUS.DEPLOYED)
        else:
            msg = 'Package id:[{}], payload_name:[{}] has not been deployed'.format(package_id, payload_name)
            self.logger.warn(msg)
    
    def _update_deployment_status(self, session, package_id, status):
        ds = session.query(DeploymentStatus).\
            filter(DeploymentStatus.package_id==package_id).\
            filter(DeploymentStatus.server_id==self.server.id).\
            one()
        ds.status = status
        ds.status_change_time = datetime.utcnow()
        
        session.add(ds)
        session.commit()
        
    def deploy_package(self, package_id):
        with closing(self.odb.session()) as session:
            dp = session.query(DeploymentPackage).\
                filter(DeploymentPackage.id==package_id).\
                one()
            
            if is_archive_file(dp.payload_name) or is_python_file(dp.payload_name):
                self._deploy_package(session, package_id, dp.payload_name, dp.payload)
            else:
                # This shouldn't really happen at all because the pickup notifier is to 
                # filter such things out but life is full of surprises
                self._update_deployment_status(session, package_id, DEPLOYMENT_STATUS.IGNORED)
                self.logger.warn('Ignoring package id:[{}], payload_name:[{}], not a Python file nor an archive'.format(dp.id, dp.payload_name))
                
    def handle(self):
        self.backup_current_work_dir()
        self.deploy_package(self.request.input.package_id)
