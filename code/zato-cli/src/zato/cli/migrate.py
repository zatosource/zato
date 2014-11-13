# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os, sys

# Zato
from zato.cli import ManageCommand
from zato.common import version as zato_version, ZATO_INFO_FILE
from zato.common.util import get_zato_command

# ################################################################################################################################

# From -> To
MIGRATION_PATHS = {
    '1.1': '2.0'
}

# ################################################################################################################################

class Migrate(ManageCommand):
    """ Migrates a Zato component to the next version.
    """

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
        _component_version = component_version.replace('Zato ', '')[:3]
        _zato_version = zato_version.replace('Zato ', '')[:3]

        next_version = MIGRATION_PATHS.get(_component_version)
        if not next_version:
            self._exit_invalid_version(component_version, zato_version)

        if next_version != _zato_version:
            self._exit_invalid_version(component_version, zato_version)

        return _component_version, _zato_version

# ################################################################################################################################

    def migrate_from_1_1_to_2_0_server(self):
        pass

    def migrate_from_1_1_to_2_0_web_admin(self):
        pass

    def migrate_from_1_1_to_2_0_load_balancer(self):
        pass

# ################################################################################################################################

    def _on_component(self, args):
        info = json.loads(open(os.path.join(self.component_dir, ZATO_INFO_FILE)).read())
        full_component_version = info['version']

        short_component_version, short_zato_version = self._ensure_proper_version(full_component_version)

        getattr(self, 'migrate_from_{}_to_{}_{}'.format(short_component_version.replace('.', '_'),
            short_zato_version.replace('.', '_'), info['component'].lower()))()

    _on_server = _on_lb = _on_web_admin = _on_component

# ################################################################################################################################
