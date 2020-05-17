# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main, TestCase


# Zato
from zato.server.apispec import Generator
from common import MyService, service_name, sio_config

# ################################################################################################################################
# ################################################################################################################################

class GeneratorTestCase(TestCase):

    def test_generator_get_info(self):

        service_store_services = {
            'my.impl.name': {
                'name': 'my.name',
                'service_class': MyService,
            }
        }
        include = ['*']
        exclude = []
        query   = ''
        tags    = ''

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)
        info = generator.get_info()

        from pprint import pprint
        pprint(info)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
