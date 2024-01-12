# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
from glob import glob
from pathlib import Path
from platform import system as platform_system
from shutil import copy as shutil_copy
from typing import Any as any_, cast as cast_

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Long_File_Pattern         = r'\\?\%s'
    Long_File_Prefix          = '\\\\?\\'
    Long_File_Prefix_Escaped  = r'\\\?\\'

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
    code_dir: 'str'
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

    lib_dir_elems         = None # type: any_
    bin_path_prefix_elems = None # type: any_
    bin_path_needs_python_dir = None # type: any_

    zato_bin_line:    'int | None' = None
    zato_bin_command: 'str | None' = None

# ################################################################################################################################

    def init(self, base_dir:'str', bin_dir:'str') -> 'None':

        self.base_dir = base_dir
        self.bin_dir = bin_dir

        # Packages are installed here
        self.site_packages_dir = os.path.join(self.code_dir, *site_packages_relative)

# ################################################################################################################################

    def update_files(self, files_dir:'any_', patterns:'any_', to_ignore:'any_') -> 'None':

        # Support long paths under Windows
        if is_windows:
            files_dir = ModuleCtx.Long_File_Pattern % files_dir

        # To be sorted later
        file_names = []

        # Check all input patterns ..
        for name in patterns:

            # .. full pattern for glob, including the directory with files ..
            full_pattern = os.path.join(files_dir, name)

            # .. consult all the file names in the directory ..
            for full_path in glob(full_pattern):

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

        for idx, name in enumerate(file_names, 1):

            # Prepare a backup file's name ..
            backup_name = name + '-bak'

            # .. and make the backup before modifying the file.
            shutil_copy(name, backup_name)

            # Now, we can get the contents of the original file
            data = open(name, 'r', encoding='utf8').read() # type: str

            if self.orig_build_dir in data:

                # Log what we are about to do
                logger.info('#%s Replacing `%s` in %s', idx, self.orig_build_dir, name)

                # Replace the build directory with the actual installation directory ..
                data = data.replace(self.orig_build_dir, self.code_dir)

                # .. and save the data on disk.
                f = open(name, 'w')
                _ = f.write(data)
                f.close()

                logger.info('#%s Finished replacing', idx)

# ################################################################################################################################

    def update_site_packages_files(self) -> 'None':

        # File types that we are going to modify
        patterns = ['*.pth', '*.egg-link']

        # Patterns will be matched against this directory
        files_dir = self.site_packages_dir

        # In site-packages, there are no files to ignore except for backup ones
        to_ignore = ['-bak']

        logger.info('Updating site-packages: %s -> %s -> %s', files_dir, patterns, to_ignore)

        # Actually updates the files now
        self.update_files(files_dir, patterns, to_ignore)

# ################################################################################################################################

    def update_bin_files(self) -> 'None':

        # In the 'bin' directory, we update all the files
        patterns = ['*']

        # Patterns will be matched against this directory
        files_dir = self.bin_dir

        # Ignore binary files in addition to the backup ones
        to_ignore = ['python', '-bak', '.dll', '.exe', '.pyd', '.zip']

        logger.info('Updating bin: %s -> %s -> %s', files_dir, patterns, to_ignore)

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
        with OpenKey(root, sub_key, 0, key_all_access) as reg_key_handle: # type: ignore

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
        _ = SendMessage(hwnd_broadcast, wm_settingchange, 0, cast_('any_', sub_key))

# ################################################################################################################################

    def update_paths(self) -> 'None':
        self.update_site_packages_files()
        self.update_bin_files()
        self.set_git_root_dir_config()

# ################################################################################################################################

    def update_registry(self) -> 'None':
        self.update_windows_registry()

# ################################################################################################################################

    def get_python_dir(self) -> 'any_':

        python_dir = 'default-python_dir'

        # This the directory where the Python directory will be found ..
        lib_dir = os.path.join(self.base_dir, *self.lib_dir_elems)

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

        python_dir_full = os.path.join(self.base_dir, *self.lib_dir_elems, self.python_dir)
        python_dir_full = os.path.abspath(python_dir_full)

        return python_dir_full

