# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main, TestCase


# Zato
from zato.server.apispec import ServiceInfo
from common import MyService, service_name, sio_config

# ################################################################################################################################
# ################################################################################################################################

class OpenAPI(TestCase):

    def test_generate_open_api(self):

        info = ServiceInfo(service_name, MyService, sio_config, 'public')
        description = info.simple_io['zato'].description # type: SimpleIODescription

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
