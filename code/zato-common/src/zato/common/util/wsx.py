# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

def find_wsx_environ(service):
    wsx_environ = service.wsgi_environ.get('zato.request_ctx.async_msg', {}).get('environ')
    if not wsx_environ:
        raise Exception('Could not find `[\'zato.request_ctx.async_msg\'][\'environ\']` in WSGI environ `{}`'.format(
            service.wsgi_environ))
    else:
        return wsx_environ

# ################################################################################################################################
