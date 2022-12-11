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
from pathlib import Path
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

class PostInstall:
    """ Code to run after a Zato package has been just installed.
    """

    build_dir_to_base_depth: 'int'

    base_dir: 'str'
    bin_dir:  'str'

    # A directory where Python binaries are in, e.g. python3.11, python3.12 etc.
    python_dir: 'str'

    # The full path to the python_dir directory
    python_dir_full: 'str'

    # The directory that this installation was originally build in,
    # e.g. the one that was used on the build server.
    orig_build_dir: 'str'

    # Packages are installed here
    site_packages_dir: 'str'

    # This is the path to the directory that 'zato.bat' command is in
    zato_windows_bin_dir: 'str'

    # Full path to 'zato.bat'
    zato_windows_bin_path: 'str'

# ################################################################################################################################

    def init(self, base_dir:'str', bin_dir:'str') -> 'None':

        self.base_dir = base_dir
        self.bin_dir = bin_dir

        # Packages are installed here
        self.site_packages_dir = os.path.join(self.base_dir, *site_packages_relative)

        # This is the path to the directory that 'zato.bat' command is in
        # self.zato_windows_bin_dir = os.path.join(self.base_dir, 'windows-bin')

        # Full path to 'zato.py'
        # self.zato_windows_bin_path = os.path.join(self.zato_windows_bin_dir, 'zato.bat')

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

            if self.orig_build_dir in data:

                # Replace the build directory with the actual installation directory ..
                data = data.replace(self.orig_build_dir, self.base_dir)

                # .. and save the data on disk.
                # f = open(name, 'w')
                # _ = f.write(data)
                # f.close()

                print(333, name)

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
        # self.update_bin_files()
        # self.set_git_root_dir_config()

# ################################################################################################################################

    def update_registry(self) -> 'None':
        self.update_windows_registry()

# ################################################################################################################################

    def get_impl_base_dir(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def run_impl(self) -> 'None':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_orig_build_dir(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_python_dir(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_python_dir_full(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_site_packages_dir(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_base_dir(self) -> 'str':

        # Base directory may be given explicitly or we will need build it in relation to our own location
        if len(sys.argv) > 1:
            base_dir = sys.argv[1]
            return base_dir
        else:
            return self.get_impl_base_dir()

# ################################################################################################################################

    def run(self) -> 'None':

        # Prepare paths ..
        self.base_dir         = self.get_base_dir()
        self.orig_build_dir   = self.get_orig_build_dir()
        self.python_dir       = self.get_python_dir()
        self.python_dir_full  = self.get_python_dir_full()
        self.site_packages_dir = self.get_site_packages_dir()

        # .. and actually run the process.
        self.run_impl()

        """
        curdir = os.path.dirname(os.path.abspath(__file__))

        base_dir = os.path.join(curdir, '..')
        base_dir = os.path.abspath(base_dir)

        base_dir = base_dir.replace('\\', '\\\\')

        bin_dir = os.path.join(base_dir, 'Scripts')
        bin_dir = os.path.abspath(bin_dir)
        """

# ################################################################################################################################
# ################################################################################################################################

class WindowsPostInstall(PostInstall):
    pass

# ################################################################################################################################
# ################################################################################################################################

class NonWindowsPostInstall(PostInstall):

    build_dir_to_base_depth = 2

# ################################################################################################################################

    def run_impl(self) -> 'None':
        self.update_paths()

# ################################################################################################################################

    def get_impl_base_dir(self) -> 'str':
        curdir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.join(curdir, '..')
        base_dir = os.path.abspath(base_dir)
        return base_dir

# ################################################################################################################################

    def get_python_dir(self) -> 'any_':

        python_dir = 'default-python_dir'

        # This the directory where the Python directory will be found ..
        lib_dir = os.path.join(self.base_dir, 'lib')

        # .. list all the directories in the lib dir ..
        for item in sorted(os.listdir(lib_dir)):

            # .. accept the one that is a Python one ..
            if item.startswith('python'):
                python_dir = item
                break

        # .. and return the result to the caller.
        return python_dir

# ################################################################################################################################

    def get_python_dir_full(self) -> 'str':

        python_dir_full = os.path.join(self.base_dir, 'lib', self.python_dir)
        python_dir_full = os.path.abspath(python_dir_full)

        return python_dir_full

# ################################################################################################################################

    def get_site_packages_dir(self) -> 'str':

        site_packages_dir = os.path.join(self.python_dir_full, 'site-packages')
        return site_packages_dir

# ################################################################################################################################

    def get_orig_build_dir(self) -> 'str':

        # Full path to the zato command ..
        zato_bin_path = os.path.join(self.base_dir, 'bin', 'zato')

        # .. read the whole contents ..
        lines = open(zato_bin_path).readlines()

        # .. our path will be in the first line ..
        bin_line = lines[0]
        bin_line = bin_line.strip()
        bin_line = bin_line.replace('#!', '')

        #
        # .. Now, we have something like this in bin_line:
        # .. /home/user/projects/zatosource-zato/3.2/code/bin/python
        # .. and we would like to remove the trailing parts to have this:
        # .. /home/user/projects/zatosource-zato/3.2/code/
        #
        # .. How many parts to remove will depend on what operating system we are on
        # .. which is why it is our subclasses that tell it to us below.

        # Turn what we have so far into a Path object so it is easier to process it ..
        bin_path = Path(bin_line)

        # .. extract the original build directory now ..
        orig_build_dir = bin_path.parts[:-self.build_dir_to_base_depth]

        # .. turn it into a list ..
        orig_build_dir = os.sep.join(orig_build_dir)

        # .. and return it to our caller.
        return orig_build_dir

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    class_ = WindowsPostInstall if is_windows else NonWindowsPostInstall
    instance = class_()
    instance.run()

# ################################################################################################################################
# ################################################################################################################################
