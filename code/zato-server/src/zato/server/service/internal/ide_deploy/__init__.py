# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.json_internal import dumps
from zato.server.service import Service

class Create(Service):
    """ Like zato.hot-deploy.create but returns an empty string if input payload is empty to let IDEs test server connections.
    """
    input = '-payload_name', '-payload'
    output = 'success', 'msg'

    def handle(self):
        if not self.request.payload:
            self.response.payload.success = True
            self.response.payload.msg = 'Ping succeeded.'
            return

        payload_name = self.request.payload.get('payload_name')
        payload = self.request.payload.get('payload')
        if not (payload and payload_name):
            self.response.payload.success = False
            self.response.payload.msg = 'Both "payload" and "payload_name" fields are required.'
            return

        new_payload = dict(self.request.payload, cluster_id=self.server.cluster_id)
        try:
            self.invoke('zato.service.upload-package', dumps(new_payload), data_format=DATA_FORMAT.JSON)
        except Exception as e:
            self.logger.warning('Could not invoke zato.service.upload-package, e:`%s`', format_exc(e))
            self.response.payload.success = False
            self.response.payload.msg = 'Deployment failed: {}'.format(e)
            return

        self.response.payload.success = True
        self.response.payload.msg = 'Deployment started: please check server log for status.'
