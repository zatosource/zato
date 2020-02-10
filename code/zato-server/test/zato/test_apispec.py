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
#from zato.server.service import Service

# ################################################################################################################################

service_name = 'my.service'
sio_config = None

# ################################################################################################################################
# ################################################################################################################################

class APISpecTestCase(TestCase):

# ################################################################################################################################

    def test_docstring_no_tags(self):

        return

        class MyService:
            """ This is a one-line summary.

            This is public information
            It is multiline
            """

        info = ServiceInfo(service_name, MyService, sio_config)

        self.assertEquals(info.docstring.summary, 'This is a one-line summary')
        self.assertEquals(info.docstring.full, 'This is a one-line summary.\n\nThis is public information\nIt is multiline')

# ################################################################################################################################

    def test_extract_tags_public_only_implicit(self):

        class MyService:
            """ This is a one-line summary.

            This is public information
            It is multiline
            """

        tags = ServiceInfo(service_name, MyService, sio_config).extract_tags()

        # There should be only one tag, the default, implicit one called 'public'
        expected = {'public':
            {'tag':         'public',
             'description': 'This is public information\nIt is multiline',
             'full':        'This is a one-line summary.\n\nThis is public information\nIt is multiline',
             'summary':     'This is a one-line summary.'
        }}

        #self.assertDictEqual(tags, expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
