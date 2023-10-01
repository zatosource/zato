# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.common.api import HotDeploy
from zato.common.typing_ import cast_
from zato.common.util.hot_deploy_ import extract_pickup_from_items

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hot_deploy_ import HotDeployProject

# ################################################################################################################################
# ################################################################################################################################

class HotDeployTestCase(TestCase):

    def test_extract_pickup_from_items(self):

        # Skip this test if we do not have an environment variable
        # pointing to a directory with a test project.
        if not (root_dir := os.environ.get('Zato_Test_Hot_Deploy_Project_Root')): # type: ignore
            return

        # We expect for the source to be kept in this directory

        # Prepare test data ..
        base_dir = '/my-base-dir'

        name0  = f'{HotDeploy.UserPrefix}.name.1'
        value0 = 'relative/path'

        name1  = f'{HotDeploy.UserPrefix}.name.2'
        value1 = '/absolute/path'

        name2 = f'{HotDeploy.UserPrefix}.project.1'
        value2 = root_dir

        # .. build a dictionary for the extracting function to process ..
        pickup_config = {
            name0: {'pickup_from': value0},
            name1: {'pickup_from': value1},
            name2: {'pickup_from': value2},
        }

        # .. expected test data on output ..
        project0_src_dir = os.path.join(root_dir, 'project0', 'subdir0', 'src')
        project1_src_dir = os.path.join(root_dir, 'project1', 'subdir1', 'src')

        for idx, item in enumerate(extract_pickup_from_items(base_dir, pickup_config, HotDeploy.Source_Directory)):

            # This was a relative path that should have been turned into an absolute one ..
            if idx == 0:
                expected = os.path.join(base_dir, value0)
                self.assertEqual(item, expected)

            # .. this was an absolute path so we should have been given the same value back ..
            elif idx == 1:
                expected = value1
                self.assertEqual(item, expected)

            elif idx == 2:

                # .. there should be two projects on output ..
                self.assertEqual(len(item), 2)

                # .. do extract them ..
                project0 = cast_('HotDeployProject', item[0])
                project1 = cast_('HotDeployProject', item[1])

                # .. and run the assertions now ..

                self.assertEqual(str(project0.sys_path_entry), project0_src_dir)
                self.assertEqual(str(project1.sys_path_entry), project1_src_dir)

            else:
                raise Exception(f'Unexpected idx -> {idx} and item -> {item} ')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
