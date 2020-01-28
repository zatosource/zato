# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import bunchify

# ################################################################################################################################
# ################################################################################################################################

class Response(object):
    def __init__(self, data):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data

# ################################################################################################################################
# ################################################################################################################################

class RequestsAdapter(object):

    def __init__(self):
        self._get_handlers = {}
        self._post_handlers = {}

# ################################################################################################################################

    def get(self, path, *args, **kwargs):
        data = self._get_handlers[path](path, args=args, kwargs=bunchify(kwargs))
        return Response(data)

# ################################################################################################################################

    def post(self, path, *args, **kwargs):
        data = self._post_handlers[path](path, args=args, kwargs=bunchify(kwargs))
        return Response(data)

# ################################################################################################################################

    def add_get_handler(self, path, func):
        self._get_handlers[path] = func

# ################################################################################################################################

    def add_post_handler(self, path, func):
        self._post_handlers[path] = func

# ################################################################################################################################
# ################################################################################################################################
