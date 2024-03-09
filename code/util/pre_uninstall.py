# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class WindowsPreUninstall:
    """ Code to run before a Windows package is to be uninstalled.
    """
    def __init__(self, base_dir:'str', bin_dir:'str') -> 'None':
        self.base_dir = base_dir
        self.bin_dir = bin_dir

        # This is the path to the directory that 'zato.py' command is in
        self.zato_windows_bin_dir = os.path.join(self.base_dir, 'windows-bin')

        # Full path to 'zato.py'
        self.zato_windows_bin_path = os.path.join(self.zato_windows_bin_dir, 'zato.py')

        # We need for the drive letter to be upper-cased since this is what will be found in the registry
        drive_letter, rest = self.zato_windows_bin_dir[0], self.zato_windows_bin_dir[1:]
        drive_letter = drive_letter.upper()

        self.zato_windows_bin_dir = drive_letter + rest

# ################################################################################################################################

    def update_windows_registry(self):

        # stdlib
        from winreg import                           \
             HKEY_CURRENT_USER as hkey_current_user, \
             KEY_ALL_ACCESS    as key_all_access,    \
             REG_EXPAND_SZ     as reg_expand_sz,     \
             OpenKey,                                \
             QueryValueEx,                           \
             SetValueEx # noqa: E272

        # pywin32
        from win32con import                         \
             HWND_BROADCAST as hwnd_broadcast,       \
             WM_SETTINGCHANGE as wm_settingchange

        # pywin32 as well
        from win32gui import SendMessage

        # We look up environment variables for current user
        root = hkey_current_user
        sub_key = 'Environment'

        # Open the registry key ..
        with OpenKey(root, sub_key, 0, key_all_access) as reg_key_handle:

            # .. look up the current value of %path% ..
            env_path, _ = QueryValueEx(reg_key_handle, 'path')

            # .. make sure that our path is already there ..
            if self.zato_windows_bin_dir not in env_path:
                return

            # .. if we are here, it means that we can remove our path ..
            env_path = env_path.replace(self.zato_windows_bin_dir, '')

            # .. now, we can save the new value of %path% in the registry ..
            SetValueEx(reg_key_handle, 'path', 0, reg_expand_sz, env_path)

        # .. finally, we can notify the system of the change.
        SendMessage(hwnd_broadcast, wm_settingchange, 0, sub_key)

# ################################################################################################################################

    def run(self):
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

    pre_uninstall = WindowsPreUninstall(base_dir, bin_dir)
    pre_uninstall.run()

# ################################################################################################################################
# ################################################################################################################################
