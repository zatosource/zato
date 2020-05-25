# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main, TestCase

# Zato
from zato.common import APISPEC
from zato.server.apispec import ServiceInfo
from common import MyService, service_name, sio_config

# ################################################################################################################################

if 0:
    from zato.server.apispec import _DocstringSegment
    from zato.server.apispec import SimpleIODescription

    _DocstringSegment = _DocstringSegment
    SimpleIODescription = SimpleIODescription

# ################################################################################################################################
# ################################################################################################################################

class APISpecSIODescription(TestCase):

    def test_get_sio_desc_multiline_no_separator(self):

        info = ServiceInfo(service_name, MyService, sio_config, 'public')
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

class APISpecDocstringParsing(TestCase):

# ################################################################################################################################

    def test_docstring_summary_only(self):

        class MyService:
            """ This is a one-line summary.
            """

        info = ServiceInfo(service_name, MyService, sio_config, 'public')

        # This service's docstring has a summary only so it will constitute
        # all of its summary, decsription and full docstring.

        self.assertEqual(info.docstring.summary, 'This is a one-line summary.')
        self.assertEqual(info.docstring.description, 'This is a one-line summary.')
        self.assertEqual(info.docstring.full, 'This is a one-line summary.')

# ################################################################################################################################

    def test_docstring_multiline(self):

        class MyService:
            """ This is a one-line summary.

            This is public information
            It is multiline
            """

        info = ServiceInfo(service_name, MyService, sio_config, 'public')

        self.assertEqual(info.docstring.summary, 'This is a one-line summary.')
        self.assertEqual(info.docstring.full, 'This is a one-line summary.\n\nThis is public information\nIt is multiline')

# ################################################################################################################################

    def test_extract_tags_public_only_implicit(self):

        class MyService:
            """ This is a one-line summary.

            This is public information
            It is multiline
            """

        segments = ServiceInfo(service_name, MyService, sio_config, APISPEC.DEFAULT_TAG).extract_segments(MyService.__doc__)

        # There should be only one tag, the default, implicit one called 'public'
        expected = {
             'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline',
             'summary':     'This is a one-line summary.'
        }

        self.assertEqual(len(segments), 1)
        public = segments[0] # type: _DocstringSegment
        self.assertDictEqual(public.to_dict(), expected)

# ################################################################################################################################

    def test_extract_tags_public_only_explicit(self):

        class MyService:
            """ #public
            This is a one-line summary.

            This is public information
            It is multiline
            """

        segments = ServiceInfo(service_name, MyService, sio_config, APISPEC.DEFAULT_TAG).extract_segments(MyService.__doc__)

        # There should be only one tag, the explicitly named 'public' one.
        expected = {
             'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline',
             'summary':     'This is a one-line summary.'
        }

        self.assertEqual(len(segments), 1)
        public = segments[0] # type: _DocstringSegment
        self.assertDictEqual(public.to_dict(), expected)

# ################################################################################################################################

    def test_extract_tags_multi_1(self):

        class MyService:
            """ This is a one-line summary.

            This is public information
            It is multiline

            #internal

            One-line summary for internal uses.

            This part is internal,
            it will not be visible
            to public users.
            """

        tags = [APISPEC.DEFAULT_TAG, 'internal']
        segments = ServiceInfo(service_name, MyService, sio_config, tags).extract_segments(MyService.__doc__)

        # There should be only one tag, the default, implicit one called 'public'
        expected_public = {
             'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline',
             'summary':     'This is a one-line summary.'
        }

        expected_internal = {
             'tag':         'internal',
             'description': 'This part is internal,\nit will not be visible\nto public users.',
             'full':        'One-line summary for internal uses.\n\nThis part is internal,\nit will not be visible\nto public users.',
             'summary':     'One-line summary for internal uses.'
        }

        self.assertEqual(len(segments), 2)

        public = segments[0] # type: _DocstringSegment
        self.assertDictEqual(public.to_dict(), expected_public)

        internal = segments[1] # type: _DocstringSegment
        self.assertDictEqual(internal.to_dict(), expected_internal)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
