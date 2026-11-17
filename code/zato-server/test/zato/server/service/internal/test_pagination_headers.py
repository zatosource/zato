# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase
from unittest.mock import MagicMock

# Zato
from zato.server.service.internal import AdminService, SearchTool

# ################################################################################################################################
# ################################################################################################################################

class TestAfterHandlePaginationHeaders(TestCase):

    def test_pagination_headers_set_when_search_tool_has_meta(self):
        """ Verify that after_handle() sets X-Zato-Page-* headers from _search_tool.output_meta.
        """
        service = AdminService.__new__(AdminService)
        service.server = MagicMock()
        service.server.is_admin_enabled_for_info = False
        service.response = MagicMock()
        service.response.headers = {}

        # .. simulate a search tool with populated meta ..
        service._search_tool = SearchTool()
        service._search_tool.output_meta = {'search': {
            'cur_page': 2,
            'page_size': 50,
            'num_pages': 5,
            'prev_page': 1,
            'next_page': 3,
            'has_prev_page': True,
            'has_next_page': True,
            'total': 237,
        }}

        service.after_handle()

        self.assertEqual(service.response.headers['X-Zato-Page-Current'], 2)
        self.assertEqual(service.response.headers['X-Zato-Page-Size'], 50)
        self.assertEqual(service.response.headers['X-Zato-Page-Total'], 5)
        self.assertEqual(service.response.headers['X-Zato-Page-Previous'], 1)
        self.assertEqual(service.response.headers['X-Zato-Page-Next'], 3)
        self.assertEqual(service.response.headers['X-Zato-Page-Has-Previous'], True)
        self.assertEqual(service.response.headers['X-Zato-Page-Has-Next'], True)
        self.assertEqual(service.response.headers['X-Zato-Result-Total'], 237)

    def test_no_headers_set_when_search_meta_empty(self):
        """ Verify that after_handle() does not set headers when search meta is empty.
        """
        service = AdminService.__new__(AdminService)
        service.server = MagicMock()
        service.server.is_admin_enabled_for_info = False
        service.response = MagicMock()
        service.response.headers = {}

        service._search_tool = SearchTool()
        service._search_tool.output_meta = {'search': {}}

        service.after_handle()

        self.assertEqual(service.response.headers, {})

    def test_no_headers_set_when_no_search_tool(self):
        """ Verify that after_handle() does nothing when there is no _search_tool.
        """
        service = AdminService.__new__(AdminService)
        service.server = MagicMock()
        service.server.is_admin_enabled_for_info = False
        service.response = MagicMock()
        service.response.headers = {}

        service.after_handle()

        self.assertEqual(service.response.headers, {})

# ################################################################################################################################
# ################################################################################################################################
