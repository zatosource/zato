# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import main, TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common import APISPEC
from zato.server.apispec import ServiceInfo

# ################################################################################################################################

if 0:
    from zato.server.apispec import _DocstringSegment
    from zato.server.apispec import SimpleIODescription

    _DocstringSegment = _DocstringSegment
    SimpleIODescription = SimpleIODescription

# ################################################################################################################################

service_name = 'my.service'

sio_config = Bunch()

sio_config.int = Bunch()
sio_config.bool = Bunch()
sio_config.secret = Bunch()
sio_config.bytes_to_str = Bunch()

sio_config.int.prefix = set()
sio_config.int.exact = set()
sio_config.int.suffix = set()

sio_config.bool.prefix = set()
sio_config.bool.exact = set()
sio_config.bool.suffix = set()

# ################################################################################################################################
# ################################################################################################################################

class APISpecSIODescription(TestCase):

    def test_get_sio_desc_multiline_no_separator(self):

        class MyService:
            class SimpleIO:
                """
                * user_id - a111 a222

                a333

                a444
                a555
                a666
                a777 a888 a99

                * user_name - b111

                * address_id - c111 c222 c333 c444

                * address_name - d111

                  d222
                """
                input_required = 'user_id'
                input_optional = 'user_name'
                output_required = 'address_id'
                output_optional = 'address_name'

        info = ServiceInfo(service_name, MyService, sio_config, 'public')
        description = info.simple_io['zato'].description # type: SimpleIODescription

        # There are multiple lines and no I/O separator
        # so input and output descriptions will be the same.

        input_user_id      = description.input['user_id']
        input_user_name    = description.input['user_name']
        input_address_id   = description.input['address_id']
        input_address_name = description.input['address_name']

        output_user_id      = description.output['user_id']
        output_user_name    = description.output['user_name']
        output_address_id   = description.output['address_id']
        output_address_name = description.output['address_name']

        self.assertListEqual(input_user_id, output_user_id)
        self.assertListEqual(input_user_name, output_user_name)
        self.assertListEqual(input_address_id, output_address_id)
        self.assertListEqual(input_address_name, output_address_name)

        print(111, description.input)

        '''
        'user_id':      ['a111 a222\n', 'a333\n', 'a444', 'a555', 'a666', 'a777 a888 a99\n']
        'user_name':    ['b111\n']
        'address_id':   ['c111 c222 c333 c444\n']
        'address_name': ['d111\n', 'd222']}
        '''

# ################################################################################################################################
# ################################################################################################################################

class APISpecDocstringParsing(TestCase):

# ################################################################################################################################

    def xtest_docstring_summary_only(self):

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

    def xtest_docstring_multiline(self):

        class MyService:
            """ This is a one-line summary.

            This is public information
            It is multiline
            """

        info = ServiceInfo(service_name, MyService, sio_config, 'public')

        self.assertEqual(info.docstring.summary, 'This is a one-line summary.')
        self.assertEqual(info.docstring.full, 'This is a one-line summary.\n\nThis is public information\nIt is multiline')

# ################################################################################################################################

    def xtest_extract_tags_public_only_implicit(self):

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

    def xtest_extract_tags_public_only_explicit(self):

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

    def xtest_extract_tags_multi_1(self):

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
