# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os, sys
from ast import literal_eval
from ConfigParser import ConfigParser
from datetime import datetime

# Bunch
from bunch import bunchify

# Zato
from zato.cli import common_logging_conf_contents, ManageCommand
from zato.common import version as zato_version, ZATO_INFO_FILE
from zato.common.util import get_zato_command

zato_version_number_full = zato_version.replace('Zato ', '')
zato_version_number = zato_version_number_full[:5]

# ################################################################################################################################

# From -> To
MIGRATION_PATHS = {
    '1.1': '2.0.0'
}

# ################################################################################################################################

class Migrate(ManageCommand):
    """ Migrates a Zato component to the next version.
    """

# ################################################################################################################################

    def get_zato_info(self):
        return bunchify(json.loads(open(os.path.join(self.component_dir, ZATO_INFO_FILE)).read()))

    def save_zato_info(self, info):
        return open(os.path.join(self.component_dir, ZATO_INFO_FILE), 'w').write(json.dumps(info))

# ################################################################################################################################

    def update_zato_info(self, info):
        version_history = info.setdefault('version_history', [])
        update_history = info.setdefault('update_history', [])

        version_history.append(info.pop('version'))
        info.version = zato_version_number_full

        last_updated_ts = info.get('last_updated_ts', info.created_ts)
        last_updated_user_host = info.get('last_updated_user_host', info.created_user_host)

        info.last_updated_ts = datetime.utcnow().isoformat()
        info.last_updated_user_host = self._get_user_host()

        update_history.append({'timestamp':last_updated_ts, 'user_host':last_updated_user_host})

        self.save_zato_info(info)

# ################################################################################################################################

    def _exit_invalid_version(self, component_version, zato_version):
        self.logger.error('Cannot migrate from %s using %s from %s', component_version, zato_version, get_zato_command())
        sys.exit(self.SYS_ERROR.CANNOT_MIGRATE)

    def no_migration_needed(self):
        self.logger.warn('No migration to %s needed for %s', zato_version, self.component_dir)

# ################################################################################################################################

    def _ensure_proper_version(self, component_version):
        """ We can only migrate one version at a time, i.e. from 1.1 to 2.0.
        """
        _component_version = component_version.replace('Zato ', '')[:5]

        next_version = MIGRATION_PATHS.get(_component_version)
        if not next_version:
            print(1)
            self._exit_invalid_version(component_version, zato_version)

        if next_version != zato_version_number:
            print(2, next_version, zato_version_number)
            self._exit_invalid_version(component_version, zato_version)

        return _component_version

# ################################################################################################################################

    def _migrate_from_1_1_to_2_0_0_logging(self):
        logging_conf_path = os.path.join(self.component_dir, 'config', 'repo', 'logging.conf')

        cp = ConfigParser()
        cp.read(logging_conf_path)

        args = literal_eval((cp.get('handler_rotating_file_handler', 'args')))
        log_path = args[0]

        logging_conf = common_logging_conf_contents.format(log_path=log_path)
        open(logging_conf_path, 'w').write(logging_conf)

    def migrate_from_1_1_to_2_0_0_server(self):
        self._migrate_from_1_1_to_2_0_0_logging()

    def migrate_from_1_1_to_2_0_0_web_admin(self):
        self._migrate_from_1_1_to_2_0_0_logging()

    def migrate_from_1_1_to_2_0_0_load_balancer(self):
        self._migrate_from_1_1_to_2_0_0_logging()

# ################################################################################################################################

    def _on_component(self, args):
        info = self.get_zato_info()
        full_component_version = info.version

        short_component_version = self._ensure_proper_version(full_component_version)

        self.logger.debug('Migrating %s from %s to %s', self.component_dir, full_component_version, zato_version_number_full)

        getattr(self, 'migrate_from_{}_to_{}_{}'.format(short_component_version.replace('.', '_'),
            zato_version_number.replace('.', '_'), info.component.lower()))()

        self.update_zato_info(info)

        self.logger.info('Migrated %s from %s to %s', self.component_dir, full_component_version, zato_version_number_full)

    _on_server = _on_lb = _on_web_admin = _on_component

# ################################################################################################################################