# ################################################################################################################################

    def get_orig_build_dir(self) -> 'str':

        # Build a full path to the zato command ..
        zato_bin_path = [self.base_dir]
        zato_bin_path.extend(self.bin_path_prefix_elems)

        if self.bin_path_needs_python_dir:
            zato_bin_path.append(self.python_dir)

        zato_bin_path.append(self.zato_bin_command) # type: ignore
        zato_bin_path = os.sep.join(zato_bin_path)

        if is_windows:
            zato_bin_path = ModuleCtx.Long_File_Pattern % zato_bin_path

        # .. read the whole contents ..
        lines = open(zato_bin_path).readlines()

        # .. our path will be in the first line ..
        bin_line = lines[self.zato_bin_line] # type: ignore
        bin_line = bin_line.strip()

        bin_path = self.extract_bin_path_from_bin_line(bin_line)

        #
        # .. Now, we have something like this in bin_line:
        # .. /home/user/projects/zatosource-zato/3.2/code/bin/python
        # .. and we would like to remove the trailing parts to have this:
        # .. /home/user/projects/zatosource-zato/3.2/code/
        #
        # .. How many parts to remove will depend on what operating system we are on
        # .. which is why it is our subclasses that tell it to us below.

        # Turn what we have so far into a Path object so it is easier to process it ..
        bin_path = Path(bin_path)

        # .. extract the original build directory now ..
        orig_build_dir = bin_path.parts[:-self.build_dir_to_base_depth]

        # Turn what we have so far into a list ..
        orig_build_dir = list(orig_build_dir)

        # If we are not on Windows, we need to remove the leading slash character
        # because we are going to use os.sep to join all the remaining parts.
        if not is_windows:
            try:
                orig_build_dir.remove('/')
            except ValueError:
                pass

        # Prepend a slahs character, unless we are on Windows
        prefix = '' if is_windows else '/'

        # .. turn it into a list ..
        orig_build_dir = prefix + os.sep.join(orig_build_dir)

        # Correct the path separator on Windows
        if is_windows:
            orig_build_dir = orig_build_dir.replace('\\\\', '\\')

        # .. and return it to our caller.
        return orig_build_dir

# ################################################################################################################################

    def get_site_packages_dir(self) -> 'str':

        site_packages_dir = os.path.join(self.python_dir_full, 'site-packages')
        return site_packages_dir

# ################################################################################################################################

    def get_impl_base_dir(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def run_impl(self) -> 'None':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_bin_dir(self) -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def extract_bin_path_from_bin_line(self, bin_line:'str') -> 'str':
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_base_dir(self) -> 'str':

        # Base directory may be given explicitly or we will need build it in relation to our own location
        if len(sys.argv) > 1:
            base_dir = sys.argv[1]
            if base_dir.endswith('\\'):
                base_dir = base_dir[:-1]
        else:
            base_dir = self.get_impl_base_dir()

        return base_dir

# ################################################################################################################################

    def run(self) -> 'None':

        # Prepare paths ..
        self.base_dir        = self.get_base_dir()
        self.code_dir        = os.path.join(self.base_dir, 'code')
        self.python_dir      = self.get_python_dir()
        self.python_dir_full = self.get_python_dir_full()
        self.orig_build_dir  = self.get_orig_build_dir()

        """
        print()
        print(111, self.base_dir)
        print()

        print()
        print(222, self.python_dir)
        print()

        print()
        print(333, self.python_dir_full)
        print()

        print()
        print(444, self.orig_build_dir)
        print()
        """

        # .. if these are the same, it means that we do not have anything to do.
        if self.base_dir == self.orig_build_dir:
            logger.info('Returning as base_dir and orig_build_dir are the same (%s)', self.base_dir)
            return
        else:

            # .. prepare the rest of the configuration ..

            self.bin_dir           = self.get_bin_dir()
            self.site_packages_dir = self.get_site_packages_dir()

            # .. and actually run the process.
            self.run_impl()

# ################################################################################################################################
# ################################################################################################################################

class WindowsPostInstall(PostInstall):
    lib_dir_elems         = ['code', 'bundle-ext', 'python-windows']
    bin_path_prefix_elems = ['code', 'bundle-ext', 'python-windows']
    bin_path_needs_python_dir = True
    zato_bin_line    = 1
    zato_bin_command = 'zato.bat'
    build_dir_to_base_depth = 4

# ################################################################################################################################

    def run_impl(self) -> 'None':
        self.update_paths()

# ################################################################################################################################

    def get_bin_dir(self) -> 'str':
        return self.python_dir_full

# ################################################################################################################################

    def extract_bin_path_from_bin_line(self, bin_line:'str') -> 'str':

        bin_line = bin_line.split() # type: ignore
        bin_path = bin_line[0]
        bin_path = bin_path.replace('"', '')

        return bin_path

# ################################################################################################################################
# ################################################################################################################################

class NonWindowsPostInstall(PostInstall):
    lib_dir_elems = ['code', 'lib']
    bin_path_prefix_elems = ['code', 'bin']
    bin_path_needs_python_dir = False
    zato_bin_line    = 0
    zato_bin_command = 'zato'
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

    def get_bin_dir(self) -> 'str':

        bin_dir = os.path.join(self.code_dir, 'bin')
        bin_dir = os.path.abspath(bin_dir)

        return bin_dir

# ################################################################################################################################

    def extract_bin_path_from_bin_line(self, bin_line:'str') -> 'str':
        bin_path = bin_line.replace('#!', '')
        return bin_path

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    class_ = WindowsPostInstall if is_windows else NonWindowsPostInstall
    instance = class_()
    instance.run()

# ################################################################################################################################
# ################################################################################################################################
