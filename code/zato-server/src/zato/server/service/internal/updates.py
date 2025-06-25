# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from errno import ENETUNREACH
from http.client import OK

# Bunch
from bunch import bunchify

# gevent
from gevent import spawn

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

# Download and info URLs
url_info = 'https://zato.io/support/updates/info-{}.json'

# ################################################################################################################################

class CheckUpdates(Service):
    """ Checks if there are any minor or major Zato updates.
    """

    def handle(self):

        # Run in a new greenlet in case we are invoked externally, e.g. over HTTP
        _ = spawn(self._check)

# ################################################################################################################################

    def _check(self):

        _version = version.replace('Zato ', '')
        major = _version[:3]

        # Check if there are updates and notify if needed
        try:
            self._check_notify(url_info, major, _version)
        except Exception:
            pass # Ignore any and all errors, e.g. due to the lack of Internet connectivity

# ################################################################################################################################

    def _check_notify(self, _url_info, self_major, self_version):
        _ = self._get_current(_url_info, self_major, self_version)

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
