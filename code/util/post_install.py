# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

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

if 0:
    from typing import Any as any_

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

    #
    # 3.9
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.9\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.9\code',

    r'c:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.9\\code',
    r'C:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.9\\code',

    #
    # 3.10
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.10\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.10\code',

    r'c:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.10\\code',
    r'C:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.10\\code',

    #
    # 3.11
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.11\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.11\code',

    r'c:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.11\\code',
    r'C:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.11\\code',

    #
    # 3.12
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.12\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.12\code',

    r'c:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.12\\code',
    r'C:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.12\\code',

    #
    # 3.13
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.13\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.13\code',

    r'c:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.13\\code',
    r'C:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.13\\code',

    #
    # 3.14
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.14\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.14\code',

    r'c:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.14\\code',
    r'C:\\Users\\dsuch\\projects\\src-zato\\zato-3.2-python-3.14\\code',

    #
    # 3.15
    #

    r'c:\Users\dsuch\projects\src-zato\zato-3.2-python-3.15\code',
    r'C:\Users\dsuch\projects\src-zato\zato-3.2-python-3.15\code',

    r'c:\\Users\\dsuch\\projects\src-zato\\zato-3.2-python-3.15\\code',
    r'C:\\Users\\dsuch\\projects\src-zato\\zato-3.2-python-3.15\\code',

]

# ################################################################################################################################
# ################################################################################################################################

class WindowsPostInstall:
    """ Code to run after a Windows package has been just installed.
    """
    def __init__(self, base_dir:'str', bin_dir:'str') -> 'None':
        self.base_dir = base_dir
        self.bin_dir = bin_dir

        # Packages are installed here
        self.site_packages_dir = os.path.join(self.base_dir, *site_packages_relative)

        # This is the path to the directory that 'zato.py' command is in
        self.zato_windows_bin_dir = os.path.join(self.base_dir, 'windows-bin')

        # Full path to 'zato.py'
        self.zato_windows_bin_path = os.path.join(self.zato_windows_bin_dir, 'zato.py')

# ################################################################################################################################

    def update_files(self, files_dir:'any_', patterns:'any_', to_ignore:'any_') -> 'None':

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

                # .. if we enter this 'if' branch, it means that the file is not to be ignored.
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
                    _ = f.write(data)
                    f.close()

# ################################################################################################################################

    def update_site_packages_files(self) -> 'None':

        # File types that we are going to modify
        patterns = ['*.pth', '*.egg-link']

        # Patterns will be matched against this directory
        files_dir = self.site_packages_dir

        # In site-packages, there are no files to ignore except for backup ones
        to_ignore = ['-bak']

        # Actually updates the files now
        self.update_files(files_dir, patterns, to_ignore)

# ################################################################################################################################

    def update_bin_files(self) -> 'None':

        # In the 'bin' directory, we update all the files
        patterns = ['*']

        # Patterns will be matched against this directory
        files_dir = self.bin_dir

        # Ignore binary files in addition to the backup ones
        to_ignore = ['-bak', '.exe', 'python']

        # Actually updates the files now
        self.update_files(files_dir, patterns, to_ignore)

# ################################################################################################################################

    def copy_zato_binary(self) -> 'None':

        # This is the path that 'zato.py' was saved to by default
        zato_py_path = os.path.join(self.bin_dir, 'zato.py')

        # Copy the binary to its final destination
        shutil_copy(zato_py_path, self.zato_windows_bin_path)

# ################################################################################################################################

    def set_git_root_dir_config(self) -> 'None':

        git_root_dir = os.path.join(self.base_dir, '..')
        git_root_dir = os.path.abspath(git_root_dir)
        git_root_dir = git_root_dir.replace('\\', '/')

        try:
            command = f'git config --global --add safe.directory {git_root_dir}'
            _ = os.system(command)
        except Exception:
            # This system may not have git
            pass

# ################################################################################################################################

    def update_windows_registry(self) -> 'None':

        # stdlib
        from winreg import OpenKey         # type: ignore
        from winreg import QueryValueEx    # type: ignore
        from winreg import SetValueEx      # type: ignore

        from winreg import HKEY_CURRENT_USER as hkey_current_user # type: ignore
        from winreg import KEY_ALL_ACCESS    as key_all_access    # type: ignore
        from winreg import REG_EXPAND_SZ     as reg_expand_sz     # type: ignore

        # pywin32
        from win32con import HWND_BROADCAST as hwnd_broadcast     # type: ignore
        from win32con import WM_SETTINGCHANGE as wm_settingchange # type: ignore

        # pywin32 as well
        from win32gui import SendMessage # type: ignore

        # We look up environment variables for current user
        root = hkey_current_user
        sub_key = 'Environment'

        # Open the registry key ..
        with OpenKey(root, sub_key, 0, key_all_access) as reg_key_handle:

            # .. look up the current value of %path% ..
            env_path, _ = QueryValueEx(reg_key_handle, 'path')

            # .. make sure that new path is not already there ..
            if self.zato_windows_bin_dir in env_path:
                return

            # .. if we are here, it means that we add our path ..
            env_path += ';' + self.zato_windows_bin_dir

            # .. now, we can save the new value of %path% in the registry ..
            SetValueEx(reg_key_handle, 'path', 0, reg_expand_sz, env_path)

        # .. finally, we can notify the system of the change.
        SendMessage(hwnd_broadcast, wm_settingchange, 0, sub_key)

# ################################################################################################################################

    def update_paths(self) -> 'None':
        self.update_site_packages_files()
        self.update_bin_files()
        self.copy_zato_binary()
        self.set_git_root_dir_config()

# ################################################################################################################################

    def update_registry(self) -> 'None':
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

    command = sys.argv[1]

    util = WindowsPostInstall(base_dir, bin_dir)
    func = getattr(util, command)
    func()

# ################################################################################################################################
# ################################################################################################################################
