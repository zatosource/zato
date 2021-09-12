# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from glob import glob
from platform import system as platform_system
from shutil import copy as shutil_copy

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

is_windows = 'windows' in platform_system().lower()

# ################################################################################################################################
# ################################################################################################################################

#
# This path is relative to the parent of the path that the 'zato' command is in (self.base_dir).
#
site_packages_relative = ['lib', 'site-packages']

# ################################################################################################################################
# ################################################################################################################################

#
# This is where the source code is built under Windows and this is what we are replacing during the installation
# with a final path that the package has been installed to, e.g. C:\Users\Jane\LocalAppData\ZatoSource\Zato\Zato-3.2-python38
#
build_dir_list = [
    r'c:\Users\Administrator\Desktop\projects\zato\code',
    r'C:\\Users\\Administrator\\Desktop\\projects\\zato\\code'
]

# ################################################################################################################################
# ################################################################################################################################

class WindowsPostInstall:
    """ Code to run after a Windows package has been just installed.
    """
    def __init__(self, base_dir, bin_dir):
        # type: (str) -> None
        self.base_dir = base_dir
        self.bin_dir = bin_dir

        self.site_packages_dir = os.path.join(self.base_dir, *site_packages_relative)

# ################################################################################################################################

    def update_files(self, files_dir, patterns, to_ignore):
        # type: (list, list, list) -> None

        # To be sorted later
        file_names = []

        # Check all input patterns ..
        for name in patterns:

            # .. full pattern for glob, including the directory with files ..
            full_pattern = os.path.join(files_dir, name)

            # .. consult all the file names in the directory ..
            for full_path in glob(full_pattern): # type: str

                # .. ignore sub-directories ..
                if os.path.isdir(full_path):
                    continue

                # .. confirm if the file name is not among ignored ones ..
                for ignored in to_ignore:
                    file_name = os.path.basename(full_path)
                    if file_name.startswith(ignored) or file_name.endswith(ignored):
                        should_add = False
                        break
                else:
                    should_add = True

                # .. if we enter this if, it means that the file is not to be ignored.
                if should_add:
                    file_names.append(full_path)

        # To make it easier to recognise what we are working with currently
        file_names.sort()

        for name in file_names:

            # Prepare a backup file's name ..
            backup_name = name + '-bak'

            # .. and make the backup before modifying the file.
            shutil_copy(name, backup_name)

            # Now, we can get the contents of the original file
            data = open(name, 'r').read() # type: str

            # Work only with files that actually need to be updated
            for build_dir in build_dir_list:

                if build_dir in data:

                    # Replace the build directory with the actual installation directory ..
                    data = data.replace(build_dir, self.base_dir)

                # .. and save the data on disk.
                f = open(name, 'w')
                f.write(data)
                f.close()

# ################################################################################################################################

    def update_site_packages_files(self):

        # File types that we are going to modify
        patterns = ['*.pth', '*.egg-link']

        # Patterns will be matched against this directory
        files_dir = self.site_packages_dir

        # In site-packages, there are no files to ignore except for backup ones
        to_ignore = ['-bak']

        # Actually updates the files now
        self.update_files(files_dir, patterns, to_ignore)

# ################################################################################################################################

    def update_bin_files(self):

        # In the 'bin' directory, we update all the files
        patterns = ['*']

        # Patterns will be matched against this directory
        files_dir = self.bin_dir

        # Ignore binary files in addition to the backup ones
        to_ignore = ['-bak', '.exe', 'python']

        # Actually updates the files now
        self.update_files(files_dir, patterns, to_ignore)

# ################################################################################################################################

    def update_windows_registry(self):
        pass

# ################################################################################################################################

    def run(self):
        self.update_site_packages_files()
        self.update_bin_files()
        self.update_windows_registry()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    curdir = os.path.dirname(os.path.abspath(__file__))

    base_dir = os.path.join(curdir, '..')
    base_dir = os.path.abspath(base_dir)

    base_dir = base_dir.replace('\\', '\\\\')

    bin_dir = os.path.join(base_dir, 'Scripts')
    bin_dir = os.path.abspath(bin_dir)

    post_install = WindowsPostInstall(base_dir, bin_dir)
    post_install.run()

# ################################################################################################################################
# ################################################################################################################################
