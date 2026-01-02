# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

def get_sys_info():
    import platform

    system = platform.system()

    is_linux = 'linux' in system.lower()
    is_windows = 'windows' in system.lower()
    is_mac = 'darwin' in system.lower()

    if is_linux:

        try:
            import distro

            info = distro.info()
            codename = info['codename'].lower()
            codename = codename.replace('/', '')

            out = '{}.{}'.format(info['id'], info['version'])

            if codename:
                out += '-{}'.format(codename)
        except ImportError:
            out = 'linux'

    elif is_windows:
        _platform = platform.platform().lower()
        _edition = platform.win32_edition()
        out = '{}-{}'.format(_platform, _edition)

    elif is_mac:
        out = platform.platform().lower()
        return out

    else:
        out = 'os.unrecognised'

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_version():

    # stdlib
    import os
    import sys

    # Python 2/3 compatibility
    from zato.common.py23_.past.builtins import execfile

    # Default version if not set below
    version = '4.1'

    # Make sure the underlying git command runs in our git repository ..
    code_dir = os.path.dirname(sys.executable)
    os.chdir(code_dir)

    curdir = os.path.dirname(os.path.abspath(__file__))
    _version_py = os.path.normpath(os.path.join(curdir, '..', '..', '..', '..', '.version.py'))
    _locals = {}
    execfile(_version_py, _locals)
    version = 'Zato {}'.format(_locals['version'])

    return version

# ################################################################################################################################
# ################################################################################################################################
