# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test.apispec_ import service_name, sio_config
from zato.common.api import APISPEC
from zato.server.apispec.parser.docstring import not_public
from zato.server.apispec.parser.service import ServiceInfo

# ################################################################################################################################

if 0:
    from zato.server.apispec.parser.docstring import _DocstringSegment, SimpleIODescription

    _DocstringSegment = _DocstringSegment
    SimpleIODescription = SimpleIODescription

# ################################################################################################################################
# ################################################################################################################################

class APISpecDocstringParsing(TestCase):

    maxDiff = 100000

# ################################################################################################################################

    def test_docstring_summary_only(self):

        class CyMyService:
            """ This is a one-line summary.
            """

        info = ServiceInfo(
            service_name,
            CyMyService, # type: ignore
            sio_config,
            'public'
        )

        # This service's docstring has a summary only so it will constitute
        # all of its summary, decsription and full docstring.

        self.assertEqual(info.docstring.data.summary, 'This is a one-line summary.')
        self.assertEqual(info.docstring.data.description, 'This is a one-line summary.')
        self.assertEqual(info.docstring.data.full, 'This is a one-line summary.')

# ################################################################################################################################

    def test_docstring_multiline(self):

        class CyMyService:
            """ This is a one-line summary.

            This is public information
            It is multiline

            ======= ======= =======
            header1 header2 header3
            ======= ======= =======
            column1 column2 column3
            ======= ======= =======

            - This is a list

              - It has a sub-list

                - And another one

                The sub-list has a table

                ======= ======= =======
                header4 header5 header6
                ======= ======= =======
                column4 column5 column6
                ======= ======= =======

            - More bullets in the list

            """
            __doc__: 'str'

        info = ServiceInfo(
            service_name,
            CyMyService, # type: ignore
            sio_config,
            'public'
        )
        self.assertEqual(info.docstring.data.summary, 'This is a one-line summary.')

        service_docstring_lines = CyMyService.__doc__.strip().splitlines()
        docstring_full_lines = info.docstring.data.full.splitlines()

        for idx, line in enumerate(service_docstring_lines):

            expected_line = line.strip() # type: str
            given_line = docstring_full_lines[idx].strip() # type: str

            self.assertEqual(expected_line, given_line)

# ################################################################################################################################

    def test_extract_tags_public_only_implicit(self):

        class CyMyService:
            """ This is a one-line summary.

            This is public information
            It is multiline
            """

        segments = ServiceInfo(
            service_name,
            CyMyService, # type: ignore
            sio_config,
            APISPEC.DEFAULT_TAG).docstring.extract_segments(
                CyMyService.__doc__ # type: ignore
            )

        # There should be only one tag, the default, implicit one called 'public'
        expected = {
             'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline\n',
             'summary':     'This is a one-line summary.'
        }

        self.assertEqual(len(segments), 1)
        public = segments[0] # type: _DocstringSegment

        segment_dict = public.to_dict()

        self.assertEqual(segment_dict['tag'], expected['tag'])
        self.assertEqual(segment_dict['description'], expected['description'])
        self.assertEqual(segment_dict['full'], expected['full'])
        self.assertEqual(segment_dict['summary'], expected['summary'])

# ################################################################################################################################

    def test_extract_tags_public_only_explicit(self):

        class CyMyService:
            """ @public
            This is a one-line summary.

            This is public information
            It is multiline
            """

        segments = ServiceInfo(
            service_name,
            CyMyService, # type: ignore
            sio_config,
            APISPEC.DEFAULT_TAG).docstring.extract_segments(
                CyMyService.__doc__ # type: ignore
            )

        # There should be only one tag, the explicitly named 'public' one.
        expected = {
             'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline\n',
             'summary':     'This is a one-line summary.'
        }

        self.assertEqual(len(segments), 1)
        public = segments[0] # type: _DocstringSegment

        segment_dict = public.to_dict()

        self.assertEqual(segment_dict['tag'], expected['tag'])
        self.assertEqual(segment_dict['description'], expected['description'])
        self.assertEqual(segment_dict['full'], expected['full'])
        self.assertEqual(segment_dict['summary'], expected['summary'])

# ################################################################################################################################

    def test_extract_tags_multi_1(self):

        class CyMyService:
            """ This is a one-line summary.

            This is public information
            It is multiline

            @internal

            One-line summary for internal uses.

            This part is internal,
            it will not be visible
            to public users.
            """

        tags = [APISPEC.DEFAULT_TAG, 'internal']
        segments = ServiceInfo(
            service_name,
            CyMyService, # type: ignore
            sio_config,
            tags).docstring.extract_segments(
                CyMyService.__doc__ # type: ignore
            )

        # There should be only one tag, the default, implicit one called 'public'
        expected_public = {
             'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline\n',
             'summary':     'This is a one-line summary.'
        }

        expected_internal = {
             'tag':         'internal',
             'description': '\n\n\n.. raw:: html\n\n    <span class="zato-tag-name-highlight">@internal</span>\n\nOne-line summary for internal uses.\n\nThis part is internal,\nit will not be visible\nto public users.', # noqa: E501
             'full':        '\n\n.. raw:: html\n\n    <span class="zato-tag-name-highlight">@internal</span>\n\n\nINFORMATION IN THIS SECTION IS NOT PUBLIC.\n\nOne-line summary for internal uses.\n\nThis part is internal,\nit will not be visible\nto public users.\n', # noqa: E501
             'summary':     not_public
        }

        self.assertEqual(len(segments), 2)

        public = segments[0] # type: _DocstringSegment
        segment_dict_public = public.to_dict()

        self.assertEqual(segment_dict_public['tag'], expected_public['tag'])
        self.assertEqual(segment_dict_public['description'], expected_public['description'])
        self.assertEqual(segment_dict_public['full'], expected_public['full'])
        self.assertEqual(segment_dict_public['summary'], expected_public['summary'])

        internal = segments[1] # type: _DocstringSegment
        segment_dict_internal = internal.to_dict()

        self.assertEqual(segment_dict_internal['tag'], expected_internal['tag'])
        self.assertEqual(segment_dict_internal['description'], expected_internal['description'])

        self.assertEqual(segment_dict_internal['full'], expected_internal['full'])
        self.assertEqual(segment_dict_internal['summary'], expected_internal['summary'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
