# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from errno import ENETUNREACH
from http.client import OK
from traceback import format_exc

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, spawn

# Requests
from requests import get as requests_get
from requests.exceptions import ConnectionError

# Zato
from zato.common.version import get_version
from zato.common.json_internal import loads
from zato.server.service import Service

# ################################################################################################################################

# Current Zato version
version = get_version()

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
url_info = 'https://zato.io/support/updates/info-{}.json'

# ################################################################################################################################

class CheckUpdates(Service):
    """ Checks if there are any minor or major Zato updates and notifies in server.log
    if there are any, if told to and it is time to do so.
    """

# ################################################################################################################################

    def handle(self):

        # Run in a new greenlet in case we are invoked externally, e.g. over HTTP
        _ = spawn(self._serve_forerver)

# ################################################################################################################################

    def _serve_forerver(self):

        try:
            _version = version.replace('Zato ', '')
            major = _version[:3]
            minor = _version[:5]

            # Each major version has its own endpoint

            while True:

                # Check if there are updates and notify if needed
                try:
                    self._check_notify(url_info, major, minor, _version)
                except Exception:
                    pass # Ignore any and all errors, e.g. due to the lack of Internet connectivity

                # We can sleep for 1 day and then check again
                sleep(day)

        except Exception:
            self.logger.warning(format_exc())

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

    def _check_notify(self, _url_info, self_major, self_minor, self_version, delta_major=delta_major, delta_minor=delta_minor):
        _ = self._get_current(_url_info, self_major, self_version)

# ################################################################################################################################
