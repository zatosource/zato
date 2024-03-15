# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.common.api import HotDeploy
from zato.common.typing_ import cast_
from zato.common.util.hot_deploy_ import extract_pickup_from_items, get_project_info

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hot_deploy_ import HotDeployProject
    HotDeployProject = HotDeployProject

# ################################################################################################################################
# ################################################################################################################################

class HotDeployTestCase(TestCase):

    def xtest_extract_pickup_from_items(self):

        # Skip this test if we do not have an environment variable
        # pointing to a directory with a test project.
        if not (root_dir := os.environ.get('Zato_Test_Hot_Deploy_Project_Root_1')): # type: ignore
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

    def test_get_project_info(self):

        # Skip this test if we do not have an environment variable
        # pointing to a directory with a test project.
        if not (root_dir := os.environ.get('Zato_Test_Hot_Deploy_Project_Root_2')): # type: ignore
            return

        # Local aliases
        src_dir = HotDeploy.Source_Directory
        project_name = 'project2'
        full_src_dir = os.path.join(root_dir, project_name, src_dir)

        # Prepare test data
        expected_sys_path_entry = full_src_dir

        # We expect for this information to have been built
        if not (project_info := get_project_info(root_dir, src_dir)):
            raise Exception('Expect for project information to be returned')

        # There should be one project on output
        self.assertEqual(len(project_info), 1)

        # Extract the project we have been given ..
        project_info = project_info[0]

        # .. run assertions ..
        self.assertEqual(str(project_info.sys_path_entry), expected_sys_path_entry)

        for item in project_info.pickup_from_path:
            print(111, item)

        # .. there should be 13 paths extracted ..
        self.assertEqual(len(project_info.pickup_from_path), 13)

        # .. create local variables for the ease of testing ..
        full_esb_dir = os.path.join(full_src_dir, 'corp', 'esb')

        #

        esb_common           = str(project_info.pickup_from_path[0])
        esb_model_common     = str(project_info.pickup_from_path[1])
        esb_adapter_common   = str(project_info.pickup_from_path[2])

        esb_core_common      = str(project_info.pickup_from_path[3])
        esb_util             = str(project_info.pickup_from_path[4])
        esb_core_util        = str(project_info.pickup_from_path[5])

        esb_channel_edu_util = str(project_info.pickup_from_path[6])
        esb_model            = str(project_info.pickup_from_path[7])
        esb_model_hr         = str(project_info.pickup_from_path[8])

        esb_core             = str(project_info.pickup_from_path[9])
        esb_channel          = str(project_info.pickup_from_path[10])
        esb_channel_edu      = str(project_info.pickup_from_path[11])
        esb_adapter          = str(project_info.pickup_from_path[12])

        #

        expected_esb_common           = os.path.join(full_esb_dir, 'common')
        expected_esb_model_common     = os.path.join(full_esb_dir, 'model', 'common')
        expected_esb_adapter_common   = os.path.join(full_esb_dir, 'adapter', 'common')

        expected_esb_core_common      = os.path.join(full_esb_dir, 'core', 'common')
        expected_esb_util             = os.path.join(full_esb_dir, 'util')
        expected_esb_core_util        = os.path.join(full_esb_dir, 'core', 'util')

        expected_esb_channel_edu_util = os.path.join(full_esb_dir, 'channel', 'edu', 'util')
        expected_esb_model            = os.path.join(full_esb_dir, 'model')
        expected_esb_model_hr         = os.path.join(full_esb_dir, 'model', 'hr')

        expected_esb_core             = os.path.join(full_esb_dir, 'core')
        expected_esb_channel          = os.path.join(full_esb_dir, 'channel')
        expected_esb_channel_edu      = os.path.join(full_esb_dir, 'channel', 'edu')
        expected_esb_adapter          = os.path.join(full_esb_dir, 'adapter')

        #

        self.assertEqual(esb_common,           expected_esb_common)
        self.assertEqual(esb_model_common,     expected_esb_model_common)
        self.assertEqual(esb_adapter_common,   expected_esb_adapter_common)

        self.assertEqual(esb_core_common,      expected_esb_core_common)
        self.assertEqual(esb_util,             expected_esb_util)
        self.assertEqual(esb_core_util,        expected_esb_core_util)

        self.assertEqual(esb_channel_edu_util, expected_esb_channel_edu_util)
        self.assertEqual(esb_model,            expected_esb_model)
        self.assertEqual(esb_model_hr,         expected_esb_model_hr)

        self.assertEqual(esb_core,             expected_esb_core)
        self.assertEqual(esb_channel,          expected_esb_channel)
        self.assertEqual(esb_channel_edu,      expected_esb_channel_edu)
        self.assertEqual(esb_adapter,          expected_esb_adapter)

        #

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
