# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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
        import distro
        info = distro.info()
        out = '{}.{}-{}'.format(info['id'], info['version'], info['codename'].lower())

    elif is_windows:
        _platform = platform.platform().lower()
        _edition = platform.win32_edition()
        out = '{}-{}'.format(_platform, _edition)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_version():

    # stdlib
    import os
    from sys import version_info as py_version_info

    # Python 2/3 compatibility
    from past.builtins import execfile

    try:
        curdir = os.path.dirname(os.path.abspath(__file__))
        _version_py = os.path.normpath(os.path.join(curdir, '..', '..', '..', '..', '.version.py'))
        _locals = {}
        execfile(_version_py, _locals)
        version = 'Zato {}'.format(_locals['version'])
    except IOError:
        version = '3.2'
    finally:
        sys_info = get_sys_info()
        version = '{}-py{}.{}.{}-{}'.format(
            version,
            py_version_info.major,
            py_version_info.minor,
            py_version_info.micro,
            sys_info)

    return version

# ################################################################################################################################
# ################################################################################################################################
