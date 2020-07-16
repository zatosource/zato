# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from unittest import main

# Bunch
from bunch import bunchify

# Zato
from zato.common.test import BaseSIOTestCase
from zato.server.apispec import Generator
from common import MyService, sio_config

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

class GeneratorTestCase(BaseSIOTestCase):

    def test_generator_get_info(self):

        MyClass = deepcopy(MyService)
        CySimpleIO.attach_sio(self.get_server_config(), MyClass)

        service_store_services = {
            'my.impl.name': {
                'name': 'my.name',
                'service_class': MyClass,
            }
        }
        include = ['*']
        exclude = []
        query   = ''
        tags    = 'public'

        generator = Generator(service_store_services, sio_config, include, exclude, query, tags, needs_sio_desc=False)

        info = generator.get_info()
        info = bunchify(info)

        services = info.services   # type: Bunch
        self.assertEqual(len(services), 1)

        service = services[0] # type: Bunch
        service_keys = sorted(service)

        self.assertListEqual(service_keys, ['docs', 'invoked_by', 'invokes', 'name', 'namespace_name', 'simple_io'])

        service_docs           = service.docs       # type: Bunch
        service_invoked_by     = service.invoked_by
        service_invokes        = service.invokes
        service_namespace_name = service.namespace_name
        service_simple_io      = service.simple_io

        self.assertEqual(service_docs.description, 'It has a docstring.')
        self.assertEqual(service_docs.description_html, 'It has a docstring.')
        self.assertEqual(service_docs.full, 'This is my service.\n\nIt has a docstring.\n')
        self.assertEqual(service_docs.full_html, 'This is my service.</p>\n<p>It has a docstring.')
        self.assertEqual(service_docs.summary, 'This is my service.')
        self.assertEqual(service_docs.summary_html, 'This is my service.')

        self.assertListEqual(service_invoked_by, [])
        self.assertListEqual(service_invokes, ['abc.def', 'qwe.rty'])

        self.assertEqual(service_namespace_name, '')

        sio_openapi_v3 = service_simple_io.openapi_v3 # type: Bunch
        sio_soap_12    = service_simple_io.soap_12    # type: Bunch
        sio_zato       = service_simple_io.zato       # type: Bunch

        self.assertEqual(len(sio_openapi_v3.input_required), 2)

        # OpenAPI

        sio_openapi_v3_input_required_0 = sio_openapi_v3.input_required[0] # type: Bunch
        sio_openapi_v3_input_required_1 = sio_openapi_v3.input_required[1] # type: Bunch

        self.assertEqual(sio_openapi_v3_input_required_0.name, 'input_req_customer_id')
        self.assertEqual(sio_openapi_v3_input_required_0.description, '')
        self.assertEqual(sio_openapi_v3_input_required_0.type, 'integer')
        self.assertEqual(sio_openapi_v3_input_required_0.subtype, 'int32')

        self.assertEqual(sio_openapi_v3_input_required_1.name, 'input_req_user_id')
        self.assertEqual(sio_openapi_v3_input_required_1.description,
            'This is the first line.\nHere is another.\nAnd here are some more lines.')
        self.assertEqual(sio_openapi_v3_input_required_1.type, 'integer')
        self.assertEqual(sio_openapi_v3_input_required_1.subtype, 'int32')

        # SOAP 1.2

        sio_soap_12_input_required_0 = sio_soap_12.input_required[0] # type: Bunch
        sio_soap_12_input_required_1 = sio_soap_12.input_required[1] # type: Bunch

        self.assertEqual(sio_soap_12_input_required_0.name, 'input_req_customer_id')
        self.assertEqual(sio_soap_12_input_required_0.description, '')
        self.assertEqual(sio_soap_12_input_required_0.type, 'integer')
        self.assertEqual(sio_soap_12_input_required_0.subtype, 'xsd:integer')

        self.assertEqual(sio_soap_12_input_required_1.name, 'input_req_user_id')
        self.assertEqual(sio_soap_12_input_required_1.description,
            'This is the first line.\nHere is another.\nAnd here are some more lines.')
        self.assertEqual(sio_soap_12_input_required_1.type, 'integer')
        self.assertEqual(sio_soap_12_input_required_1.subtype, 'xsd:integer')

        # Zato

        sio_zato_input_required_0 = sio_zato.input_required[0] # type: Bunch
        sio_zato_input_required_1 = sio_zato.input_required[1] # type: Bunch

        self.assertEqual(sio_zato_input_required_0.name, 'input_req_customer_id')
        self.assertEqual(sio_zato_input_required_0.description, '')
        self.assertEqual(sio_zato_input_required_0.type, 'integer')
        self.assertEqual(sio_zato_input_required_0.subtype, 'integer')

        self.assertEqual(sio_zato_input_required_1.name, 'input_req_user_id')
        self.assertEqual(sio_zato_input_required_1.description,
            'This is the first line.\nHere is another.\nAnd here are some more lines.')
        self.assertEqual(sio_zato_input_required_1.type, 'integer')
        self.assertEqual(sio_zato_input_required_1.subtype, 'integer')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
