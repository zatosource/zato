# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
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

# We notify users of major releases once a quarter = 90 days
delta_major_days = 90
delta_major = day * delta_major_days

# We notify users of major releases once a month = 30 days
delta_minor_days = 30
delta_minor = day * delta_minor_days

# Download URLs
url_latest = 'https://zato.io/docs/admin/guide/install/index.html'
url_version = 'https://zato.io/docs/{}/admin/guide/install/index.html'

# What to store in logs
msg = 'Cluster `%s` uses Zato `%s` and a new %s release `%s` is available' \
      ' from %s - consider an upgrade.' \
      ' This message will be repeated in %s days.'

data = """
{

 "current_major":"4.0",
 "current_minor":"4.0.7",
 "current_minor_release_date": "2015-01-28",

 "latest_2_0":"2.0.7",
 "latest_3_0":"3.0.5",
 "latest_3_1":"3.1.9",

}
"""

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

        # One day in seconds
        d1 = 1#60 * 60 * 24

        try:
            _version = version.replace('Zato ', '')
            major = _version[:3]
            minor = _version[:5]

            # Each major version has its own endpoint
            address = 'https://zato.io/support/updates/info-{}.json'.format(major)

            x = 0

            while x < 2:
                x += 1

                # Check if there are updates and notify if needed
                self._check_notify(address, major, minor, _version)

                # We can sleep for 1 day and then check again
                sleep(d1)

        except Exception, e:
            self.logger.warn(format_exc(e))

# ################################################################################################################################

    def _get_last_notified(self, key):
        value = self.kvdb.conn.get(key)
        return arrow_get(value) if value else None

# ################################################################################################################################

    def _set_last_modified(self, key):
        self.kvdb.conn.set(key, utcnow().format('YYYY-MM-DD'))

# ################################################################################################################################

    def _time_elapsed_major(self, _delta_major):
        """ Returns True if enough time elapsed since the last time we let users
        know that a new major version is available.
        """
        last_notified = self._get_last_notified(cache_key_major)

        # We let users know at least once
        if last_notified:
            return True
            if (utcnow() - last_notified).total_seconds() >= _delta_major:
                return True

        # We never let users know so we can do it now
        else:
            self._set_last_modified(cache_key_major)
            return True

# ################################################################################################################################

    def _time_elapsed_minor(self, _delta_minor):
        pass

# ################################################################################################################################

    def _get_current(self):
        #response = requests_get(address, params={'v':_version})
        #self.logger.warn(response.text)

        return bunchify(loads(data))

# ################################################################################################################################

    def _remote_has_new_minor(self, self_major_json, self_minor, remote_data):
        return False

# ################################################################################################################################

    def _notify(self, self_version, current, type, url, delta):
        self.logger.warn(msg, self.server.cluster.name, self_version, type, current, url, delta)

# ################################################################################################################################

    def _notify_major_release(self, self_version, current_major):
        self._notify(self_version, current_major, 'major', url_latest, delta_major_days)

# ################################################################################################################################

    def _notify_minor_release(self, self_version, current_major, current_minor):
        self._notify(self_version, current_major, 'minor', url_version.format(self_version), delta_minor_days)

# ################################################################################################################################

    def _check_notify(self, address, self_major, self_minor, self_version, delta_major=delta_major, delta_minor=delta_minor):
        """ Checks if users should be notified of new releases and does it if required.

        Scenarios to handle (note that 2. and 4. do not rule out each other):

        * Someone is running Zato from source code in which case we only notify of full releases
        * Someone's major versions is not newest
        * Someone's major version is newest but their minor one is not
        * Someone's major is not newest and there is a newer minor version within their self_major,
          for instance someone is running 3.0.1 and the newest major version is 3.1.3 but there is also 3.0.5 for them
        """

        # Consult remote end
        data = self._get_current()

        # To save on keystrokes
        config = self.server.fs_server_config.updates
        self_major_json = self_major.replace('.', '_') # E.g. 3.0 -> 3_0

        # We are running from source code so only notify of latest versions, no matter which
        if source_prefix in self_major and config.notify_major_versions and self._time_elapsed_major(delta_major):
            self._notify_major_release(self_version, data.current_major)
            return

        # We are on the current major but possibly not on minor
        if self_major == data.current_major:
            if self_minor < data.current_minor:
                if config.notify_minor_versions and self._time_elapsed_minor(delta_minor):
                    self._notify_minor_release(self_version, current_major, data.current_minor)

        # We are definitely running on an older version and on top of there may be a new minor version of our major revision
        # For instance, we are 3.0.1 but there is 4.0.3 and on top of it, there is 3.0.5 within the 3.0.x branch.
        if self_major < data.current_major:

            if config.notify_major_versions and self._time_elapsed_major(delta_major):
                self._notify_major_release(self_version, data.current_minor)

            if self._remote_has_new_minor(self_major_json, self_minor, data):
                if config.notify_minor_versions and self._time_elapsed_minor(delta_minor):
                    self._notify_minor_release(self_version, current_major, data.current_minor)

# ################################################################################################################################
