# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from platform import system as platform_system

is_linux = platform_system().lower() == 'linux'
is_other_than_linux = not is_linux

# For pyflakes
is_linux = is_linux
is_other_than_linux = is_other_than_linux
