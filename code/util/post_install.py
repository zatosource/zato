# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# sh
import sh

# ################################################################################################################################
# ################################################################################################################################

class PostInstallProcess:
    """ Tasks run after the main installation process.
    """
    def __init__(self, base_dir):
        # type: (str) -> None
        self.base_dir = base_dir

# ################################################################################################################################

    def update_git_revision(self):

        # This is where we will store our git commit ID
        revision_file_path = os.path.join(self.base_dir, 'release-info', 'revision.txt')

        out = sh.git('--version')

        print()
        print(111, out)
        print()

# ################################################################################################################################

    def run(self):
        self.update_git_revision()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    sys_exec_dir = os.path.dirname(sys.executable)

    base_dir = os.path.join(sys_exec_dir, '..')
    base_dir = os.path.abspath(base_dir)

    process = PostInstallProcess(base_dir)
    process.run()

# ################################################################################################################################
# ################################################################################################################################
