# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Zato
from zato.server.apispec import Generator
from common import MyService, service_name, sio_config

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

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
        tags    = 'public'

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)

        info = generator.get_info()
        info = bunchify(info)

        services   = info.services   # type: Bunch
        self.assertEqual(len(services), 1)

        namespaces = info.namespaces # type: Bunch

        service = services[0] # type: Bunch
        service_keys = sorted(service)

        self.assertListEqual(service_keys, ['docs', 'invoked_by', 'invokes', 'name', 'namespace_name', 'simple_io'])

        service_docs           = service.docs       # type: Bunch
        service_invoked_by     = service.invoked_by
        service_invokes        = service.invokes
        service_name           = service.name
        service_namespace_name = service.namespace_name
        service_simple_io      = service.simple_io

        self.assertEqual(service_docs.description, 'It has a docstring.')
        self.assertEqual(service_docs.description_html, 'It has a docstring.')
        self.assertEqual(service_docs.full, 'This is my service.\n\nIt has a docstring.')
        self.assertEqual(service_docs.full_html, 'This is my service.</p>\n<p>It has a docstring.')
        self.assertEqual(service_docs.summary, 'This is my service.')
        self.assertEqual(service_docs.summary_html, 'This is my service.')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
