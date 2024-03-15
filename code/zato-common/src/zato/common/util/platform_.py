# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from platform import platform as platform_platform, system as platform_system

system_result = platform_system().lower()
platform_result = platform_platform().lower()

is_mac     = 'mac' in platform_result
is_linux   = 'linux' in system_result
is_windows = 'windows' in system_result

is_non_mac     = not is_mac
is_non_linux   = not is_linux
is_non_windows = not is_windows

non_mac     = is_non_mac
non_linux   = is_non_linux
non_windows = is_non_windows

# For pyflakes
is_mac     = is_mac
is_linux   = is_linux
is_windows = is_windows

is_non_mac     = is_non_mac
is_non_linux   = is_non_linux
is_non_windows = is_non_windows

non_mac     = non_mac
non_linux   = non_linux
non_windows = non_windows

is_posix = is_non_windows
