# -*- coding: utf-8 -*-

"""
Copyright (C) 2018 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import DATA_FORMAT
from zato.server.service.internal import AdminService, AdminSIO


class Create(AdminService):
    """ Behave like zato.hot-deploy.create, except support returning an empty
    successful response in the case of a blank request payload, to allow
    the IDE to test the server connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_ide_deploy_create_request'
        response_elem = 'zato_ide_deploy_create_response'
        input_required = ()

    def handle(self):
        if not self.request.raw_request:
            return
        else:
            self.response.payload = self.invoke('zato.service.upload-package', self.request.payload, data_format=DATA_FORMAT.JSON)
