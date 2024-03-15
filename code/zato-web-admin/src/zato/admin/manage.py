# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write('Error: Can not find the file 'settings.py' in the directory containing %r. It appears you have customized things.\nYou will have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it is causing an ImportError somehow.)\n' % __file__) # noqa
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
