# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from unittest import main

# Zato
from zato.server.apispec import ServiceInfo
from zato.common.test import BaseSIOTestCase
from common import MyService, service_name, sio_config

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################

if 0:
    from zato.server.apispec import _DocstringSegment
    from zato.server.apispec import SimpleIODescription

    _DocstringSegment = _DocstringSegment
    SimpleIODescription = SimpleIODescription

# ################################################################################################################################
# ################################################################################################################################

class APISpecSIODescription(BaseSIOTestCase):

    def test_get_sio_desc_multiline_no_separator(self):

        MyClass = deepcopy(MyService)
        CySimpleIO.attach_sio(self.get_server_config(), MyClass)

        info = ServiceInfo(service_name, MyClass, sio_config, 'public')
        description = info.simple_io['zato'].description # type: SimpleIODescription

        # There are multiple lines and no I/O separator
        # so input and output descriptions will be the same.

        input_user_id      = description.input['input_req_user_id']
        input_user_name    = description.input['input_opt_user_name']
        input_address_id   = description.input['output_req_address_id']
        input_address_name = description.input['output_opt_address_name']

        output_user_id      = description.output['input_req_user_id']
        output_user_name    = description.output['input_opt_user_name']
        output_address_id   = description.output['output_req_address_id']
        output_address_name = description.output['output_opt_address_name']

        self.assertEqual(input_user_id, output_user_id)
        self.assertEqual(input_user_name, output_user_name)
        self.assertEqual(input_address_id, output_address_id)
        self.assertEqual(input_address_name, output_address_name)

        self.assertEqual(input_user_id, 'This is the first line.\nHere is another.\nAnd here are some more lines.')
        self.assertEqual(input_user_name, 'b111')
        self.assertEqual(input_address_id, 'c111 c222 c333 c444')
        self.assertEqual(input_address_name, 'd111\nd222')

        self.assertEqual(output_user_id, 'This is the first line.\nHere is another.\nAnd here are some more lines.')
        self.assertEqual(output_user_name, 'b111')
        self.assertEqual(output_address_id, 'c111 c222 c333 c444')
        self.assertEqual(output_address_name, 'd111\nd222')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
