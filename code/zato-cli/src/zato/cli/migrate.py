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
from cStringIO import StringIO
from datetime import datetime

# Bunch
from bunch import bunchify

# Zato
from zato.cli import common_logging_conf_contents, ManageCommand
from zato.cli.create_server import lua_zato_rename_if_exists, server_conf_template, user_conf_contents
from zato.common import version as zato_version, ZATO_INFO_FILE
from zato.common.util import get_zato_command

zato_version_number_full = zato_version.replace('Zato ', '')
zato_version_number = zato_version_number_full[:3]

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
        _component_version = component_version.replace('Zato ', '')[:3]

        next_version = MIGRATION_PATHS.get(_component_version)
        if not next_version:
            self._exit_invalid_version(component_version, zato_version)

        if next_version != zato_version_number:
            self._exit_invalid_version(component_version, zato_version)

        return _component_version

# ################################################################################################################################

    def _migrate_from_1_1_to_2_0_logging(self):
        logging_conf_path = os.path.join(self.component_dir, 'config', 'repo', 'logging.conf')

        cp = ConfigParser()
        cp.read(logging_conf_path)

        args = literal_eval((cp.get('handler_rotating_file_handler', 'args')))
        log_path = args[0]

        logging_conf = common_logging_conf_contents.format(log_path=log_path)
        open(logging_conf_path, 'w').write(logging_conf)

    def _migrate_from_1_1_to_2_0_server_conf(self):

        def update_main(section):
            gunicorn_workers = int(section['gunicorn_workers'])
            if gunicorn_workers >= 3:
                section['gunicorn_workers'] = 2

        def update_crypto(section):
            section['use_tls'] = False
            section['tls_protocol'] = 'TLSv1'
            section['tls_ciphers'] = 'EECDH+AES:EDH+AES:-SHA1:EECDH+RC4:EDH+RC4:RC4-SHA:EECDH+AES256:EDH+AES256:AES256-SHA:!aNULL:!eNULL:!EXP:!LOW:!MD5'
            section['tls_client_certs'] = 'optional'

        def update_odb(section):
            section['use_async_driver'] = True
            if section['engine'] == 'postgresql':
                section['engine'] = 'postgresql+pg8000'

        def update_hot_deploy(section):
            section['delete_after_pick_up'] = True

        def update_deploy_patterns_allowed(section):
            section['order'] = 'false_true'
            section['*'] = True

        def update_invoke_patterns_allowed(section):
            section['order'] = 'false_true'
            section['*'] = True

        def update_singleton(section):
            if section['initial_sleep_time'] == '500':
                section['initial_sleep_time'] = 2500

        def update_misc(section):
            section['return_internal_objects'] = False
            section['delivery_lock_timeout'] = 2
            section['queue_build_cap'] = 30
            section['http_proxy'] = ''
            section['locale'] = ''
            section['ensure_sql_connections_exist'] = True
            section['http_server_header'] = 'Zato'
            section['zeromq_connect_sleep'] = '0.1'
            section['aws_host'] = ''
            section['use_soap_envelope'] = True

        def update_kvdb(section):
            section['use_redis_sentinels'] = False
            section['redis_sentinels'] = ''
            section['redis_sentinels_master'] = ''
            section['shadow_password_in_logs'] = True
            section['log_connection_info_sleep_time'] = 5

        def update_component_enabled(section):
            section['stats'] = True
            section['slow_response'] = True

        def update_os_environ(section):
            section['sample_key'] = 'sample_value'

        update_handlers = {
            'main': update_main,
            'crypto': update_crypto,
            'odb': update_odb,
            'hot_deploy': update_hot_deploy,
            'singleton': update_singleton,
            'misc': update_misc,
            'kvdb': update_kvdb,
            'component_enabled': update_component_enabled,
            'os_environ': update_os_environ,
            'deploy_patterns_allowed': update_deploy_patterns_allowed,
            'invoke_patterns_allowed': update_invoke_patterns_allowed,
        }

        # Order of sections in 2.0
        all_sections_2_0 = ('main', 'crypto', 'odb', 'hot_deploy', 'deploy_patterns_allowed', 'invoke_patterns_allowed', 
            'singleton', 'spring', 'misc', 'stats', 'kvdb', 'startup_services_first_worker', 'startup_services_any_worker',
            'pubsub', 'patterns', 'profiler', 'user_config', 'newrelic', 'sentry', 'rbac', 'component_enabled', 'os_environ')

        buff = StringIO(server_conf_template)

        ref_cp = ConfigParser()
        ref_cp.readfp(buff)
        buff.close()

        server_conf_path = os.path.join(self.component_dir, 'config', 'repo', 'server.conf')

        old_config = ConfigParser()
        old_config.read(server_conf_path)

        new_config = {}

        # Update sections already existing in 1.1
        for section in old_config.sections():
            section_dict = dict(old_config.items(section))
            if section in update_handlers:
                update_handlers[section](section_dict)
            new_config[section] = section_dict

        # Sections new to 2.0
        for name in ('stats', 'startup_services_first_worker', 'startup_services_any_worker', 'pubsub', 'patterns', 
                    'profiler', 'user_config', 'newrelic', 'sentry', 'rbac', 'component_enabled', 'os_environ',
                    'deploy_patterns_allowed', 'invoke_patterns_allowed'):
            new_config[name] = dict(ref_cp.items(name))

        new_cp = ConfigParser()
        for section in all_sections_2_0:
            new_cp.add_section(section)
            for key, value in new_config[section].items():
                new_cp.set(section, key, value)

        server_conf = open(server_conf_path, 'w')
        new_cp.write(server_conf)
        server_conf.close()

    def _migrate_from_1_1_to_2_0_lua(self):
        lua_internal_path = os.path.join(self.component_dir, 'config', 'repo', 'lua', 'internal')
        lua_user_path = os.path.join(self.component_dir, 'config', 'repo', 'lua', 'user')

        os.makedirs(lua_internal_path)
        os.makedirs(lua_user_path)

        rename_if_exists_path = os.path.join(lua_internal_path, 'zato.rename_if_exists.lua')
        f = open(rename_if_exists_path, 'w')
        f.write(lua_zato_rename_if_exists)
        f.close()

    def _migrate_from_1_1_to_2_0_static(self):
        os.mkdir(os.path.join(self.component_dir, 'config', 'repo', 'static'))

    def _migrate_from_1_1_to_2_0_tls(self):
        tls_dir_path = os.path.join(self.component_dir, 'config', 'repo', 'tls')

        os.mkdir(tls_dir_path)
        os.mkdir(os.path.join(tls_dir_path, 'ca-certs'))
        os.mkdir(os.path.join(tls_dir_path, 'keys-certs'))

    def _migrate_from_1_1_to_2_0_user_conf(self):
        f = open(os.path.join(self.component_dir, 'config', 'repo', 'user.conf'), 'w')
        f.write(user_conf_contents)
        f.close()

    def migrate_from_1_1_to_2_0_server(self):
        self._migrate_from_1_1_to_2_0_logging()
        self._migrate_from_1_1_to_2_0_server_conf()
        self._migrate_from_1_1_to_2_0_lua()
        self._migrate_from_1_1_to_2_0_static()
        self._migrate_from_1_1_to_2_0_tls()
        self._migrate_from_1_1_to_2_0_user_conf()

    def migrate_from_1_1_to_2_0_web_admin(self):
        self._migrate_from_1_1_to_2_0_logging()

    def migrate_from_1_1_to_2_0_load_balancer(self):
        self._migrate_from_1_1_to_2_0_logging()

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
