# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common.test import enrich_with_static_config, rand_string
from zato.server.service.internal.updates import CheckUpdates, delta_major_days, delta_minor_days, msg, url_latest, url_version

enrich_with_static_config(CheckUpdates)

# ################################################################################################################################

class _FakeLogger(object):

    def __init__(self):
        self.args = []

    def warn(self, *args):
        self.args.append(args)

# ################################################################################################################################

class CheckUpdatesTestCase(TestCase):

# ################################################################################################################################

    def _get_service(self, current_major, current_minor, self_version,self_major, self_minor, elapsed,
        use_remote_has=False, remote_has_new_minor=None):

        def _get_current(_self, *ignored):
            return Bunch({
                'current_major': current_major,
                'current_minor': current_minor,
                'latest_2_0':'2.0.8',
                'latest_3_0':'3.0.5',
                'latest_4_0':'4.0.1',
                'latest_5_0':'5.0.2',
                'latest_5_1':'5.1.3',
                })

        def _time_elapsed(_self, *ignored):
            return elapsed

        cu = CheckUpdates()

        if use_remote_has:
            def _remote_has_new_minor(_self, *ignored):
                return remote_has_new_minor

            cu._remote_has_new_minor = _remote_has_new_minor

        cu.logger = _FakeLogger()
        cu._get_current = _get_current
        cu._time_elapsed = _time_elapsed

        return cu

# ################################################################################################################################

    def test_from_source_code_notify_true_elapsed_true(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1pre1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.1'
        current_minor = '5.1.3'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # We should have notified of a new major version only, hence len == 1
        self.assertEquals(len(cu.logger.args), 1)

        log_msg, log_cluster_name, log_self_version, log_type, log_url, log_current, log_delta = cu.logger.args[0]

        self.assertEquals(log_msg, msg)
        self.assertEquals(log_cluster_name, cluster_name)
        self.assertEquals(log_self_version, self_version)
        self.assertEquals(log_type, 'major')
        self.assertEquals(log_current, current_major)
        self.assertEquals(log_url, url_latest)
        self.assertEquals(log_delta, delta_major_days)

# ################################################################################################################################

    def test_from_source_code_notify_true_elapsed_false(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1pre1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.1'
        current_minor = '5.1.3'

        elapsed = False

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # No notifications since elapsed is False
        self.assertEquals(len(cu.logger.args), 0)

# ################################################################################################################################

    def test_from_source_code_notify_false_elapsed_true(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1pre1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.1'
        current_minor = '5.1.3'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = False

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # No notifications since notify_if_from_source is False
        self.assertEquals(len(cu.logger.args), 0)

# ################################################################################################################################

    def test_major_equal_minor_not_lesser(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.0'
        current_minor = '5.0.1'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # No notifications since we already have the latest minor version
        self.assertEquals(len(cu.logger.args), 0)

# ################################################################################################################################

    def test_major_equal_minor_lesser_notify_true_elapsed_true(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.0'
        current_minor = '5.0.2'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # We should have notified of a new minor version only, hence len == 1
        self.assertEquals(len(cu.logger.args), 1)

        log_msg, log_cluster_name, log_self_version, log_type, log_url, log_current, log_delta = cu.logger.args[0]

        self.assertEquals(log_msg, msg)
        self.assertEquals(log_cluster_name, cluster_name)
        self.assertEquals(log_self_version, self_version)
        self.assertEquals(log_type, 'minor')
        self.assertEquals(log_current, current_major)
        self.assertEquals(log_url, url_version.format(current_major))
        self.assertEquals(log_delta, delta_minor_days)

# ################################################################################################################################

    def test_major_equal_minor_lesser_notify_true_elapsed_false(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.0'
        current_minor = '5.0.2'

        elapsed = False

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # Elapsed is false so there should be no notifications
        self.assertEquals(len(cu.logger.args), 0)

# ################################################################################################################################

    def test_major_equal_minor_lesser_notify_false_elapsed_true(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '5.0'
        current_minor = '5.0.2'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = False
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # Notifications are off so none should be logged
        self.assertEquals(len(cu.logger.args), 0)

# ################################################################################################################################

    def test_major_lesser_notify_true_elapsed_true_remote_has_new_true(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '6.5'
        current_minor = '6.5.9'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # We should have notified of both major and minor versions
        self.assertEquals(len(cu.logger.args), 2)

        major_log_msg, major_log_cluster_name, major_log_self_version, major_log_type, major_log_url, major_log_current, \
            major_log_delta = cu.logger.args[0]

        self.assertEquals(major_log_msg, msg)
        self.assertEquals(major_log_cluster_name, cluster_name)
        self.assertEquals(major_log_self_version, self_version)
        self.assertEquals(major_log_type, 'major')
        self.assertEquals(major_log_current, current_minor)
        self.assertEquals(major_log_url, url_latest)
        self.assertEquals(major_log_delta, delta_major_days)

        minor_log_msg, minor_log_cluster_name, minor_log_self_version, minor_log_type, minor_log_url, minor_log_current, \
            minor_log_delta = cu.logger.args[1]

        self.assertEquals(minor_log_msg, msg)
        self.assertEquals(minor_log_cluster_name, cluster_name)
        self.assertEquals(minor_log_self_version, self_version)
        self.assertEquals(minor_log_type, 'minor')
        self.assertEquals(minor_log_current, current_major)
        self.assertEquals(minor_log_url, url_version.format(current_major))
        self.assertEquals(minor_log_delta, delta_minor_days)

# ################################################################################################################################

    def test_major_lesser_notify_true_elapsed_true_remote_has_new_false(self):

        cluster_name = rand_string()

        self_major = '5.0'
        self_minor = '5.0.1'
        self_version = self_minor + '.rev-abcdef3'

        current_major = '6.5'
        current_minor = '6.5.9'

        elapsed = True

        cu = self._get_service(current_major, current_minor, self_version, self_major, self_minor, elapsed, True, False)

        cu.server = Bunch()
        cu.server.cluster = Bunch(name=cluster_name)

        cu.server.fs_server_config = Bunch(updates=Bunch())
        cu.server.fs_server_config.updates.notify_major_versions = True
        cu.server.fs_server_config.updates.notify_minor_versions = True
        cu.server.fs_server_config.updates.notify_if_from_source = True

        cu._check_notify(None, self_major, self_minor, self_version, None, None)

        # We have a new major version but remote has nothing about a newer minor version
        self.assertEquals(len(cu.logger.args), 1)

        major_log_msg, major_log_cluster_name, major_log_self_version, major_log_type, major_log_url, major_log_current, \
            major_log_delta = cu.logger.args[0]

        self.assertEquals(major_log_msg, msg)
        self.assertEquals(major_log_cluster_name, cluster_name)
        self.assertEquals(major_log_self_version, self_version)
        self.assertEquals(major_log_type, 'major')
        self.assertEquals(major_log_current, current_minor)
        self.assertEquals(major_log_url, url_latest)
        self.assertEquals(major_log_delta, delta_major_days)

# ################################################################################################################################
