# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from platform import system as platform_system

platform_result = platform_system().lower()

is_linux   = 'linux' in platform_result
is_windows = 'windows' in platform_result

is_non_linux   = not is_linux
is_non_windows = not is_windows

non_linux   = is_non_linux
non_windows = is_non_windows

# For pyflakes
is_linux   = is_linux
is_windows = is_windows

is_non_linux   = is_non_linux
is_non_windows = is_non_windows

non_linux   = non_linux
non_windows = non_windows

is_posix = is_non_windows
