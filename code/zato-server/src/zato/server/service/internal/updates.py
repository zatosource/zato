# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from errno import ENETUNREACH
from http.client import OK
from json import loads
from traceback import format_exc

# Arrow
from arrow import get as arrow_get, utcnow

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, spawn

# Requests
from requests import get as requests_get
from requests.exceptions import ConnectionError

# Zato
from zato.common import version
from zato.server.service import Service

# ################################################################################################################################

# If a version has this prefix it means someone is running from source code
source_prefix = 'pre'
cache_key_major = 'zato.updates.major.last-notified'
cache_key_minor = 'zato.updates.minor.last-notified'

# In seconds
day = 24 * 60 * 60

# We notify users of major releases half a year = 180 days
delta_major_days = 180
delta_major = day * delta_major_days

# We notify users of minor releases bimonthly = 60 days
delta_minor_days = 60
delta_minor = day * delta_minor_days

# Download and info URLs
url_latest = 'https://zato.io/docs/admin/guide/install/index.html'
url_version = 'https://zato.io/docs/{}/admin/guide/install/index.html'
url_info = 'https://zato.io/support/updates/info-{}.json'

# What to store in logs
msg = '\n\nCluster `%s` uses Zato `%s` and a new %s release is available' \
      ' from %s - consider an upgrade to %s.' \
      ' This message will be repeated in %s days.'

# ################################################################################################################################

class CheckUpdates(Service):
    """ Checks if there are any minor or major Zato updates and notifies in server.log
    if there are any, if told to and it is time to do so.
    """

# ################################################################################################################################

    def handle(self):

        # Run in a new greenlet in case we are invoked externally, e.g. over HTTP
        spawn(self._serve_forerver)

# ################################################################################################################################

    def _serve_forerver(self):

        try:
            _version = version.replace('Zato ', '')
            major = _version[:3]
            minor = _version[:5]

            # Each major version has its own endpoint

            while True:

                # Check if there are updates and notify if needed
                self._check_notify(url_info, major, minor, _version)

                # We can sleep for 1 day and then check again
                sleep(day)

        except Exception:
            self.logger.warn(format_exc())

# ################################################################################################################################

    def _get_last_notified(self, key):
        with self.lock():
            value = self.kvdb.conn.get(key)
            return arrow_get(value) if value else None

# ################################################################################################################################

    def _set_last_modified(self, key):
        self.kvdb.conn.set(key, utcnow().format('YYYY-MM-DD'))

# ################################################################################################################################

    def _time_elapsed(self, cache_key, delta):
        """ Returns True if enough time elapsed since the last time we let users
        know that a new major version is available.
        """
        last_notified = self._get_last_notified(cache_key)

        # We let users know at least once
        if last_notified:
            if (utcnow() - last_notified).total_seconds() >= delta:
                return True

        # We never let users know so we can do it now
        else:
            self._set_last_modified(cache_key)
            return True

# ################################################################################################################################

    def _time_elapsed_major(self, _delta_major):
        return self._time_elapsed(cache_key_major, _delta_major)

# ################################################################################################################################

    def _time_elapsed_minor(self, _delta_minor):
        return self._time_elapsed(cache_key_minor, _delta_minor)

# ################################################################################################################################

    def _get_current(self, _url_info, self_major, self_version):
        try:
            response = requests_get(_url_info.format(self_major), params={'v':self_version})
        except ConnectionError as e:
            # We ignore ENETUNREACH because it simply means that we could not connect to the server,
            # which is fine, e.g. no Internet connectivity is allowed in that system.
            if e.errno != ENETUNREACH:
                raise
        else:
            if response.status_code == OK:
                return bunchify(loads(response.text))

# ################################################################################################################################

    def _remote_has_new_minor(self, self_major_json, self_minor, remote_data):
        return remote_data.get('latest_{}'.format(self_major_json)) > self_minor

# ################################################################################################################################

    def _notify(self, self_version, current, type, url, delta):
        self.logger.warn(msg, self.server.cluster.name, self_version, type, url, current, delta)

# ################################################################################################################################

    def _notify_major_release(self, self_version, current_major):
        self._notify(self_version, current_major, 'major', url_latest, delta_major_days)

# ################################################################################################################################

    def _notify_minor_release(self, self_version, current_major, current_minor):
        self._notify(self_version, current_major, 'minor', url_version.format(current_major), delta_minor_days)

# ################################################################################################################################

    def _check_notify(self, _url_info, self_major, self_minor, self_version, delta_major=delta_major, delta_minor=delta_minor):
        """ Checks if users should be notified of new releases and does it if required.

        Scenarios to handle (note that 2. and 4. do not rule out each other):

        * Someone is running Zato from source code in which case we only notify of full releases
        * Someone's major versions is not newest
        * Someone's major version is newest but their minor one is not
        * Someone's major is not newest and there is a newer minor version within their self_major,
          for instance someone is running 3.0.1 and the newest major version is 3.1.3 but there is also 3.0.5 for them
        """

        # Consult remote end
        data = self._get_current(_url_info, self_major, self_version)

        # Apparently we have nothing to work with
        if not data:
            return

        # To save on keystrokes
        config = self.server.fs_server_config.updates
        self_major_json = self_major.replace('.', '_') # E.g. 3.0 -> 3_0

        # We are running from source code so only notify of latest versions, no matter which
        if source_prefix in self_minor:
            if config.notify_if_from_source and self._time_elapsed_major(delta_major):
                self._notify_major_release(self_version, data.current_major)
            return

        # We are on the current major but possibly not on minor
        if self_major == data.current_major:
            if self_minor < data.current_minor:
                if config.notify_minor_versions and self._time_elapsed_minor(delta_minor):
                    self._notify_minor_release(self_version, data.current_major, data.current_minor)

        # We are definitely running on an older version and on top of there may be a new minor version of our major revision
        # For instance, we are 3.0.1 but there is 4.0.3 and on top of it, there is 3.0.5 within the 3.0.x branch.
        if self_major < data.current_major:

            if config.notify_major_versions and self._time_elapsed_major(delta_major):
                self._notify_major_release(self_version, data.current_minor)

            if self._remote_has_new_minor(self_major_json, self_minor, data):
                if config.notify_minor_versions and self._time_elapsed_minor(delta_minor):
                    self._notify_minor_release(self_version, data.current_major, data.current_minor)

# ################################################################################################################################
