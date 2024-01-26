# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.util.cloud.google import get_api_list

# ################################################################################################################################
# ################################################################################################################################

class UtilCloudGoogleTestCase(TestCase):

    def test_get_api_list(self):

        # Get a list of all the APIs available ..
        api_list = get_api_list()

        # We do not know how many APIs we are going to receive as this is outside our control.
        # But we do know there will be hundreds of them.
        min_api_list_len = 200
        actual_api_list_len = len(api_list)

        # Make sure we have at least that many results
        self.assertGreater(actual_api_list_len, min_api_list_len)

        # Find a sample API description and confirm its contents.
        api_title = 'Drive API'
        api_version = 'v3'

        for item in api_list:
            if item.title == api_title and item.version == api_version:
                self.assertEqual(item.name, 'drive')
                self.assertEqual(item.id, 'drive:v3')
                break
        else:
            raise Exception(f'API description not found -> {api_title}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
