# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common.util import api as util_api, StaticConfig
from zato.common.util.search import SearchResults

# ################################################################################################################################
# ################################################################################################################################

class UtilsTestCase(TestCase):
    def test_uncamelify(self):
        original = 'HelloHowAreYouGOOD'
        expected1 = 'hello-how-are-you-good'
        self.assertEqual(util_api.uncamelify(original), expected1)

# ################################################################################################################################
# ################################################################################################################################

class TestAPIKeyUsername(TestCase):
    def test_update_apikey_username(self):
        config = Bunch(header='x-aaa')
        util_api.update_apikey_username_to_channel(config)
        self.assertEqual(config.header, 'HTTP_X_AAA')

# ################################################################################################################################
# ################################################################################################################################

class StaticConfigTestCase(TestCase):

    def test_read_file_no_directories(self):

        with TemporaryDirectory() as base_dir:

            file_dir = os.path.join(base_dir)
            file_name = 'foo.txt'
            file_path = os.path.join(file_dir, file_name)

            contents = 'This is a test.'
            _ = Path(file_path).write_text(contents)

            static_config = StaticConfig(base_dir)
            static_config.read_file(file_path, file_name)

            value = static_config[file_name]
            self.assertEqual(value, contents)

# ################################################################################################################################

    def test_read_file_with_one_directory(self):

        with TemporaryDirectory() as base_dir:

            level1 = 'abc'

            file_dir = os.path.join(base_dir, level1)
            file_name = 'foo.txt'
            file_path = os.path.join(file_dir, file_name)

            contents = 'This is a test.'

            Path(file_dir).mkdir(parents=True)
            _ = Path(file_path).write_text(contents)

            static_config = StaticConfig(base_dir)
            static_config.read_file(file_path, file_name)

            value = static_config[level1][file_name]
            self.assertEqual(value, contents)

# ################################################################################################################################

    def test_read_file_with_nested_directory(self):

        with TemporaryDirectory() as base_dir:

            level1 = 'abc'
            level2 = 'zxc'
            level3 = 'qwe'

            file_dir = os.path.join(base_dir, *[level1, level2, level3])
            file_name = 'foo.txt'
            file_path = os.path.join(file_dir, file_name)

            contents = 'This is a test.'

            Path(file_dir).mkdir(parents=True)
            _ = Path(file_path).write_text(contents)

            static_config = StaticConfig(base_dir)
            static_config.read_file(file_path, file_name)

            value = static_config[level1][level2][level3][file_name]
            self.assertEqual(value, contents)

# ################################################################################################################################
# ################################################################################################################################

class SearchResultsTestCase(TestCase):
    def test_from_list(self):

        data_list = [

            # Page 1
            'item1',
            'item2',
            'item3',

            # Page 2
            'item4',
            'item5',
            'item6',

            # Page 3
            'item7',
            'item8',
            'item9',

            # Page 3
            'item10',
            'item11',
            'item12',
        ]

        # Which page are we on in this result object
        cur_page = 2

        # How many results to return in each page
        page_size = 3

        search_results = SearchResults.from_list(data_list, cur_page, page_size, needs_sort=False)
        search_results = search_results.to_dict()

        self.assertIsInstance(search_results, dict)

        self.assertEqual(search_results['num_pages'], 4)
        self.assertEqual(search_results['cur_page'], 2)
        self.assertEqual(search_results['prev_page'], 1)
        self.assertEqual(search_results['next_page'], 3)
        self.assertEqual(search_results['page_size'], 3)
        self.assertEqual(search_results['total'], 12)

        self.assertTrue(search_results['has_prev_page'])
        self.assertTrue(search_results['has_next_page'])

        self.assertListEqual(
            search_results['result'],
            ['item9', 'item8', 'item7']
        )


# ################################################################################################################################
# ################################################################################################################################
